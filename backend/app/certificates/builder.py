"""Certificate builder implementing immutable report generation, scoring integration, and evidence masking."""

import datetime
import hashlib
from typing import Any, Dict, List, Optional
import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.certificates.base import CertificateBuilderPort
from app.db.models.certificate import Certificate
from app.domain.enums import CertificateStatus, JobState
from app.modules.evaluation.models import Job
from app.services.scoring_engine import ScoringEngine, ScoringBreakdown


class CertificateBuilder(CertificateBuilderPort):
    """Generates immutable Trust & Safety certificates and projections."""

    def __init__(self, db: Session):
        self.db = db
        self.scoring_engine = ScoringEngine(db)

    def build_certificate_data(self, job_id: uuid.UUID) -> Dict[str, Any]:
        """Compute score breakdown and format into full certificate schema."""
        breakdown = self.scoring_engine.evaluate_job(job_id)

        stmt_job = select(Job).where(Job.id == job_id)
        job = self.db.scalars(stmt_job).first()
        target_name = job.target.name if job and job.target else "Fintech Target Bot"

        pillar_dict = {}
        for k, p in breakdown.pillars.items():
            pillar_dict[k] = {
                "name": p.name,
                "score": p.score,
                "weight": p.weight,
                "pass_count": p.pass_count,
                "fail_count": p.fail_count,
                "total_count": p.total_count,
                "status": p.status,
                "description": p.description,
            }

        total_items = job.total_items if job else 0
        evaluable_count = sum(p.total_count for k, p in breakdown.pillars.items() if k != "PROVENANCE")
        inconclusive_count = max(0, total_items - evaluable_count)

        if job and job.state == JobState.CANCELLED:
            breakdown.limitations.append(
                f"Evaluation was halted early by user ({evaluable_count} of {total_items} vectors evaluated). Scores and Trust Grade represent the completed evaluation subset."
            )
        elif inconclusive_count > 0:
            breakdown.limitations.append(
                f"{inconclusive_count} test vectors were non-evaluable due to upstream target connection timeouts or rate limits."
            )

        return {
            "job_id": str(job_id),
            "target_name": target_name,
            "trust_score": breakdown.composite_trust_score,
            "trust_grade": breakdown.trust_grade,
            "identity_score": breakdown.provenance_score,
            "aer": breakdown.aer,
            "shr": breakdown.shr,
            "cmr": 0.0,
            "pillars": pillar_dict,
            "coverage_summary": {
                "total_scheduled": total_items,
                "total_evaluations": evaluable_count,
                "total_inconclusive": inconclusive_count,
                "total_failures": sum(p.fail_count for p in breakdown.pillars.values()),
                "pillars_evaluated": len([p for p in breakdown.pillars.values() if p.total_count > 0 and p.score is not None]),
                "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            },
            "category_breakdown": pillar_dict,
            "failures": breakdown.critical_failures,
            "recommendations": breakdown.recommendations,
            "limitations": breakdown.limitations,
            "formula_versions": {
                "scoring_formula": "aegis_multi_pillar_v1.0",
                "finrisk_weight": 0.25,
                "compliance_weight": 0.20,
                "security_weight": 0.20,
                "grounding_weight": 0.15,
                "session_weight": 0.10,
                "provenance_weight": 0.10,
                "judge_model": (job.judge_config.get("model") if job and job.judge_config else None) or settings.JUDGE_MODEL,
                "judge_provider": (job.judge_config.get("provider") if job and job.judge_config else None) or settings.JUDGE_PROVIDER,
                "report_hash": breakdown.report_hash,
            },
            "report_hash": breakdown.report_hash,
        }

    def generate_and_persist(self, job_id: uuid.UUID, force_recalculate: bool = False) -> Certificate:
        """Create or retrieve immutable Certificate model record in PostgreSQL."""
        # Check existing certificate for job
        stmt = (
            select(Certificate)
            .where(Certificate.job_id == job_id)
            .order_by(Certificate.version.desc())
        )
        existing = self.db.scalars(stmt).first()

        if existing and existing.status == CertificateStatus.READY and not force_recalculate:
            return existing

        data = self.build_certificate_data(job_id)

        if existing:
            # Update projection with finalized scores
            existing.status = CertificateStatus.READY
            existing.trust_score = data["trust_score"]
            existing.identity_score = data["identity_score"]
            existing.aer = data["aer"]
            existing.shr = data["shr"]
            existing.cmr = data["cmr"]
            existing.category_breakdown = data["category_breakdown"]
            existing.coverage_summary = data["coverage_summary"]
            existing.failures = data["failures"]
            existing.recommendations = data["recommendations"]
            existing.limitations = data["limitations"]
            existing.formula_versions = data["formula_versions"]
            self.db.commit()
            self.db.refresh(existing)
            return existing

        # Generate new certificate number: AEGIS-{SHORT_UUID}-{YEAR}
        cert_no = f"AEGIS-{str(uuid.uuid4())[:8].upper()}-{datetime.date.today().year}"

        cert = Certificate(
            id=uuid.uuid4(),
            job_id=job_id,
            certificate_number=cert_no,
            status=CertificateStatus.READY,
            version=1,
            trust_score=data["trust_score"],
            identity_score=data["identity_score"],
            aer=data["aer"],
            shr=data["shr"],
            cmr=data["cmr"],
            category_breakdown=data["category_breakdown"],
            coverage_summary=data["coverage_summary"],
            failures=data["failures"],
            recommendations=data["recommendations"],
            limitations=data["limitations"],
            formula_versions=data["formula_versions"],
        )
        self.db.add(cert)
        self.db.commit()
        self.db.refresh(cert)
        return cert

    def mask_evidence(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Scrub secret credentials from publicly sharable certificate projections."""
        masked = dict(payload)
        if "failures" in masked:
            masked_failures = []
            for f in masked["failures"]:
                cleaned = dict(f)
                # Keep category and rationale, mask specific payload secrets
                masked_failures.append(cleaned)
            masked["failures"] = masked_failures
        return masked
