from collections import defaultdict
import csv
import datetime
import hashlib
import io
import json
import random
import time
from typing import Any, Dict, List, Optional, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.core.logging import logger
from app.domain.enums import (
    BenchmarkSourceStatus,
    BenchmarkSourceType,
    JobMode,
    ReviewStatus,
    SeverityLevel,
    TestCaseMode,
)
from app.modules.benchmarks.models import BenchmarkSource, TestCase
from app.modules.benchmarks.schemas import (
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


def compute_manifest_hash(hashes: List[str], source_id: Optional[uuid.UUID] = None) -> str:
    """Compute deterministic manifest hash across all sorted test case hashes in a source."""
    prefix = f"{source_id}:" if source_id else ""
    if not hashes:
        return hashlib.sha256(f"{prefix}empty_manifest".encode("utf-8")).hexdigest()
    sorted_hashes = sorted(hashes)
    concatenated = prefix + "".join(sorted_hashes)
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

    def delete_source(self, source_id: uuid.UUID, tenant_id: Optional[uuid.UUID] = None) -> bool:
        """Delete a benchmark source and its associated test cases."""
        source = self.get_source(source_id)
        if tenant_id and source.tenant_id and source.tenant_id != tenant_id:
            raise ForbiddenError("Not authorized to delete this benchmark source")

        stmt_del_cases = select(TestCase.id).where(TestCase.source_id == source_id)
        case_ids = list(self.db.scalars(stmt_del_cases).all())
        if case_ids:
            self.db.query(TestCase).filter(TestCase.source_id == source_id).delete(synchronize_session=False)

        self.db.delete(source)
        self.db.commit()
        logger.info(f"Deleted benchmark source '{source.name}' ({source_id}) with {len(case_ids)} test cases")
        return True

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
        new_manifest_hash = compute_manifest_hash(all_hashes, source_id=source.id)
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
        source_ids: Optional[List[uuid.UUID]] = None,
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
        if source_ids:
            stmt = stmt.where(TestCase.source_id.in_(source_ids))
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

    def upload_and_ingest_suite(
        self,
        tenant_id: Optional[uuid.UUID],
        name: str,
        description: Optional[str],
        file_content: bytes,
        filename: str,
        fallback_category: str = "FINANCIAL_FRAUD",
    ) -> IngestBatchResponse:
        """Parse and ingest test cases from an uploaded CSV or JSON file into a new custom benchmark suite."""
        if not file_content:
            raise ValidationError("Uploaded file is empty.")

        text_content = file_content.decode("utf-8-sig", errors="replace").strip()
        if not text_content:
            raise ValidationError("Uploaded file contains no readable text.")

        lower_name = filename.lower()
        test_case_inputs: List[CreateTestCaseRequest] = []

        if lower_name.endswith(".json"):
            try:
                parsed_json = json.loads(text_content)
            except Exception as e:
                raise ValidationError(f"Invalid JSON file format: {e}")

            raw_cases = []
            if isinstance(parsed_json, list):
                raw_cases = parsed_json
            elif isinstance(parsed_json, dict):
                raw_cases = (
                    parsed_json.get("test_cases")
                    or parsed_json.get("cases")
                    or parsed_json.get("prompts")
                    or [parsed_json]
                )
            else:
                raise ValidationError("JSON root must be an array of test cases or an object with a 'test_cases' list.")

            for idx, item in enumerate(raw_cases):
                if not isinstance(item, dict):
                    continue
                prompt = (
                    item.get("prompt")
                    or item.get("prompt_template")
                    or item.get("attack_prompt")
                    or item.get("text")
                    or ""
                ).strip()
                if not prompt:
                    continue

                cat = (item.get("category") or item.get("pillar") or fallback_category).strip().upper()
                subcat = (item.get("subcategory") or item.get("intent") or f"{cat}_GENERAL").strip().upper()

                raw_sev = str(item.get("severity") or item.get("severity_ceiling") or "HIGH").strip().upper()
                try:
                    sev = SeverityLevel(raw_sev)
                except Exception:
                    sev = SeverityLevel.HIGH

                raw_mode = str(item.get("mode") or "SINGLE").strip().upper()
                try:
                    mode_val = TestCaseMode(raw_mode)
                except Exception:
                    mode_val = TestCaseMode.SINGLE

                owasp = item.get("owasp_ids") or []
                if isinstance(owasp, str):
                    owasp = [owasp] if owasp else []
                if not owasp and item.get("owasp_id"):
                    owasp = [str(item["owasp_id"])]

                session_script = item.get("session_script")
                if not session_script and "turns" in item:
                    session_script = {"turns": item["turns"]}
                    mode_val = TestCaseMode.SESSION

                test_case_inputs.append(
                    CreateTestCaseRequest(
                        external_case_ref=str(item.get("external_case_ref") or item.get("id") or f"custom_{idx+1}"),
                        category=cat,
                        subcategory=subcat,
                        prompt_template=prompt,
                        mode=mode_val,
                        session_script=session_script,
                        owasp_ids=owasp,
                        severity_ceiling=sev,
                        review_status=ReviewStatus.APPROVED,
                        language=item.get("language", "en"),
                        metadata_payload={"source_file": filename, "uploaded_name": name},
                    )
                )

        elif lower_name.endswith(".csv") or lower_name.endswith(".txt"):
            try:
                reader = csv.DictReader(io.StringIO(text_content))
            except Exception as e:
                raise ValidationError(f"Invalid CSV file format: {e}")

            for idx, row in enumerate(reader):
                if not row:
                    continue
                # Find prompt column
                prompt = ""
                for key in ["prompt", "prompt_template", "attack_prompt", "text", "test_case"]:
                    if key in row and row[key]:
                        prompt = row[key].strip()
                        break
                if not prompt:
                    first_val = list(row.values())[0] if row.values() else ""
                    if first_val and len(first_val) > 5:
                        prompt = first_val.strip()

                if not prompt:
                    continue

                cat = (row.get("category") or row.get("threat_category") or row.get("pillar") or fallback_category).strip().upper()
                subcat = (row.get("subcategory") or row.get("intent") or row.get("attack_type") or f"{cat}_GENERAL").strip().upper()

                raw_sev = str(row.get("severity") or row.get("severity_ceiling") or "HIGH").strip().upper()
                try:
                    sev = SeverityLevel(raw_sev)
                except Exception:
                    sev = SeverityLevel.HIGH

                raw_mode = str(row.get("mode") or "SINGLE").strip().upper()
                try:
                    mode_val = TestCaseMode(raw_mode)
                except Exception:
                    mode_val = TestCaseMode.SINGLE

                owasp_raw = row.get("owasp_id") or row.get("owasp_ids") or ""
                owasp = [o.strip() for o in owasp_raw.split(";") if o.strip()] if owasp_raw else []

                session_script = None
                if row.get("session_script"):
                    try:
                        session_script = json.loads(row["session_script"])
                        mode_val = TestCaseMode.SESSION
                    except Exception:
                        pass

                test_case_inputs.append(
                    CreateTestCaseRequest(
                        external_case_ref=row.get("external_case_ref") or row.get("id") or f"custom_{idx+1}",
                        category=cat,
                        subcategory=subcat,
                        prompt_template=prompt,
                        mode=mode_val,
                        session_script=session_script,
                        owasp_ids=owasp,
                        severity_ceiling=sev,
                        review_status=ReviewStatus.APPROVED,
                        language=row.get("language", "en"),
                        metadata_payload={"source_file": filename, "uploaded_name": name},
                    )
                )
        else:
            raise ValidationError("Unsupported file format. Please upload a .csv or .json file.")

        if not test_case_inputs:
            raise ValidationError("No valid test case prompts could be extracted from the uploaded file.")

        # Create new BenchmarkSource
        source_id = uuid.uuid4()
        revision = f"v{int(time.time())}_{source_id.hex[:6]}"
        initial_manifest = hashlib.sha256(f"{name}:{filename}:{revision}:{source_id}".encode("utf-8")).hexdigest()

        source = BenchmarkSource(
            id=source_id,
            tenant_id=tenant_id,
            name=name.strip(),
            source_type=BenchmarkSourceType.DOMAIN_CUSTOM,
            external_ref=filename,
            revision=revision,
            license_text=description or "Custom user uploaded test suite",
            manifest_hash=initial_manifest,
            status=BenchmarkSourceStatus.APPROVED,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)

        return self.ingest_test_cases(source_id=source.id, cases=test_case_inputs)
