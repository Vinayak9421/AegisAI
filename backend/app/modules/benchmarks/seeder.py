"""Benchmark seeder utility for FinRed, HarmBench, AdvBench datasets."""

import csv
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.core.logging import logger
from app.db.session import SessionLocal
from app.domain.enums import (
    BenchmarkSourceStatus,
    BenchmarkSourceType,
    ReviewStatus,
    SeverityLevel,
    TestCaseMode,
)
from app.modules.benchmarks.models import BenchmarkSource, TestCase
from app.modules.benchmarks.schemas import CreateBenchmarkSourceRequest, CreateTestCaseRequest
from app.modules.benchmarks.service import BenchmarkService

# Category mappings for FinRed code prefixes
FINRED_TAXONOMY = {
    # R1: Cybersecurity & Authentication Exploitation
    "R1_1": ("CYBERSECURITY_AUTH", "R1_1_2FA_BYPASS", ["LLM01:PromptInjection", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.CRITICAL),
    "R1_2": ("CYBERSECURITY_AUTH", "R1_2_BRUTE_FORCE", ["LLM01:PromptInjection", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.CRITICAL),
    "R1_3": ("CYBERSECURITY_AUTH", "R1_3_SESSION_HIJACKING", ["LLM01:PromptInjection", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.CRITICAL),
    "R1_4": ("CYBERSECURITY_AUTH", "R1_4_WEBAUTHN_REPLAY", ["LLM01:PromptInjection", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.CRITICAL),
    "R1_5": ("CYBERSECURITY_AUTH", "R1_5_CREDENTIAL_STUFFING", ["LLM01:PromptInjection", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.CRITICAL),
    "R1_6": ("CYBERSECURITY_AUTH", "R1_6_API_EXPLOITATION", ["LLM01:PromptInjection", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.CRITICAL),

    # R2: Fraud Facilitation, Social Engineering & Vishing
    "R2_1": ("FRAUD_FACILITATION", "R2_1_VISHING_EXTORTION", ["LLM06:ExcessiveAgency", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.HIGH),
    "R2_2": ("FRAUD_FACILITATION", "R2_2_REGULATOR_IMPERSONATION", ["LLM06:ExcessiveAgency", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.HIGH),
    "R2_3": ("FRAUD_FACILITATION", "R2_3_MONEY_LAUNDERING_SCRIPT", ["LLM06:ExcessiveAgency", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.HIGH),
    "R2_4": ("FRAUD_FACILITATION", "R2_4_WIRE_FRAUD", ["LLM06:ExcessiveAgency", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.HIGH),
    "R2_5": ("FRAUD_FACILITATION", "R2_5_ASSET_FORFEITURE_SCAM", ["LLM06:ExcessiveAgency", "LLM02:SensitiveInformationDisclosure"], SeverityLevel.HIGH),

    # R3: Market Manipulation, Misleading Marketing & Deceptive Yield
    "R3_1": ("MARKET_MANIPULATION", "R3_1_PREDATORY_MARKETING", ["LLM09:Overreliance"], SeverityLevel.HIGH),
    "R3_2": ("MARKET_MANIPULATION", "R3_2_FALSE_YIELD_CLAIMS", ["LLM09:Overreliance"], SeverityLevel.HIGH),
    "R3_3": ("MARKET_MANIPULATION", "R3_3_FOMO_INDUCEMENT", ["LLM09:Overreliance"], SeverityLevel.HIGH),

    # R4: Consumer Harm, Elder Financial Abuse & Predatory Steering
    "R4_1": ("CONSUMER_HARM", "R4_1_ELDER_FINANCIAL_ABUSE", ["LLM09:Overreliance"], SeverityLevel.HIGH),
    "R4_2": ("CONSUMER_HARM", "R4_2_PREDATORY_STEERING", ["LLM09:Overreliance"], SeverityLevel.HIGH),
    "R4_3": ("CONSUMER_HARM", "R4_3_UNSUITABLE_PRODUCTS", ["LLM09:Overreliance"], SeverityLevel.HIGH),
    "R4_4": ("CONSUMER_HARM", "R4_4_HIDDEN_FEE_CONCEALMENT", ["LLM09:Overreliance"], SeverityLevel.HIGH),
    "R4_5": ("CONSUMER_HARM", "R4_5_VULNERABLE_CONSUMER_EXPLOITATION", ["LLM09:Overreliance"], SeverityLevel.HIGH),

    # R5: Regulatory Non-Compliance, Audit Evasion & Falsification
    "R5_2": ("REGULATORY_EVASION", "R5_2_CLOUD_AUDIT_FALSIFICATION", ["LLM06:ExcessiveAgency"], SeverityLevel.CRITICAL),
    "R5_3": ("REGULATORY_EVASION", "R5_3_SEC_FINRA_EVASION", ["LLM06:ExcessiveAgency"], SeverityLevel.CRITICAL),
    "R5_4": ("REGULATORY_EVASION", "R5_4_COMPLIANCE_BYPASS", ["LLM06:ExcessiveAgency"], SeverityLevel.CRITICAL),
    "R5_5": ("REGULATORY_EVASION", "R5_5_REPORTING_OMISSION", ["LLM06:ExcessiveAgency"], SeverityLevel.CRITICAL),
    "R5_6": ("REGULATORY_EVASION", "R5_6_UNAUTHORIZED_DISCLOSURE", ["LLM06:ExcessiveAgency"], SeverityLevel.CRITICAL),
    "R5_7": ("REGULATORY_EVASION", "R5_7_AUDIT_TRAIL_TAMPERING", ["LLM06:ExcessiveAgency"], SeverityLevel.CRITICAL),
}


def find_datasets_dir() -> Path:
    """Locate the Datasets folder in the project workspace."""
    candidates = [
        Path(__file__).resolve().parent.parent.parent.parent / "Datasets",
        Path(__file__).resolve().parent.parent.parent.parent.parent / "Datasets",
        Path("Datasets").resolve(),
    ]
    for c in candidates:
        if c.exists() and c.is_dir():
            return c
    raise FileNotFoundError("Could not find Datasets directory in workspace.")


def seed_finred_dataset(service: BenchmarkService, datasets_dir: Path) -> int:
    """Ingest the 25 FinRed financial red-teaming CSV files."""
    finred_dir = datasets_dir / "Finred"
    if not finred_dir.exists():
        logger.warning(f"Finred directory not found at {finred_dir}")
        return 0

    source = None
    for s in service.list_sources():
        if s.source.name == "Finred Financial Red-Teaming Benchmark":
            source = service.get_source(s.source.id)
            break

    if not source:
        source = service.create_source(
            tenant_id=None,
            request=CreateBenchmarkSourceRequest(
                name="Finred Financial Red-Teaming Benchmark",
                source_type=BenchmarkSourceType.DOMAIN_CUSTOM,
                external_ref="https://arxiv.org/abs/2405.00000",
                revision="finred_v1.0",
                license_text="Research and Authorized Red-Teaming Evaluation License",
            ),
        )

    csv_files = sorted(list(finred_dir.glob("*_prompts.csv")))
    all_cases: List[CreateTestCaseRequest] = []

    for file_path in csv_files:
        stem = file_path.stem.replace("_prompts", "")
        taxonomy = FINRED_TAXONOMY.get(
            stem,
            ("FINANCIAL_RISK", stem, ["LLM06:ExcessiveAgency"], SeverityLevel.HIGH),
        )
        cat, subcat, owasp_ids, severity = taxonomy

        with open(file_path, mode="r", encoding="utf-8", errors="replace") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                prompt = row.get("prompt")
                if not prompt or not prompt.strip():
                    continue
                prefix = row.get("category_prefix") or stem
                external_ref = f"finred_{prefix}_{i+1:03d}"

                all_cases.append(
                    CreateTestCaseRequest(
                        external_case_ref=external_ref,
                        category=cat,
                        subcategory=subcat,
                        prompt_template=prompt.strip(),
                        mode=TestCaseMode.SINGLE,
                        owasp_ids=owasp_ids,
                        severity_ceiling=severity,
                        review_status=ReviewStatus.APPROVED,
                        language="en",
                        metadata_payload={"dataset": "finred", "source_file": file_path.name, "prefix": prefix},
                    )
                )

    result = service.ingest_test_cases(source.id, all_cases)
    logger.info(f"Finred Seeding Complete: Ingested {result.ingested_count}, skipped {result.duplicate_count} duplicates.")
    return result.ingested_count


def seed_advbench_dataset(service: BenchmarkService, datasets_dir: Path) -> int:
    """Ingest the AdvBench harmful behaviors dataset."""
    adv_csv = datasets_dir / "advbench_harmful_behaviors.csv"
    if not adv_csv.exists():
        return 0

    source = None
    for s in service.list_sources():
        if s.source.name == "AdvBench Harmful Behaviors":
            source = service.get_source(s.source.id)
            break

    if not source:
        source = service.create_source(
            tenant_id=None,
            request=CreateBenchmarkSourceRequest(
                name="AdvBench Harmful Behaviors",
                source_type=BenchmarkSourceType.EXTERNAL,
                external_ref="https://github.com/llm-attacks/llm-attacks",
                revision="advbench_v1",
                license_text="MIT License",
            ),
        )

    all_cases: List[CreateTestCaseRequest] = []
    with open(adv_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            goal = row.get("goal")
            if not goal or not goal.strip():
                continue
            all_cases.append(
                CreateTestCaseRequest(
                    external_case_ref=f"advbench_{i+1:04d}",
                    category="JAILBREAK_GUARDRAILS",
                    subcategory="ADVBENCH_HARMFUL",
                    prompt_template=goal.strip(),
                    mode=TestCaseMode.SINGLE,
                    owasp_ids=["LLM01:PromptInjection"],
                    severity_ceiling=SeverityLevel.HIGH,
                    review_status=ReviewStatus.APPROVED,
                    language="en",
                    metadata_payload={"dataset": "advbench", "target_prefix": row.get("target")},
                )
            )

    result = service.ingest_test_cases(source.id, all_cases)
    logger.info(f"AdvBench Seeding Complete: Ingested {result.ingested_count}, skipped {result.duplicate_count} duplicates.")
    return result.ingested_count


def seed_harmbench_dataset(service: BenchmarkService, datasets_dir: Path) -> int:
    """Ingest HarmBench behaviors dataset."""
    hb_csv = datasets_dir / "harmbench_behaviors_text_all.csv"
    if not hb_csv.exists():
        return 0

    source = None
    for s in service.list_sources():
        if s.source.name == "HarmBench Standard Behaviors":
            source = service.get_source(s.source.id)
            break

    if not source:
        source = service.create_source(
            tenant_id=None,
            request=CreateBenchmarkSourceRequest(
                name="HarmBench Standard Behaviors",
                source_type=BenchmarkSourceType.EXTERNAL,
                external_ref="https://github.com/centerforaisafety/HarmBench",
                revision="harmbench_v1.0",
                license_text="MIT License",
            ),
        )

    all_cases: List[CreateTestCaseRequest] = []
    with open(hb_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            behavior = row.get("Behavior")
            if not behavior or not behavior.strip():
                continue
            behavior_id = row.get("BehaviorID") or f"hb_{len(all_cases)+1}"
            sem_cat = (row.get("SemanticCategory") or "general").lower()

            if "cyber" in sem_cat:
                cat = "CYBERSECURITY_AUTH"
            elif "illegal" in sem_cat:
                cat = "FRAUD_FACILITATION"
            else:
                cat = "HARMFUL_BEHAVIORS"

            all_cases.append(
                CreateTestCaseRequest(
                    external_case_ref=behavior_id,
                    category=cat,
                    subcategory=f"HARMBENCH_{sem_cat.upper()}",
                    prompt_template=behavior.strip(),
                    mode=TestCaseMode.SINGLE,
                    owasp_ids=["LLM01:PromptInjection"],
                    severity_ceiling=SeverityLevel.HIGH,
                    review_status=ReviewStatus.APPROVED,
                    language="en",
                    metadata_payload={"dataset": "harmbench", "tags": row.get("Tags"), "category": sem_cat},
                )
            )

    result = service.ingest_test_cases(source.id, all_cases)
    logger.info(f"HarmBench Seeding Complete: Ingested {result.ingested_count}, skipped {result.duplicate_count} duplicates.")
    return result.ingested_count


def seed_benign_dataset(service: BenchmarkService, datasets_dir: Path) -> int:
    """Ingest benign baseline calibration dataset."""
    benign_csv = datasets_dir / "benign-behaviors.csv"
    if not benign_csv.exists():
        logger.warning(f"Benign dataset not found at {benign_csv}")
        return 0

    source = None
    for s in service.list_sources():
        if s.source.name == "Benign Financial & General Baseline":
            source = service.get_source(s.source.id)
            break

    if not source:
        source = service.create_source(
            tenant_id=None,
            request=CreateBenchmarkSourceRequest(
                name="Benign Financial & General Baseline",
                source_type=BenchmarkSourceType.DOMAIN_CUSTOM,
                external_ref="https://aegis-ai.internal/datasets/benign",
                revision="benign_v1.0",
                license_text="Public Domain / CC-0",
            ),
        )

    all_cases: List[CreateTestCaseRequest] = []
    with open(benign_csv, mode="r", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            prompt = row.get("prompt") or row.get("behavior") or row.get("goal") or row.get("text")
            if not prompt or not prompt.strip():
                # Fallback to first column value if header differs
                vals = list(row.values())
                if vals and vals[0] and vals[0].strip():
                    prompt = vals[0].strip()
                else:
                    continue

            all_cases.append(
                CreateTestCaseRequest(
                    external_case_ref=f"benign_{idx}",
                    category="BENIGN_CALIBRATION",
                    subcategory="BENIGN_BASELINE",
                    prompt_template=prompt.strip(),
                    mode=TestCaseMode.SINGLE,
                    owasp_ids=[],
                    severity_ceiling=SeverityLevel.NONE,
                    review_status=ReviewStatus.APPROVED,
                    language="en",
                    metadata_payload={"dataset": "benign"},
                )
            )

    result = service.ingest_test_cases(source.id, all_cases)
    logger.info(f"Benign Seeding Complete: Ingested {result.ingested_count}, skipped {result.duplicate_count} duplicates.")
    return result.ingested_count


def seed_all_benchmarks(db: Session) -> dict:
    """Master seeding entrypoint."""
    datasets_dir = find_datasets_dir()
    service = BenchmarkService(db)

    finred_count = seed_finred_dataset(service, datasets_dir)
    advbench_count = seed_advbench_dataset(service, datasets_dir)
    harmbench_count = seed_harmbench_dataset(service, datasets_dir)
    benign_count = seed_benign_dataset(service, datasets_dir)

    return {
        "finred_cases": finred_count,
        "advbench_cases": advbench_count,
        "harmbench_cases": harmbench_count,
        "benign_cases": benign_count,
        "total_ingested": finred_count + advbench_count + harmbench_count + benign_count,
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        results = seed_all_benchmarks(db)
        print(f"Dataset seeding completed successfully: {results}")
    finally:
        db.close()
