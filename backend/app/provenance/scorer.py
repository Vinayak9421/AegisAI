"""Provenance & Identity Scoring Engine.

Implements the 4-dimension scoring formula from Technical Plan Section 7.2:
    Identity Score = 0.30 * M + 0.35 * D + 0.25 * S + 0.10 * O

Where:
    M (Model Identity):
        - name_and_revision: 30%
        - provider_and_deployment: 20%
        - fine_tuning_disclosure: 20%
        - evidence_and_review: 30%
    D (Data Provenance):
        - source_inventory: 30%
        - ownership_and_licensing: 20%
        - update_version_metadata: 20%
        - retrieval_grounding_documentation: 30%
    S (System Configuration):
        - prompt_version_and_owner: 25%
        - safety_and_tool_constraints: 30%
        - review_change_history: 20%
        - limitations_and_escalation: 25%
    O (Operational Accountability):
        - application_version: 25%
        - contact_and_owner: 20%
        - evaluation_consent: 20%
        - evidence_freshness: 35%

Each sub-criterion is scored:
    - PRESENT: 1.0
    - PARTIALLY_PRESENT: 0.5
    - ABSENT: 0.0
    - NOT_APPLICABLE: Excluded from dimension denominator
"""

import datetime
import re
from typing import Any, Dict, List, Optional, Tuple

from app.core.errors import ValidationError
from app.core.logging import logger
from app.provenance.base import ProvenanceScoreResult, ProvenanceScorerPort

# Regex for common leaked API keys / secrets
SECRET_PATTERN = re.compile(
    r"(sk-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9_\-\.]{20,}|ey[A-Za-z0-9_\-]{30,})",
    re.IGNORECASE,
)


def validate_no_secrets(obj: Any, path: str = "provenance") -> None:
    """Recursively check that no API keys, bearer tokens, or secrets are embedded in metadata."""
    if isinstance(obj, str):
        if SECRET_PATTERN.search(obj):
            raise ValidationError(f"Potential credential or secret detected in field '{path}'. Plaintext secrets are prohibited in provenance metadata.")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            validate_no_secrets(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            validate_no_secrets(item, f"{path}[{i}]")


class ProvenanceScorer(ProvenanceScorerPort):
    """Computes deterministic Identity Scores and produces quality gap audit flags."""

    SCORE_VERSION = "identity_v1.0"

    def calculate_identity_score(
        self,
        model_metadata: Dict[str, Any],
        data_sources: Dict[str, Any],
        system_prompt_metadata: Dict[str, Any],
        operational_metadata: Dict[str, Any],
    ) -> ProvenanceScoreResult:
        """Calculate the 4-dimension Identity Score and identify documentation gaps."""
        # 1. Validate against leaked credentials in all metadata sections
        validate_no_secrets(model_metadata, "model_metadata")
        validate_no_secrets(data_sources, "data_sources")
        validate_no_secrets(system_prompt_metadata, "system_prompt_metadata")
        validate_no_secrets(operational_metadata, "operational_metadata")

        quality_flags: List[str] = []

        # 2. Score Dimension M: Model Identity
        score_m, flags_m = self._score_model_identity(model_metadata)
        quality_flags.extend(flags_m)

        # 3. Score Dimension D: Data Provenance
        score_d, flags_d = self._score_data_provenance(data_sources)
        quality_flags.extend(flags_d)

        # 4. Score Dimension S: System Configuration
        score_s, flags_s = self._score_system_configuration(system_prompt_metadata)
        quality_flags.extend(flags_s)

        # 5. Score Dimension O: Operational Accountability
        score_o, flags_o = self._score_operational_accountability(operational_metadata)
        quality_flags.extend(flags_o)

        # 6. Composite Identity Score = 0.30M + 0.35D + 0.25S + 0.10O
        raw_identity_score = (0.30 * score_m) + (0.35 * score_d) + (0.25 * score_s) + (0.10 * score_o)
        identity_score = round(max(0.0, min(100.0, raw_identity_score)), 2)

        dimension_scores = {
            "model_identity": round(score_m, 2),
            "data_provenance": round(score_d, 2),
            "system_configuration": round(score_s, 2),
            "operational_accountability": round(score_o, 2),
        }

        # Overall quality threshold flags
        if identity_score < 50.0:
            quality_flags.append("POOR_TRANSPARENCY_SCORE")
        elif identity_score < 75.0:
            quality_flags.append("MODERATE_TRANSPARENCY_SCORE")

        return ProvenanceScoreResult(
            identity_score=identity_score,
            quality_flags=sorted(list(set(quality_flags))),
            dimension_scores=dimension_scores,
            score_version=self.SCORE_VERSION,
        )

    # -------------------------------------------------------------------------
    # Dimension Evaluators
    # -------------------------------------------------------------------------

    def _score_model_identity(self, meta: Dict[str, Any]) -> Tuple[float, List[str]]:
        """M: name/revision 30%, provider/deployment 20%, fine-tuning 20%, evidence 30%."""
        flags: List[str] = []
        weights = {
            "name_and_revision": 0.30,
            "provider_and_deployment": 0.20,
            "fine_tuning_disclosure": 0.20,
            "evidence_and_review": 0.30,
        }
        scores: Dict[str, float] = {}

        # 1. Name and revision (30%)
        name = meta.get("model_name") or meta.get("name")
        revision = meta.get("model_revision") or meta.get("version") or meta.get("revision")
        if name and revision:
            scores["name_and_revision"] = 1.0
        elif name:
            scores["name_and_revision"] = 0.5
            flags.append("EVIDENCE_GAP: Missing model revision/version")
        else:
            scores["name_and_revision"] = 0.0
            flags.append("MISSING_MODEL_IDENTITY")

        # 2. Provider and deployment (20%)
        provider = meta.get("provider") or meta.get("organization")
        deployment = meta.get("deployment_mode") or meta.get("mode")
        if provider and deployment:
            scores["provider_and_deployment"] = 1.0
        elif provider or deployment:
            scores["provider_and_deployment"] = 0.5
            flags.append("EVIDENCE_GAP: Incomplete provider or deployment mode declaration")
        else:
            scores["provider_and_deployment"] = 0.0
            flags.append("EVIDENCE_GAP: Missing model provider and deployment mode")

        # 3. Fine-tuning disclosure (20%)
        # Explicit false is full disclosure; explicit true with details is full; partial details = 0.5
        is_fine_tuned = meta.get("is_fine_tuned")
        fine_tuning_details = meta.get("fine_tuning_details") or meta.get("fine_tuning")
        if is_fine_tuned is False:
            scores["fine_tuning_disclosure"] = 1.0
        elif is_fine_tuned is True:
            if fine_tuning_details and (isinstance(fine_tuning_details, dict) or len(str(fine_tuning_details)) > 10):
                scores["fine_tuning_disclosure"] = 1.0
            else:
                scores["fine_tuning_disclosure"] = 0.5
                flags.append("EVIDENCE_GAP: Model declared fine-tuned but missing adapter/dataset details")
        elif fine_tuning_details:
            scores["fine_tuning_disclosure"] = 0.5
        else:
            scores["fine_tuning_disclosure"] = 0.0
            flags.append("MISSING_FINE_TUNING_DISCLOSURE")

        # 4. Evidence and review (30%)
        evidence_links = meta.get("evidence_links") or meta.get("model_card_url") or meta.get("benchmark_refs")
        review_notes = meta.get("review_notes") or meta.get("evaluation_summary")
        if evidence_links and review_notes:
            scores["evidence_and_review"] = 1.0
        elif evidence_links or review_notes:
            scores["evidence_and_review"] = 0.5
            flags.append("EVIDENCE_GAP: Model card or review notes partially missing")
        else:
            scores["evidence_and_review"] = 0.0
            flags.append("EVIDENCE_GAP: Missing model evidence links or benchmark review")

        dimension_score = self._compute_weighted_dimension(scores, weights)
        if dimension_score < 70.0:
            flags.append("LOW_MODEL_TRANSPARENCY")

        return dimension_score, flags

    def _score_data_provenance(self, meta: Dict[str, Any]) -> Tuple[float, List[str]]:
        """D: source inventory 30%, ownership/licensing 20%, update/version 20%, retrieval/grounding 30%."""
        flags: List[str] = []
        weights = {
            "source_inventory": 0.30,
            "ownership_and_licensing": 0.20,
            "update_version_metadata": 0.20,
            "retrieval_grounding_documentation": 0.30,
        }
        scores: Dict[str, Optional[float]] = {}

        # Handle list or dict format for sources
        raw_sources = meta.get("sources") or meta.get("items") or []
        if isinstance(raw_sources, dict):
            raw_sources = list(raw_sources.values())
        if not isinstance(raw_sources, list):
            raw_sources = []

        # 1. Source inventory (30%)
        if len(raw_sources) > 0:
            # Check if all have source_id/name and purpose
            valid_items = [
                s for s in raw_sources
                if isinstance(s, dict) and (s.get("source_id") or s.get("name")) and s.get("purpose")
            ]
            if len(valid_items) == len(raw_sources):
                scores["source_inventory"] = 1.0
            elif len(valid_items) > 0:
                scores["source_inventory"] = 0.5
                flags.append("EVIDENCE_GAP: Some data sources lack defined purpose or identifiers")
            else:
                scores["source_inventory"] = 0.25
        else:
            scores["source_inventory"] = 0.0
            flags.append("NO_DECLARED_DATA_SOURCES")

        # 2. Ownership and licensing (20%)
        if len(raw_sources) > 0:
            licensed_items = [
                s for s in raw_sources
                if isinstance(s, dict) and (s.get("license") or s.get("licensing_status") or s.get("license_type"))
            ]
            owned_items = [
                s for s in raw_sources
                if isinstance(s, dict) and (s.get("owner") or s.get("organization") or s.get("publisher"))
            ]
            if len(licensed_items) == len(raw_sources) and len(owned_items) == len(raw_sources):
                scores["ownership_and_licensing"] = 1.0
            elif len(licensed_items) > 0 or len(owned_items) > 0:
                scores["ownership_and_licensing"] = 0.5
                flags.append("UNVERIFIED_DATA_LICENSES")
            else:
                scores["ownership_and_licensing"] = 0.0
                flags.append("UNVERIFIED_DATA_LICENSES")
        else:
            scores["ownership_and_licensing"] = 0.0

        # 3. Update and version metadata (20%)
        if len(raw_sources) > 0:
            versioned_items = [
                s for s in raw_sources
                if isinstance(s, dict) and (s.get("version") or s.get("last_updated") or s.get("collection_date"))
            ]
            if len(versioned_items) == len(raw_sources):
                scores["update_version_metadata"] = 1.0
            elif len(versioned_items) > 0:
                scores["update_version_metadata"] = 0.5
            else:
                scores["update_version_metadata"] = 0.0
        else:
            scores["update_version_metadata"] = 0.0

        # 4. Retrieval & Grounding documentation (30%)
        rag_enabled = meta.get("rag_enabled")
        grounding_policy = meta.get("grounding_policy") or meta.get("retrieval_policy") or meta.get("chunking_strategy")
        if rag_enabled is False or meta.get("retrieval_not_applicable") is True:
            # Excluded from denominator if explicitly not applicable
            scores["retrieval_grounding_documentation"] = None
        elif rag_enabled is True:
            if grounding_policy:
                scores["retrieval_grounding_documentation"] = 1.0
            else:
                scores["retrieval_grounding_documentation"] = 0.5
                flags.append("EVIDENCE_GAP: RAG enabled but retrieval grounding policy undocumented")
        elif grounding_policy:
            scores["retrieval_grounding_documentation"] = 0.75
        else:
            scores["retrieval_grounding_documentation"] = 0.0
            flags.append("EVIDENCE_GAP: Undocumented retrieval and grounding policy")

        dimension_score = self._compute_weighted_dimension(scores, weights)
        if dimension_score < 70.0:
            flags.append("INCOMPLETE_DATA_PROVENANCE")

        return dimension_score, flags

    def _score_system_configuration(self, meta: Dict[str, Any]) -> Tuple[float, List[str]]:
        """S: prompt version/owner 25%, safety/tool constraints 30%, review history 20%, limitations/escalation 25%."""
        flags: List[str] = []
        weights = {
            "prompt_version_and_owner": 0.25,
            "safety_and_tool_constraints": 0.30,
            "review_change_history": 0.20,
            "limitations_and_escalation": 0.25,
        }
        scores: Dict[str, Optional[float]] = {}

        # 1. Prompt version and owner (25%)
        documented = meta.get("documented", True)
        version = meta.get("prompt_version") or meta.get("version")
        owner = meta.get("prompt_owner") or meta.get("author") or meta.get("owner")
        if not documented:
            scores["prompt_version_and_owner"] = 0.0
            flags.append("EVIDENCE_GAP: System prompt documentation declared absent")
        elif version and owner:
            scores["prompt_version_and_owner"] = 1.0
        elif version or owner:
            scores["prompt_version_and_owner"] = 0.5
            flags.append("EVIDENCE_GAP: System prompt version or owner missing")
        else:
            scores["prompt_version_and_owner"] = 0.0
            flags.append("EVIDENCE_GAP: System prompt undocumented")

        # 2. Safety and tool constraints (30%)
        safety_rules = meta.get("safety_instructions") or meta.get("guardrails") or meta.get("safety_rules")
        tool_constraints = meta.get("tool_constraints") or meta.get("tool_policies") or meta.get("authority_limits")
        tools_enabled = meta.get("tools_enabled", True)

        if tools_enabled is False:
            # If tools are not enabled, tool constraints are N/A; only safety rules apply
            if safety_rules:
                scores["safety_and_tool_constraints"] = 1.0
            else:
                scores["safety_and_tool_constraints"] = 0.0
                flags.append("MISSING_SAFETY_CONSTRAINTS")
        else:
            if safety_rules and tool_constraints:
                scores["safety_and_tool_constraints"] = 1.0
            elif safety_rules or tool_constraints:
                scores["safety_and_tool_constraints"] = 0.5
                flags.append("EVIDENCE_GAP: Missing safety guardrails or tool execution constraints")
            else:
                scores["safety_and_tool_constraints"] = 0.0
                flags.append("MISSING_SAFETY_CONSTRAINTS")

        # 3. Review and change history (20%)
        change_history = meta.get("change_history") or meta.get("changelog") or meta.get("revisions")
        last_reviewed_at = meta.get("last_reviewed_at") or meta.get("last_review_date")
        if change_history and last_reviewed_at:
            scores["review_change_history"] = 1.0
        elif change_history or last_reviewed_at:
            scores["review_change_history"] = 0.5
        else:
            scores["review_change_history"] = 0.0
            flags.append("EVIDENCE_GAP: No system prompt review or change history")

        # 4. Limitations and escalation (25%)
        limitations = meta.get("known_limitations") or meta.get("limitations")
        escalation = meta.get("human_escalation_path") or meta.get("escalation_procedure") or meta.get("fallback")
        if limitations and escalation:
            scores["limitations_and_escalation"] = 1.0
        elif limitations or escalation:
            scores["limitations_and_escalation"] = 0.5
            flags.append("EVIDENCE_GAP: Known limitations or human escalation procedure missing")
        else:
            scores["limitations_and_escalation"] = 0.0
            flags.append("EVIDENCE_GAP: No documented limitations or escalation procedures")

        dimension_score = self._compute_weighted_dimension(scores, weights)
        if dimension_score < 70.0:
            flags.append("WEAK_SYSTEM_PROMPT_GOVERNANCE")

        return dimension_score, flags

    def _score_operational_accountability(self, meta: Dict[str, Any]) -> Tuple[float, List[str]]:
        """O: application version 25%, contact/owner 20%, evaluation consent 20%, evidence freshness 35%."""
        flags: List[str] = []
        weights = {
            "application_version": 0.25,
            "contact_and_owner": 0.20,
            "evaluation_consent": 0.20,
            "evidence_freshness": 0.35,
        }
        scores: Dict[str, Optional[float]] = {}

        # 1. Application version (25%)
        app_version = meta.get("application_version") or meta.get("app_version") or meta.get("version")
        if app_version:
            scores["application_version"] = 1.0
        else:
            scores["application_version"] = 0.0
            flags.append("EVIDENCE_GAP: Missing application release version")

        # 2. Contact and owner (20%)
        contact = meta.get("contact_email") or meta.get("owner_contact") or meta.get("responsible_team") or meta.get("owner")
        if contact:
            scores["contact_and_owner"] = 1.0
        else:
            scores["contact_and_owner"] = 0.0
            flags.append("EVIDENCE_GAP: Missing responsible contact or operational owner")

        # 3. Evaluation consent (20%)
        consent = meta.get("evaluation_consent") or meta.get("consent_confirmed") or meta.get("authorization_confirmed")
        if consent is True:
            scores["evaluation_consent"] = 1.0
        else:
            scores["evaluation_consent"] = 0.0
            flags.append("MISSING_EVALUATION_CONSENT")

        # 4. Evidence freshness (35%)
        # Metadata declared or verified within 90 days = 1.0; within 180 days = 0.5; older or missing = 0.0
        freshness_date_str = (
            meta.get("evidence_freshness_date")
            or meta.get("documented_at")
            or meta.get("last_verified_at")
            or meta.get("updated_at")
        )
        if freshness_date_str:
            try:
                if isinstance(freshness_date_str, (datetime.date, datetime.datetime)):
                    dt = freshness_date_str
                else:
                    dt = datetime.datetime.fromisoformat(str(freshness_date_str).replace("Z", "+00:00"))
                
                # Make timezone-aware UTC comparison
                now = datetime.datetime.now(datetime.timezone.utc)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=datetime.timezone.utc)
                
                days_diff = (now - dt).days
                if days_diff <= 90:
                    scores["evidence_freshness"] = 1.0
                elif days_diff <= 180:
                    scores["evidence_freshness"] = 0.5
                    flags.append("STALE_PROVENANCE_METADATA")
                else:
                    scores["evidence_freshness"] = 0.25
                    flags.append("STALE_PROVENANCE_METADATA")
            except Exception:
                scores["evidence_freshness"] = 0.5
        elif meta.get("is_fresh") is True:
            scores["evidence_freshness"] = 1.0
        else:
            # Fallback if no date is provided
            scores["evidence_freshness"] = 0.5
            flags.append("EVIDENCE_GAP: Missing evidence freshness date")

        dimension_score = self._compute_weighted_dimension(scores, weights)
        if dimension_score < 70.0:
            flags.append("LIMITED_OPERATIONAL_ACCOUNTABILITY")

        return dimension_score, flags

    # -------------------------------------------------------------------------
    # Math Helper: Dynamic denominator adjustment for N/A criteria
    # -------------------------------------------------------------------------

    def _compute_weighted_dimension(
        self,
        scores: Dict[str, Optional[float]],
        weights: Dict[str, float],
    ) -> float:
        """
        Compute dimension score (0 to 100).
        If any criterion is None (NOT_APPLICABLE), exclude it from the denominator.
        """
        eligible_weight = 0.0
        weighted_sum = 0.0

        for key, weight in weights.items():
            val = scores.get(key)
            if val is not None:
                eligible_weight += weight
                weighted_sum += val * weight

        if eligible_weight <= 0.0:
            return 100.0

        ratio = weighted_sum / eligible_weight
        return ratio * 100.0
