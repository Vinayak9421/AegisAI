# Phase 5: Evaluation Jobs Orchestration & Independent Judge Integration

**Status:** Completed  
**Branch:** `aegis-v1`  
**Test Suite:** 55 tests passing (`pytest tests/ -v`)

---

## 1. Objectives Completed

1. **Structured Evaluation Job Orchestration:**
   - Implemented `JobService` supporting job creation with stratified sampling (Quick mode: 25 prompts, Full mode: 150–200 prompts).
   - Atomic transaction guarantees: target configuration snapshotting, dataset manifest recording, and creation of immutable work items (`job_items`).
   - Tenant isolation, authorization verification (target must be in `VERIFIED` status), and RFC-compliant idempotency replay (`Idempotency-Key` header).
   - Cooperative job cancellation (`POST /api/v1/jobs/{id}/cancel`) preventing cancellations of already completed or cancelled jobs.

2. **Independent LLM Judge Integration:**
   - Created `GroqJudgeAdapter` implementing `JudgePort` interface.
   - Strict untrusted evidence isolation delimiters (`<<<ATTACK_PROMPT_START>>>`, `<<<TARGET_RESPONSE_START>>>`) to defend against target prompt injections attempting to jailbreak the evaluator.
   - Structured JSON schema enforcement with strict normalization (e.g. forcing `verdict=SAFE` to always have `severity=NONE`).
   - Deterministic heuristic fallback evaluator for offline testing, rate limiting (HTTP 429), or target error responses.
   - Pluggable `JudgeRouter` factory.

3. **Evaluation Worker Runner:**
   - Implemented `EvaluationRunner` in `app/workers/runner.py`.
   - Execution loop executing single-turn attack cases through `HostedConnector` (with decrypted in-memory credentials from envelope encryption).
   - Atomic recording of:
     - Target invocation attempts (`ResultAttempt` phase `TARGET`)
     - Judge evaluation attempts (`ResultAttempt` phase `JUDGE`)
     - Deterministic logical results (`TestResult`) indexed by SHA-256 `logical_key`
     - Judge verdict details (`JudgeEvaluation`)
   - Sequential execution loop with cooperative cancellation checks.

4. **REST API v1 Endpoints:**
   - `POST /api/v1/jobs`: Create evaluation job with sampling mode and authorization check.
   - `GET /api/v1/jobs`: List jobs for authenticated tenant with pagination.
   - `GET /api/v1/jobs/{id}`: Retrieve detailed job progress and metadata.
   - `POST /api/v1/jobs/{id}/cancel`: Cooperatively cancel job.
   - `POST /api/v1/jobs/{id}/run`: Run pending work items to completion.
   - `GET /api/v1/jobs/{id}/results`: Query results with verdict, severity, and category filters.

---

## 2. Test Verification Matrix

| Test Suite | Coverage Area | Status |
| :--- | :--- | :--- |
| `tests/test_judge.py` | Refusal detection (SAFE / NONE) | PASSED |
| `tests/test_judge.py` | Exploitation detection (UNSAFE / HIGH) | PASSED |
| `tests/test_judge.py` | Target failure fallback (NOT_EVALUABLE / NONE) | PASSED |
| `tests/test_judge.py` | JSON parsing & severity normalization | PASSED |
| `tests/test_judge.py` | Live Groq mock API response parsing | PASSED |
| `tests/test_judge.py` | HTTP 429 rate-limit heuristic fallback | PASSED |
| `tests/test_judge.py` | JudgeRouter provider factory | PASSED |
| `tests/test_jobs.py` | Quick mode job creation & idempotency | PASSED |
| `tests/test_jobs.py` | Target authorization & VERIFIED status validation | PASSED |
| `tests/test_jobs.py` | Job listing and retrieval | PASSED |
| `tests/test_jobs.py` | Cooperative cancellation & terminal state rejection | PASSED |
| `tests/test_jobs.py` | End-to-end evaluation runner, judging, and results query | PASSED |
| **All Tests** | **55 passed in 5.34s across entire backend** | **100% PASS** |
