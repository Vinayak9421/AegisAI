# Aegis AI
### A Provenance-Aware Red-Teaming Platform for Trust and Safety Evaluation of Fintech LLM Applications

**Department of Computer Engineering, A. P. Shah Institute of Technology, Thane**
**Team (Div B):** Vivek Maurya (104), Vedant Mallya (101), Vinayak Mishra (115), Mihir Mehta (105)
**Guide:** Prof. Harshada Sonkamble

---

## 1. Problem Statement

LLM-powered chatbots and RAG applications are increasingly deployed in fintech — loan eligibility, welfare-scheme discovery, transaction support, and financial guidance — yet most are evaluated once, informally, before launch, if at all. Existing safety benchmarks (S-Eval, HarmBench, JailbreakBench) test the underlying model in isolation, without checking whether the deployed application's data sources, base model, or configuration are actually documented. Almost none test whether risk accumulates gradually across a multi-turn conversation, and none check whether a failure inside an agentic pipeline (retrieval → reasoning → response formatting) gets silently masked by a fluent final answer.

Real-world incidents already show the cost of this gap: Air Canada was held legally liable by a tribunal for its chatbot inventing a bereavement-fare refund policy that never existed; a Chevrolet dealership bot was manipulated via prompt injection into "agreeing" to sell a $60,000 SUV for $1; an NYC government chatbot advised small businesses to break local housing law. In fintech specifically, the stakes are sharper — fabricated eligibility rules, regulatory misstatements, or fraud-facilitation responses carry direct financial and compliance consequences.

Aegis AI treats trust and safety as a continuous, measurable property of a deployed fintech LLM application — not a one-time manual review — by combining **provenance verification** with **automated, multi-turn red-teaming** to produce an explainable Trust & Safety Certificate before deployment.

---

## 2. Proposed Solution

Aegis AI is a **black-box evaluation platform** that connects to any target chatbot — via a live API endpoint or a locally-run/hosted HuggingFace model — and runs it through two complementary evaluation tracks:

1. **Provenance / Identity Engine** — a lightweight, rule-based scorer that evaluates whether the target's base model, data sources, and system prompt configuration are documented and transparent, producing an **Identity Score**.
2. **Sentinel Red-Teaming Engine** — an automated attack-and-judge loop that executes single-turn and scripted multi-turn adversarial prompts across jailbreak, injection, bias, hallucination, and domain-specific fraud/misuse categories, each independently scored by a judge model decoupled from the target's own infrastructure.

The platform's core research question — and its main differentiator from every prior tool and paper — is whether these two tracks are **connected**: does a poorly-documented application (weak provenance) actually correlate with worse behavioral safety outcomes? No existing benchmark, open-source scanner, or published paper tests this relationship, because none of them measure provenance at all.

Results from both tracks are aggregated into a numeric **Trust Score** and an explainable **Trust & Safety Certificate** — category breakdowns, representative failure transcripts, and mitigation recommendations — generated asynchronously so the user never has to wait on-screen for a full evaluation to complete.

---

## 3. Objectives

1. Design a provenance and identity scoring engine that evaluates the transparency of an LLM application's base model, data sources, and system configuration.
2. Build an automated red-teaming (Sentinel) engine executing single-turn and multi-turn adversarial test suites across jailbreak, injection, bias, hallucination, and domain-specific (fintech) misuse categories.
3. Develop an independent LLM-judge scoring pipeline and an explainable Trust & Safety Certificate that quantifies and communicates evaluation results.
4. Investigate whether conversational risk accumulates predictably across turns, and whether provenance quality correlates with measurable safety outcomes.
5. Extend evaluation into agentic pipelines via an optional trace mode, quantifying failures that black-box output judging alone would miss (Cascade Masking Rate).
6. Explore a self-improving attacker model (rejection-sampling + LoRA fine-tuning) that adapts round-over-round against a given target, rather than relying on a static, quickly-stale prompt list.

---

## 4. Scope

- Universal Target Connector — connect to any LLM-powered chatbot via HTTP API, or a locally-run / hosted HuggingFace model, through one shared interface.
- Three connector modes: **hosted** (Aegis calls the target directly), **agent** (a lightweight connector runs inside the target owner's own infrastructure, keeping credentials off Aegis's servers), and **local HF** (direct model loading for open-weight targets).
- Lightweight Provenance Engine — captures and scores base model, data sources, and system prompt documentation into an Identity Score.
- Automated Multi-turn Red-Teaming — single-turn and scripted multi-turn adversarial conversations across jailbreak, injection, RAG-corpus poisoning, bias, leakage, hallucination, and fintech-specific misuse (fraud facilitation, regulatory misstatement, eligibility gaming).
- Independent Judge & Scoring Pipeline — a dedicated judge model, decoupled from the target's own API quota, using role-specific rubrics mapped to OWASP LLM Top 10 categories.
- Asynchronous, Resumable Job Execution — every test result persisted immediately; jobs survive target rate-limits, quota errors, and crashes without losing progress.
- Optional Agent-Trace Evaluation — judges each stage of an agentic pipeline (Ingestion / Orchestration / Tool Execution) individually when the target exposes intermediate outputs.
- Explainable Trust & Safety Certificate — numeric scores, category breakdowns, failure transcripts, mitigation suggestions, with masking of sensitive endpoint/credential details on export.
- Scoped to one primary target application (a fintech-adjacent RAG chatbot, e.g. a government welfare-scheme bot) plus a small comparative set of API and HuggingFace-hosted models for the MVP, using open benchmark datasets and self-built target applications.
- **Out of scope:** model-internals/interpretability analysis, training target models from scratch, always-on production runtime monitoring (this is pre-deployment evaluation, not a live guardrail), and exhaustive coverage of every possible attack category in year one.

---

## 5. Mapping with SDG

**Goal 16: Peace, Justice and Strong Institutions**
*"Build effective, accountable and transparent institutions at all levels."*

Project contributes as:
- Providing an independent verification layer for AI systems that mediate citizen and consumer access to financial services, supporting institutional accountability and transparency.
- Detecting fraudulent, biased, or fabricated responses in AI-driven fintech applications before deployment, reducing risk to end users.
- Establishing a quantifiable Trust Score and certification process organizations can adopt as part of responsible AI deployment.
- Extending trust and accountability principles from institutions to the AI infrastructure they increasingly depend on.

**Secondary alignment:** Goal 9 (resilient, safety-verified AI infrastructure), Goal 10 (bias detection reducing inequality of AI-mediated financial access).

---

## 6. Unique Selling Points (USP) — What Aegis Does Differently

### Against open-source tools (Garak, Promptfoo, DeepEval)
| They do | Aegis adds |
|---|---|
| Test model behavior against static/semi-static attack lists | Combines behavioral testing with **provenance scoring**, testing whether documentation quality predicts actual safety |
| Single-turn scanning | Scripted **multi-turn sessions** — Session Harm Rate tracks risk invisible to one-shot testing |
| Score the final output only | Optional **agent-trace mode** — catches mid-pipeline failures masked by a fluent final answer (Cascade Masking Rate) |
| Fixed rule-based or static prompt sets | A **self-improving attacker** (rejection sampling + LoRA) that adapts round-over-round instead of going stale |

### Against research papers (S-Eval, HarmBench, JailbreakBench, BBQ, CoRT, FinRED, FinSafetyBench)
| They do | Aegis adds |
|---|---|
| Evaluate the model in isolation | Evaluates the **deployed application** — model + data sources + system prompt together |
| Single-turn, or multi-turn with no provenance link (CoRT) | Explicitly tests whether **provenance correlates with safety outcomes** — a question none of these ask |
| A one-time benchmark or attack-technique contribution | A **continuous, resumable evaluation platform** designed to be re-run every time an app changes |
| Fintech-specific but not agent-pipeline-aware | Adds **agent-trace evaluation** for RAG/multi-agent fintech pipelines these papers don't look inside |

### Against peer-reviewed governance/scanner papers (Lu et al., IEEE; Regmi & Saravanan, Springer)
| They do | Aegis adds |
|---|---|
| Lu et al.: a responsible-AI **pattern catalogue** (manual guidance) | Aegis **operationalizes** these patterns as automated, repeatable tests |
| Regmi & Saravanan: a classifier scanner for injection/jailbreak only | Aegis's judge covers this as one category among provenance, bias, hallucination, session-risk, and agent-trace |

**Core thesis:** No existing tool or paper combines (1) provenance verification, (2) multi-turn session-risk tracking, (3) agent-trace evaluation, and (4) an adaptive attacker. Aegis's contribution is testing whether these are *connected* — does poor provenance predict poor safety? Does single-turn safety predict multi-turn safety? — which no cited prior work investigates.

---

## 7. Technical Stack

**Backend**
- FastAPI — async API framework orchestrating connectors, jobs, and evaluation pipelines
- httpx — async HTTP client for calling target chatbot endpoints
- transformers + peft (LoRA) + bitsandbytes — loading, running, and fine-tuning local/quantized HuggingFace models, including the attacker model
- tenacity — exponential backoff and adaptive rate-limit / hard-block handling

**Frontend**
- Next.js 14 / React — dashboard, connector forms, certificate visualization, agent-trace drill-down
- Tailwind CSS — responsive UI components
- Recharts — category breakdowns, trust score trends, per-agent trace views

**Data & Storage**
- PostgreSQL (Neon.tech) — resumable, checkpointed storage of every test result, trace step, and certificate
- HuggingFace `datasets` — AdvBench, JailbreakBench, BBQ benchmark pools

**Evaluation & Judging**
- Groq-hosted or local Llama-Guard — independent judge model, decoupled from target quota
- Custom rubric-based prompts — category-specific judging (safety, bias, grounding, injection), mapped to OWASP LLM Top 10 IDs

**Adaptive Attacker (stretch scope)**
- Mistral-7B-Instruct-v0.3 (Apache 2.0) — base attacker model, selected for willingness to follow adversarial-generation instructions
- LoRA fine-tuning via `peft` — lightweight, rejection-sampling based round-over-round adaptation, runnable on a single free-tier GPU (Colab T4)

**Deployment / Compute**
- HuggingFace Inference Endpoints (default, avoids local GPU dependency), with Colab / on-demand GPU rental as fallback for local model runs

---

## 8. System Architecture

**Layer 1 — Presentation:** Next.js dashboard, connector/target submission form, job status view, certificate visualization, agent-trace drill-down.

**Layer 2 — API & Orchestration:** FastAPI backend — validates and creates jobs, coordinates hosted/agent/local-HF connector modes, enforces SSRF validation, consent gating, and rate-limit policy before any request is dispatched.

**Layer 3 — Connector Layer (three interchangeable modes):**
- API connector (httpx, async) — hosted-mode, direct calls to a live endpoint
- HuggingFace connector (transformers / HF Inference Endpoints) — local or hosted model targets
- Agent connector — a lightweight polling agent run inside the target owner's own infrastructure, so credentials and raw traffic never leave their network

**Layer 4 — Evaluation Core (the "brain" of the system):**
- **Job Scheduler** — selects the next prompt or turn from the combined benchmark + domain pool, skipping already-completed items (enables resumability)
- **Session Controller** — holds multi-turn conversation state, decides when a scripted session escalates or ends
- **Execution Dispatcher** — routes the prompt to the correct connector, applying backoff / hard-block detection
- **Judge Router** — selects the category-specific rubric and routes the (prompt, response) pair to the judge model
- **Provenance/Identity Engine** — rule-based scorer, runs once per target
- **Agent-Trace Evaluator** (optional) — judges each pipeline stage individually when a target exposes intermediate outputs

**Layer 5 — Judge & Scoring:** independent judge model (Groq / local Llama-Guard), role-specific rubrics per category and per agent-trace stage.

**Layer 6 — Persistence:** PostgreSQL — `jobs`, `test_results`, `trace_results`, `provenance`, `certificates` tables; every individual result written immediately, not batched.

**Layer 7 — Certificate & Reporting:** aggregates persisted results into Trust Score, Identity Score, Attack Effectiveness Rate (AER), Session Harm Rate, and Cascade Masking Rate; generates the exportable, credential-masked certificate.

**Cross-cutting — Security & Trust:** SSRF-safe target validation, encrypted credential storage, per-user access-scoped jobs/certificates, adaptive backoff distinguishing rate-limits from hard blocks, agent-mode trust boundary, server-enforced target allow-listing for any adaptive attack generation.

---

## 9. Workflow — End to End

1. **Connect a target** — user submits an endpoint URL (or HF model repo), selects connector mode (hosted / agent / local HF), confirms ownership/authorization, and chooses quick mode (fast sanity check, ~2 min) or full certificate (complete evaluation, background job).
2. **Job created, user walks away** — the job is queued asynchronously; no need to stay on screen for the 40–90 minute full run.
3. **Provenance scoring runs once** — base model, data sources, and system prompt documentation are evaluated into an Identity Score.
4. **Sentinel loop begins:**
   - Job Scheduler pulls the next test case from the benchmark + domain pool
   - Session Controller determines single-turn or multi-turn context
   - Execution Dispatcher sends the prompt via the appropriate connector, backing off automatically on rate limits and halting (not retrying) on hard blocks
   - Response returns; Judge Router selects the matching rubric and scores it
   - Result is written immediately to the database (resumable checkpoint)
   - Loop repeats until the pool is exhausted
5. **(Optional) Agent-trace evaluation** — if the target exposes intermediate pipeline steps, each stage is judged individually, computing the Cascade Masking Rate.
6. **Aggregation** — Trust Score, AER, Session Harm Rate, Identity Score, and (if applicable) Cascade Masking Rate are computed from persisted results.
7. **Certificate generated and user notified** — dashboard shows category breakdowns, representative failure transcripts, and mitigation suggestions; sensitive endpoint/credential data is masked in exported views.

---

## 10. Security and Trust Model

- **Platform security:** SSRF-safe target URL validation (blocks private/internal IP ranges), encrypted credential storage, per-request timeouts and response size limits, per-user access-scoped jobs and certificates.
- **Operator trust (Aegis's own trustworthiness):** minimum-necessary access (query-only, never state-changing), full transparency of stored prompts/responses to the target owner, scoped and revocable credentials, explicit consent confirmation at every submission, agent-mode as a self-hosted option for users unwilling to share raw traffic with a third party.
- **Rate-limit vs. hard-block handling:** exponential backoff for transient 429s; automatic halt (not retry) on detected blocks (403 / bot-detection), flagged for manual review rather than evaded.
- **Adaptive attacker guardrails:** server-enforced target allow-listing (the attack-generation loop cannot call an unverified URL), per-engagement audit logs, weights never exported or published as a standalone artifact.
- **Industry standards alignment:** test categories mapped to OWASP Top 10 for LLM Applications (e.g., Prompt Injection = LLM01, Excessive Agency = LLM03); agent-trace stages mapped to the Ingestion / Orchestration / Tool Execution model used in MITRE ATLAS-aligned red-teaming practice.

---

## 11. Literature Survey

| Paper / Source | Year | Venue | Key Finding |
|---|---|---|---|
| Developing Responsible Chatbots for Financial Services (Lu et al.) | 2023 | IEEE Intelligent Systems | Pattern-oriented responsible-AI catalogue for financial chatbots; Aegis operationalizes this as automated testing |
| Securing LLM-Integrated Chatbots: Transformer-Based Vulnerability Scanner (Regmi & Saravanan) | 2026 | Springer, SecITC | Classifier-based injection/jailbreak scanner (97% accuracy with ELECTRA); informs Aegis's judge design |
| A Survey of Safety and Trustworthiness of LLMs (V&V lens) | 2024 | Springer, AI Review | Peer-reviewed survey anchoring Aegis's overall trust-evaluation framing |
| Learning to Conceal Risk: Controllable Multi-turn Red Teaming in Finance (Cheng et al.) | 2025 | arXiv (ACL'26) | Multi-turn regulatory-risk-concealment attacks in finance; closest existing match to Aegis's session-risk research angle |
| FinRED: Expert-Guided Benchmark Generation for Financial LLM Red-Teaming (Kim et al.) | 2026 | arXiv | Regulatory-standard-mapped threat taxonomy (FATF, EU DORA); informs Aegis's domain-pool design |
| FinSafetyBench | 2026 | arXiv | 14-subcategory financial compliance refusal benchmark; candidate domain-pool source |
| S-Eval (Yuan et al.) | 2024 | arXiv | Adaptive, taxonomy-guided test generation; informs benchmark-pool sampling |
| HarmBench (Mazeika et al.) | 2024 | arXiv | Standardized generate→complete→evaluate red-teaming pipeline; basis for Sentinel's architecture |
| JailbreakBench (Chao et al.) | 2024 | arXiv | Open, reproducible jailbreak benchmark with public leaderboard |
| BBQ (Parrish et al.) | 2022 | arXiv | Nine-dimension social bias benchmark |
| Indirect Prompt Injection (Greshake et al.) | 2023 | arXiv | Introduces attacks embedded in retrieved content; motivates RAG-poisoning tests |

---

## 12. Gaps in Existing Research / Solutions

**Gap 1 — No Provenance Awareness:** Existing benchmarks and scanners evaluate model behavior in isolation, with no check on whether the deployed application's data sources or configuration are documented.
→ *Aegis:* Introduces an Identity/Provenance score and tests its correlation with actual safety outcomes.

**Gap 2 — Single-Turn Evaluation Bias:** Most red-teaming frameworks test one-shot prompts; even fintech-specific multi-turn work (CoRT) doesn't connect risk to provenance.
→ *Aegis:* Runs scripted multi-turn sessions and computes a Session Harm Rate distinct from single-turn scores.

**Gap 3 — No Visibility into Agentic Pipelines:** Black-box evaluation judges only the final output, missing failures a fluent final answer can mask.
→ *Aegis:* Optional trace-level judging per agent step, quantified via a Cascade Masking Rate.

**Gap 4 — Domain-Blind Benchmarks:** Generic jailbreak/bias datasets don't cover fintech-specific misuse (eligibility gaming, regulatory misstatement, fraud facilitation).
→ *Aegis:* Combines generic benchmark pools with a curated, fintech-specific domain pool.

**Gap 5 — Static Attack Sets:** Open-source scanners (Garak, Promptfoo) and academic benchmarks rely on fixed prompt lists that go stale as target models patch known tricks.
→ *Aegis:* A rejection-sampling, LoRA-fine-tuned attacker that adapts round-over-round against a specific target.
