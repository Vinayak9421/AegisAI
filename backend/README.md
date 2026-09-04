# Aegis AI — Backend & Database Foundation (Phase 1)

Aegis AI is a provenance-aware, application-level red-teaming and trust/safety evaluation platform for authorized fintech LLM applications.

This directory contains the **Phase 1 Backend and Database Foundation**, providing the persistence layer, data models, schema migrations, typed configuration, correlation middleware, and API foundation upon which evaluation jobs, target connectors, independent judging, and certificates will be built.

---

## 1. Architecture Overview

Phase 1 follows a **modular monolith** pattern with strict domain isolation:

```
backend/
├── app/
│   ├── main.py                          # FastAPI application & lifecycle entrypoint
│   ├── api/
│   │   ├── deps.py                      # FastAPI dependency injection (DB session, auth headers)
│   │   ├── error_handlers.py            # Central domain exception -> API envelope mapping
│   │   └── v1/
│   │       ├── router.py                # Central v1 API router
│   │       └── health.py                # GET /health/live, /health/ready, /health/db
│   ├── core/
│   │   ├── config.py                    # Typed Pydantic Settings with env parsing & safety gates
│   │   ├── logging.py                   # Structured logging with secret redaction & request IDs
│   │   ├── errors.py                    # Domain exception hierarchy
│   │   ├── middleware.py                # Correlation ID (X-Request-ID) & latency tracking
│   │   └── security.py                  # Password hashing & envelope encryption for credentials
│   ├── domain/
│   │   ├── enums.py                     # System state machine & categorical enums
│   │   ├── contracts.py                 # Abstract ports for connectors, judges, and scorers
│   │   └── state_machines.py            # State transition validation tables
│   ├── db/
│   │   ├── base.py                      # DeclarativeBase, naming conventions & dialect types
│   │   ├── session.py                   # SQLAlchemy engine, sessionmaker & get_db provider
│   │   └── models/                      # 20 relational database models
│   │       ├── tenant.py                # Tenant, User, AuthSession
│   │       ├── target.py                # Target, TargetCredential (encrypted)
│   │       ├── provenance.py            # ProvenanceRecord (immutable versions)
│   │       ├── benchmark.py             # BenchmarkSource, TestCase
│   │       ├── job.py                   # Job, JobItem (resumable work checkpoints)
│   │       ├── session.py               # Session, SessionTurn (multi-turn history)
│   │       ├── result.py                # TestResult, ResultAttempt, JudgeEvaluation
│   │       ├── trace.py                 # TraceResult, TraceStage (agentic execution)
│   │       ├── certificate.py           # Certificate (immutable report projections)
│   │       ├── audit.py                 # AuditLog (append-only compliance trail)
│   │       └── idempotency.py           # IdempotencyKey (POST command deduplication)
│   ├── schemas/                         # Pydantic v2 DTOs
│   │   ├── common.py                    # ApiResponse[T], ApiErrorResponse, Page[T]
│   │   ├── health.py                    # Health probe schemas
│   │   ├── auth.py                      # Auth & user schemas
│   │   ├── targets.py                   # Target & credential metadata schemas
│   │   ├── provenance.py                # Provenance declaration schemas
│   │   ├── jobs.py                      # Evaluation job schemas
│   │   ├── results.py                   # Result, attempt & session schemas
│   │   ├── certificates.py              # Certificate report schemas
│   │   └── benchmarks.py                # Benchmark & test case schemas
│   ├── services/                        # Service layer foundations (base interfaces)
│   ├── connectors/                      # Target connector adapters (base port)
│   ├── judging/                         # Independent judge adapters (base port)
│   ├── provenance/                      # Provenance scoring engine (base port)
│   ├── workers/                         # Worker lifecycle & lease recovery (base port)
│   └── certificates/                    # Certificate generation & masking (base port)
├── alembic/                             # Alembic migrations
│   ├── env.py                           # Migration runner configured with app metadata
│   ├── script.py.mako
│   └── versions/
│       └── 0001_initial_phase1_schema.py# Full Phase 1 schema migration
├── tests/                               # Pytest test suite
│   ├── conftest.py                      # Test database & client fixtures
│   ├── test_config.py                   # Configuration & env gate tests
│   ├── test_health.py                   # Health endpoint & correlation ID tests
│   ├── test_models.py                   # Model relationships, FKs & encryption tests
│   ├── test_result_identity.py          # Deterministic logical key deduplication tests
│   └── test_alembic_migrations.py       # Migration revision chain & metadata tests
├── docker-compose.yml                   # PostgreSQL 16 container definition
├── alembic.ini                          # Alembic configuration
├── pyproject.toml                       # Python package & build metadata
├── requirements.txt                     # Pinned runtime and test dependencies
└── .env.example                         # Documented template of environment variables
```

---

## 2. Database Schema (20 Implemented Tables)

| Table | Purpose | Primary Key | Key Constraints / Indexes |
|---|---|---|---|
| `tenants` | Multi-tenant isolation root | UUID | `name` UNIQUE |
| `users` | Authenticated principals | UUID | `(tenant_id, email)` UNIQUE, FK `tenants` |
| `auth_sessions` | Refresh tokens & revocation | UUID | `token_hash` UNIQUE, FK `users` |
| `targets` | Registered evaluation targets | UUID | `(tenant_id, name)` UNIQUE, FK `tenants`, `users` |
| `target_credentials` | Envelope-encrypted API secrets | UUID | FK `targets` (ciphertext never returned in API) |
| `provenance_records` | Declared metadata & Identity Score | UUID | `(target_id, version)` UNIQUE, FK `targets` |
| `benchmark_sources` | Curated dataset manifests | UUID | `manifest_hash` UNIQUE |
| `test_cases` | Curated attack prompts & scripts | UUID | `(source_id, content_hash)` UNIQUE |
| `jobs` | Immutable evaluation runs | UUID | `(tenant_id, state)` INDEX, FK `tenants`, `targets` |
| `job_items` | Durable work units & leases | UUID | `(job_id, state, next_retry_at)` INDEX, FK `jobs` |
| `sessions` | Multi-turn conversation state | UUID | `(job_id, state)` INDEX, FK `jobs` |
| `session_turns` | Per-turn prompt & history hashes | UUID | `(session_id, turn_number)` UNIQUE |
| `test_results` | Logical evaluation verdicts | UUID | `logical_key` UNIQUE (deterministic SHA-256) |
| `result_attempts` | Connector/judge execution attempts | UUID | `(job_item_id, attempt_no, phase)` UNIQUE |
| `judge_evaluations` | Independent judge verdicts | UUID | `(test_result_id, judge_model, rubric_version)` UNIQUE |
| `trace_results` | Agent trace metadata | UUID | `test_result_id` UNIQUE FK |
| `trace_stages` | Intermediate tool/reasoning steps | UUID | `(trace_result_id, stage_index)` UNIQUE |
| `certificates` | Trust & Safety reports | UUID | `(job_id, version)` UNIQUE, `certificate_number` UNIQUE |
| `audit_logs` | Append-only security audit trail | UUID | `(tenant_id, created_at)` INDEX |
| `idempotency_keys` | POST command deduplication | UUID | `(tenant_id, user_id, key)` UNIQUE |

---

## 3. Standard API Envelopes

### Success Envelope
```json
{
  "data": {
    "status": "alive",
    "environment": "development",
    "version": "0.1.0"
  },
  "meta": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Error Envelope
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource was not found",
    "details": [],
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

---

## 4. Local Setup & Quickstart

### Step 1: Start PostgreSQL (Docker)
```bash
docker-compose up -d postgres
```
*(Or use a locally installed PostgreSQL instance on port 5432 with database `aegis_ai`)*

### Step 2: Configure Environment
```bash
cp .env.example .env
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Alembic Migrations
```bash
alembic upgrade head
```

### Step 5: Start FastAPI Server
```bash
uvicorn app.main:app --reload --port 8000
```
Interactive documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

### Step 6: Run Automated Tests
```bash
pytest
```

---

## 5. Scope Boundaries (Intentionally Deferred to Later Phases)

To preserve architectural integrity and avoid incomplete implementations, the following components are scheduled for subsequent phases:
- **Phase 2:** Target Registration API, hosted LLM connector (`httpx`), and SSRF-safe URL validation.
- **Phase 3:** Provenance scoring engine and versioned metadata ingestion API.
- **Phase 4:** Benchmark ingestion and single-turn Sentinel attack execution engine.
- **Phase 5:** Independent judge router (Groq / Llama-3.3-70B) with schema repair.
- **Phase 6:** Metric calculations (AER, SHR, Trust Score) and Certificate generation.
- **Phase 7:** Multi-turn conversational sessions and agent trace evaluation (CMR).
