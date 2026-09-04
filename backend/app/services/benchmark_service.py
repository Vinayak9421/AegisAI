"""Benchmark service implementing source management, test case ingestion, content hashing, and stratified sampling."""

from collections import defaultdict
import datetime
import hashlib
import random
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, NotFoundError, ValidationError
from app.core.logging import logger
from app.db.models.benchmark import BenchmarkSource, TestCase
from app.domain.enums import (
    BenchmarkSourceStatus,
    BenchmarkSourceType,
    JobMode,
    ReviewStatus,
    SeverityLevel,
    TestCaseMode,
)
from app.schemas.benchmarks import (
    BenchmarkSourceResponse,
    BenchmarkSourceSummaryResponse,
    CreateBenchmarkSourceRequest,
    CreateTestCaseRequest,
    IngestBatchResponse,
    SampledTestCasesResponse,
    TestCaseResponse,
)
from app.schemas.common import Page
from app.services.base import BaseService


def compute_content_hash(category: str, subcategory: str, prompt_template: str) -> str:
    """Compute deterministic SHA-256 content hash for an attack test case."""
    normalized_content = f"{category.strip()}:{subcategory.strip()}:{prompt_template.strip()}"
    return hashlib.sha256(normalized_content.encode("utf-8")).hexdigest()


def compute_manifest_hash(hashes: List[str]) -> str:
    """Compute deterministic manifest hash across all sorted test case hashes in a source."""
    if not hashes:
        return hashlib.sha256(b"empty_manifest").hexdigest()
    sorted_hashes = sorted(hashes)
    concatenated = "".join(sorted_hashes)
    return hashlib.sha256(concatenated.encode("utf-8")).hexdigest()


class BenchmarkService(BaseService):
    """Encapsulates operations for benchmark sources, attack catalogs, and evaluation sampling."""

    def create_source(
        self,
        tenant_id: Optional[uuid.UUID],
        request: CreateBenchmarkSourceRequest,
    ) -> BenchmarkSource:
        """Register a new immutable benchmark source manifest."""
        # 1. Check uniqueness of (source_type, revision)
        if request.revision:
            stmt = select(BenchmarkSource).where(
                BenchmarkSource.source_type == request.source_type,
                BenchmarkSource.revision == request.revision,
            )
            if self.db.scalars(stmt).first():
                raise ConflictError(
                    f"Benchmark source of type '{request.source_type}' with revision '{request.revision}' already exists"
                )

        initial_manifest = hashlib.sha256(f"{request.name}:{request.revision}:{datetime.datetime.now(datetime.timezone.utc).isoformat()}".encode("utf-8")).hexdigest()
        source = BenchmarkSource(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            name=request.name,
            source_type=request.source_type,
            external_ref=request.external_ref,
            revision=request.revision,
            license_text=request.license_text,
            manifest_hash=initial_manifest,
            status=BenchmarkSourceStatus.APPROVED,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        logger.info(f"Registered benchmark source '{source.name}' (revision: {source.revision})")
        return source

    def get_source(self, source_id: uuid.UUID) -> BenchmarkSource:
        """Retrieve benchmark source by UUID."""
        source = self.db.get(BenchmarkSource, source_id)
        if not source:
            raise NotFoundError(f"Benchmark source '{source_id}' not found")
        return source

    def get_source_summary(self, source_id: uuid.UUID) -> BenchmarkSourceSummaryResponse:
        """Retrieve source details with aggregated test case statistics and category breakdown."""
        source = self.get_source(source_id)

        # Count total cases
        stmt_total = select(func.count(TestCase.id)).where(TestCase.source_id == source_id)
        total_cases = self.db.scalar(stmt_total) or 0

        # Group by category
        stmt_cat = (
            select(TestCase.category, func.count(TestCase.id))
            .where(TestCase.source_id == source_id)
            .group_by(TestCase.category)
        )
        categories = {cat: count for cat, count in self.db.execute(stmt_cat).all()}

        # Group by severity
        stmt_sev = (
            select(TestCase.severity_ceiling, func.count(TestCase.id))
            .where(TestCase.source_id == source_id)
            .group_by(TestCase.severity_ceiling)
        )
        severities = {str(sev.value if hasattr(sev, "value") else sev): count for sev, count in self.db.execute(stmt_sev).all()}

        return BenchmarkSourceSummaryResponse(
            source=BenchmarkSourceResponse.model_validate(source, from_attributes=True),
            total_test_cases=total_cases,
            categories=categories,
            severities=severities,
        )

    def list_sources(
        self,
        source_type: Optional[BenchmarkSourceType] = None,
        status: Optional[BenchmarkSourceStatus] = None,
    ) -> List[BenchmarkSourceSummaryResponse]:
        """List all benchmark sources matching filters with summary statistics."""
        stmt = select(BenchmarkSource.id)
        if source_type:
            stmt = stmt.where(BenchmarkSource.source_type == source_type)
        if status:
            stmt = stmt.where(BenchmarkSource.status == status)
        stmt = stmt.order_by(BenchmarkSource.created_at.desc())

        source_ids = list(self.db.scalars(stmt).all())
        return [self.get_source_summary(sid) for sid in source_ids]

    def ingest_test_cases(
        self,
        source_id: uuid.UUID,
        cases: List[CreateTestCaseRequest],
    ) -> IngestBatchResponse:
        """
        Batch ingest attack test cases into a benchmark source.
        Computes SHA-256 content hashes, skips existing duplicate prompts, and updates the manifest hash.
        """
        source = self.get_source(source_id)
        if not cases:
            stmt_total = select(func.count(TestCase.id)).where(TestCase.source_id == source_id)
            total_count = self.db.scalar(stmt_total) or 0
            return IngestBatchResponse(
                source_id=source_id,
                ingested_count=0,
                duplicate_count=0,
                total_source_cases=total_count,
                manifest_hash=source.manifest_hash,
            )

        # Pre-fetch existing content hashes and external refs for this source
        stmt_hashes = select(TestCase.content_hash).where(TestCase.source_id == source_id)
        existing_hashes = set(self.db.scalars(stmt_hashes).all())

        stmt_refs = select(TestCase.external_case_ref).where(
            TestCase.source_id == source_id, TestCase.external_case_ref.is_not(None)
        )
        existing_refs = set(self.db.scalars(stmt_refs).all())

        ingested_count = 0
        duplicate_count = 0
        batch_seen_hashes = set()

        for case_req in cases:
            content_hash = compute_content_hash(
                category=case_req.category,
                subcategory=case_req.subcategory,
                prompt_template=case_req.prompt_template,
            )

            # Check if duplicate in source or in this current batch
            if content_hash in existing_hashes or content_hash in batch_seen_hashes:
                duplicate_count += 1
                continue

            if case_req.external_case_ref and case_req.external_case_ref in existing_refs:
                duplicate_count += 1
                continue

            # Create TestCase entity
            test_case = TestCase(
                id=uuid.uuid4(),
                source_id=source_id,
                external_case_ref=case_req.external_case_ref,
                content_hash=content_hash,
                category=case_req.category.strip().upper(),
                subcategory=case_req.subcategory.strip().upper(),
                mode=case_req.mode,
                prompt_template=case_req.prompt_template.strip(),
                variables_schema=case_req.variables_schema,
                session_script=case_req.session_script,
                owasp_ids=case_req.owasp_ids,
                severity_ceiling=case_req.severity_ceiling,
                review_status=case_req.review_status,
                language=case_req.language or "en",
                metadata_payload=case_req.metadata_payload,
            )
            self.db.add(test_case)
            batch_seen_hashes.add(content_hash)
            existing_hashes.add(content_hash)
            if case_req.external_case_ref:
                existing_refs.add(case_req.external_case_ref)
            ingested_count += 1

        self.db.flush()

        # Update source manifest hash across all current test cases
        all_hashes = list(existing_hashes)
        new_manifest_hash = compute_manifest_hash(all_hashes)
        source.manifest_hash = new_manifest_hash

        self.db.commit()

        stmt_total = select(func.count(TestCase.id)).where(TestCase.source_id == source_id)
        total_source_cases = self.db.scalar(stmt_total) or 0

        logger.info(
            f"Ingested {ingested_count} test cases (skipped {duplicate_count} duplicates) for source '{source.name}'. Total cases: {total_source_cases}"
        )
        return IngestBatchResponse(
            source_id=source_id,
            ingested_count=ingested_count,
            duplicate_count=duplicate_count,
            total_source_cases=total_source_cases,
            manifest_hash=new_manifest_hash,
        )

    def list_test_cases(
        self,
        source_id: Optional[uuid.UUID] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        severity: Optional[SeverityLevel] = None,
        mode: Optional[TestCaseMode] = None,
        review_status: Optional[ReviewStatus] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Page[TestCaseResponse]:
        """Paginated search across the test case catalog."""
        stmt = select(TestCase)
        count_stmt = select(func.count(TestCase.id))

        if source_id:
            stmt = stmt.where(TestCase.source_id == source_id)
            count_stmt = count_stmt.where(TestCase.source_id == source_id)
        if category:
            stmt = stmt.where(TestCase.category == category.upper())
            count_stmt = count_stmt.where(TestCase.category == category.upper())
        if subcategory:
            stmt = stmt.where(TestCase.subcategory == subcategory.upper())
            count_stmt = count_stmt.where(TestCase.subcategory == subcategory.upper())
        if severity:
            stmt = stmt.where(TestCase.severity_ceiling == severity)
            count_stmt = count_stmt.where(TestCase.severity_ceiling == severity)
        if mode:
            stmt = stmt.where(TestCase.mode == mode)
            count_stmt = count_stmt.where(TestCase.mode == mode)
        if review_status:
            stmt = stmt.where(TestCase.review_status == review_status)
            count_stmt = count_stmt.where(TestCase.review_status == review_status)
        if search:
            stmt = stmt.where(TestCase.prompt_template.ilike(f"%{search}%"))
            count_stmt = count_stmt.where(TestCase.prompt_template.ilike(f"%{search}%"))

        total_estimate = self.db.scalar(count_stmt) or 0
        stmt = stmt.order_by(TestCase.category, TestCase.subcategory, TestCase.created_at).offset(offset).limit(limit)
        items = list(self.db.scalars(stmt).all())

        return Page(
            items=[TestCaseResponse.model_validate(tc, from_attributes=True) for tc in items],
            total_estimate=total_estimate,
        )

    def select_test_cases(
        self,
        mode: JobMode = JobMode.QUICK,
        categories: Optional[List[str]] = None,
        seed: int = 42,
        sample_size: Optional[int] = None,
    ) -> SampledTestCasesResponse:
        """
        Stratified sampling engine for Quick and Full evaluation runs.
        - Quick Mode: Capped at ~25 prompts (balanced across categories).
        - Full Audit Mode: Capped at 150-200 relevant prompts (balanced across all risk pools).
        - Deterministic: Seeded sampling produces identical outputs for identical seeds.
        """
        # 1. Fetch eligible approved test cases
        stmt = select(TestCase).where(TestCase.review_status == ReviewStatus.APPROVED)
        if categories:
            normalized_cats = [c.upper() for c in categories]
            stmt = stmt.where(TestCase.category.in_(normalized_cats))

        candidates = list(self.db.scalars(stmt).all())
        if not candidates:
            return SampledTestCasesResponse(
                mode=mode,
                seed=seed,
                total_sampled=0,
                category_distribution={},
                test_cases=[],
            )

        # 2. Determine target budget
        if sample_size is not None:
            # Explicit override capped at 200
            target_budget = min(max(1, sample_size), 200)
        elif mode == JobMode.QUICK:
            target_budget = min(25, len(candidates))
        else:
            # Full Audit Mode: Capped at 150-200 relevant prompts
            target_budget = min(150, len(candidates))

        # 3. Stratified grouping by category
        cat_groups: Dict[str, List[TestCase]] = defaultdict(list)
        for tc in candidates:
            cat_groups[tc.category].append(tc)

        active_categories = sorted(list(cat_groups.keys()))
        num_cats = len(active_categories)

        # 4. Deterministic shuffle per category
        rng = random.Random(seed)
        for cat in active_categories:
            # Sort first for deterministic baseline before shuffle
            cat_groups[cat].sort(key=lambda x: x.content_hash)
            rng.shuffle(cat_groups[cat])

        # 5. Distribute quota evenly across categories
        selected: List[TestCase] = []
        base_quota = target_budget // num_cats

        # First pass: take base_quota from each category
        remaining_budget = target_budget
        category_pointers = {cat: 0 for cat in active_categories}

        for cat in active_categories:
            items_to_take = min(base_quota, len(cat_groups[cat]))
            selected.extend(cat_groups[cat][:items_to_take])
            category_pointers[cat] = items_to_take
            remaining_budget -= items_to_take

        # Second pass: round-robin any remaining budget
        while remaining_budget > 0:
            added_any = False
            for cat in active_categories:
                ptr = category_pointers[cat]
                if ptr < len(cat_groups[cat]):
                    selected.append(cat_groups[cat][ptr])
                    category_pointers[cat] += 1
                    remaining_budget -= 1
                    added_any = True
                    if remaining_budget <= 0:
                        break
            if not added_any:
                break  # All available candidates exhausted

        # 6. Sort selected test cases deterministically for the evaluation runner
        selected.sort(key=lambda x: (x.category, x.subcategory, x.content_hash))

        # 7. Compute distribution
        category_distribution: Dict[str, int] = defaultdict(int)
        for tc in selected:
            category_distribution[tc.category] += 1

        return SampledTestCasesResponse(
            mode=mode,
            seed=seed,
            total_sampled=len(selected),
            category_distribution=dict(category_distribution),
            test_cases=[TestCaseResponse.model_validate(tc, from_attributes=True) for tc in selected],
        )
