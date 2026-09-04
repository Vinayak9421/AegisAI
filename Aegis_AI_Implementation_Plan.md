# Aegis AI — Detailed Implementation Plan

**Team (Div B):** Vivek Maurya (104), Vedant Mallya (101), Vinayak Mishra (115), Mihir Mehta (105)
**Guide:** Prof. Harshada Sonkamble
**Duration:** 1 academic year (FYP), split across two semesters

---

## 1. Development Philosophy

Build in this order of priority so that, whatever gets cut for time, the core deliverable still stands:

1. **Must-have (core FYP deliverable):** Provenance Engine + Sentinel Red-Teaming Engine + Judge Pipeline + async resumable jobs + basic dashboard + certificate generation, demonstrated on one self-built target (fintech-adjacent RAG bot).
2. **Should-have (strengthens research contribution):** Multi-turn session testing, OWASP-category mapping, agent-trace evaluation mode, comparative evaluation across 2–3 targets.
3. **Nice-to-have (stretch, build only if time remains):** Agent-mode (self-hosted connector), adaptive/self-improving attacker (rejection sampling + LoRA).

Never let a should-have or nice-to-have block finishing a must-have. Scope down, don't skip the foundation.

---

## 2. High-Level Timeline (12 months)

| Phase | Months | Focus |
|---|---|---|
| Phase 0 — Setup & Research | 1–2 | Literature survey finalized, tech stack setup, provenance engine + connector architecture |
| Phase 1 — Core Engine Build | 3–6 | Sentinel red-teaming engine, judge pipeline, multi-turn scripting, database schema |
| Phase 2 — Evaluation Runs | 7–8 | Run full evaluations across target apps, collect data, debug pipeline issues |
| Phase 3 — Analysis & Extensions | 9–10 | Provenance–safety correlation analysis, agent-trace mode, certificate generator polish |
| Phase 4 — Stretch Goals | 10–11 | Agent-mode connector, adaptive attacker (only if ahead of schedule) |
| Phase 5 — Report & Demo Prep | 11–12 | Report writing, paper draft, panel demo rehearsal, buffer |

---

## 3. Phase-by-Phase Breakdown

### Phase 0 — Setup & Research (Months 1–2)

**Week 1–2: Literature and dataset survey**
- Finalize literature survey table (S-Eval, HarmBench, JailbreakBench, BBQ, CoRT, FinRED, FinSafetyBench, Lu et al., Regmi & Saravanan)
- Confirm current HuggingFace dataset repo IDs for AdvBench, JailbreakBench, BBQ
- Identify/confirm the self-built target application (fintech-adjacent RAG bot) to be used as the primary evaluation target

**Week 3–4: Environment and repo setup**
- Initialize FastAPI backend repo, Next.js frontend repo
- Set up PostgreSQL on Neon.tech; design initial schema (`jobs`, `test_results`, `provenance`)
- Set up separate API keys: one for the target app (production-safe), one for Aegis's own testing/judge traffic

**Week 5–6: Connector architecture**
- Build the API connector (httpx, async) — single shared interface for `{message, session_id, history} → {reply}`
- Build target URL validation (SSRF protection): block private/internal IP ranges, resolve hostnames before validating, enforce timeouts and response-size limits

**Week 7–8: Provenance Engine (lightweight, build early since it's low-effort)**
- Define the metadata schema: base model, data sources, system prompt documentation
- Build the rule-based scorer → Identity Score (0–100)
- Build a simple metadata-entry form (can be manual input at MVP stage, not auto-detected)

**Milestone check (end of Month 2):** Connector can call a target and get a reply; provenance scorer produces a number from manually-entered metadata; SSRF validation blocks a private IP test case.

---

### Phase 1 — Core Engine Build (Months 3–6)

**Week 9–10: Benchmark + domain pool**
- Pull and sample AdvBench, JailbreakBench, BBQ via `datasets` library
- Author 30–50 seed domain-pool prompts (fintech misuse: eligibility gaming, fraud facilitation, regulatory misstatement, hallucinated scheme/product details)
- Expand seed prompts via LLM-assisted variation (GPT-4o/Gemini), manually review a sample for quality

**Week 11–12: Test case schema and job queue**
- Finalize `test_results` schema: `id, job_id, prompt_id, category, turn_number, session_id, target_response, judge_verdict, severity, owasp_category`
- Build the Job Scheduler: pulls next incomplete test case for a job, skips already-completed ones (resumability foundation)

**Week 13–15: Judge pipeline**
- Set up judge model (Groq-hosted Llama-Guard or local, kept separate from target's API quota)
- Write category-specific rubric prompts (jailbreak, injection, bias, hallucination, fraud facilitation)
- Map each category to an OWASP LLM Top 10 ID
- Validate judge accuracy: hand-label ~100 responses, compare against judge output, compute agreement rate

**Week 16–18: Execution Dispatcher + rate-limit handling**
- Implement `tenacity`-based exponential backoff for 429 responses
- Implement hard-block detection (403 / bot-detection signatures) — halt and flag, do not retry
- Implement request throttling (self-imposed conservative rate cap for targets with unknown limits)

**Week 19–20: Multi-turn Session Controller**
- Design 20–30 pre-scripted multi-turn conversation trees (3–5 turns each), escalating gradually toward the actual test intent
- Build session state tracking: `session_id`, `turn_number`, maintains conversation history across calls
- Compute Session Harm Rate: % of sessions where risk crossed threshold by final turn despite clean early turns

**Week 21–22: Async job execution**
- Move job execution to FastAPI `BackgroundTasks` (or Celery + Redis if time allows)
- Build job status polling endpoint; frontend shows progress (`X / N prompts complete`)
- Ensure every individual result commits to the database immediately, not batched

**Milestone check (end of Month 6):** Full single-turn and multi-turn evaluation run completes end-to-end against the self-built target, asynchronously, with resumable checkpointing verified by deliberately interrupting a run and resuming it.

---

### Phase 2 — Evaluation Runs (Months 7–8)

**Week 23–26:**
- Run full evaluations (300–500 prompts) against the primary target
- Debug pipeline issues surfaced by real runs: judge rubric misfires, rate-limit tuning, session-scripting adjustments
- Add a second and third comparative target (e.g., a direct Gemini/GPT API-wrapped bot, and one HuggingFace-hosted model) for comparative results

**Week 27–28:**
- Aggregate results into Trust Score, AER, Session Harm Rate, Identity Score per target
- Cross-check judge accuracy again on the real evaluation data (not just the earlier hand-labeled sample)

**Milestone check (end of Month 8):** Clean, complete evaluation data collected across at least 3 targets, ready for analysis.

---

### Phase 3 — Analysis & Extensions (Months 9–10)

**Week 29–30: Provenance–safety correlation analysis**
- Compute correlation between Identity Score and AER / Session Harm Rate across all evaluated targets
- Document findings — this is the platform's core research contribution

**Week 31–33: Agent-trace evaluation (should-have)**
- Add a `trace` field to the self-built target's API response (retriever / reasoner / formatter steps)
- Build role-specific judge rubrics per agent step
- Compute Cascade Masking Rate: % of intermediate failures invisible to black-box judging alone
- Add `trace_results` table, linked to `test_results`

**Week 34–36: Certificate generator + dashboard polish**
- Build the full Trust & Safety Certificate view: score cards, category breakdown bars, failure-transcript drill-down
- Implement credential/endpoint masking on certificate export
- Build "quick mode" (30–50 prompt sample, <5 min) alongside full-run mode

**Milestone check (end of Month 10):** Correlation analysis complete with a documented finding; agent-trace mode demoable on the primary target; certificate dashboard fully functional.

---

### Phase 4 — Stretch Goals (Months 10–11, only if ahead of schedule)

**Agent-mode connector (self-hosted, ~1–2 weeks)**
- Build a minimal (~100–150 line) polling agent script: poll for job → call local target → report result
- Add agent-token issuance/revocation on the backend
- Demo once, live, against the primary target — does not need production hardening (token rotation, offline queuing are explicitly out of scope, documented as future work)

**Adaptive attacker (rejection sampling + LoRA, ~2–3 weeks)**
- Load Mistral-7B-Instruct-v0.3 via `transformers`, 4-bit quantized (Colab T4 or equivalent)
- Generate a batch of candidate adversarial prompts against the primary target
- Filter to successful (`COMPROMISED`-verdict) prompts via the existing judge pipeline
- LoRA fine-tune (via `peft`) on the filtered successful prompts
- Run 2–3 rounds; chart attack success rate improving round-over-round
- Enforce server-side target allow-listing so the attacker can only ever call verified, owned targets

**If time does not allow full implementation:** describe both in the report as designed-but-not-fully-built, with the design rationale and guardrails documented — this is an acceptable, honest scope decision (see Section 5).

---

### Phase 5 — Report & Demo Prep (Months 11–12)

- Finalize project report, research paper draft (if targeting publication/submission)
- Prepare the panel demo: architecture diagram walkthrough → live "quick mode" run (2–3 min) → pre-generated full certificate walkthrough → provenance-correlation finding → live single-prompt replay for Q&A
- Rehearse handling of live-demo edge cases (target rate-limited, quota reached) using the error-state UI already designed
- Buffer week for unexpected issues

---

## 4. Team Role Split (suggested)

| Member | Primary responsibility |
|---|---|
| Vivek Maurya | Sentinel engine (Job Scheduler, Session Controller, Execution Dispatcher), multi-turn scripting |
| Vedant Mallya | Judge pipeline, rubric design, OWASP mapping, provenance–safety correlation analysis |
| Vinayak Mishra | Backend infrastructure — FastAPI, database schema, async job queue, SSRF/security layer |
| Mihir Mehta | Frontend — Next.js dashboard, connector forms, certificate visualization, agent-trace drill-down |

Provenance Engine, benchmark/domain pool curation, and report writing are shared responsibilities across all four members. Adjust based on individual strengths — this split is a starting point, not a rigid assignment.

---

## 5. Risk Register and Mitigations

| Risk | Mitigation |
|---|---|
| Quota exhaustion (target or judge API) | Separate API keys for target vs. judge traffic; rotate across team members' free-tier keys if needed; cache responses during debug cycles |
| Target rate-limiting / hard blocks | Adaptive backoff for 429s; automatic halt (not retry) on detected blocks; self-imposed conservative request budget for unknown-capacity targets |
| Judge accuracy / false positives | Hand-label a validation sample early (Week 15) and re-validate after real runs (Week 27); treat judge tuning as its own workstream |
| Scope creep (agent-mode, adaptive attacker) | Explicitly gated as Phase 4 stretch goals — only attempted if Phases 0–3 finish on schedule; describable-but-not-built is an acceptable fallback |
| GPU/compute access for HF models and attacker fine-tuning | Default to HuggingFace Inference Endpoints (no GPU needed); Colab free-tier T4 as fallback for local runs; LoRA (not full fine-tuning) keeps attacker training within free-tier compute |
| Demo timing (full run takes 40–90 min) | Async job architecture — never demoed live in full; "quick mode" (<3 min) proves the pipeline live; full certificate pre-generated before the panel session |
| Third-party endpoint permission concerns | Evaluation scope limited to self-built targets and direct API-key-based calls (Gemini/GPT/Claude); no third-party production systems tested without explicit authorization |

---

## 6. Deliverables Checklist

- [ ] Working Provenance Engine producing an Identity Score from target metadata
- [ ] Working Sentinel engine executing single-turn and multi-turn adversarial tests
- [ ] Independent judge pipeline with rubric-per-category, validated against hand-labeled data
- [ ] Async, resumable job execution with checkpointed database persistence
- [ ] Dashboard with connector form, job status, and Trust & Safety Certificate view
- [ ] Full evaluation runs completed across at least 3 comparative targets
- [ ] Provenance–safety correlation analysis with a documented finding
- [ ] Agent-trace evaluation mode demoable on the primary target
- [ ] (Stretch) Agent-mode self-hosted connector, demoed once live
- [ ] (Stretch) Adaptive attacker with round-over-round improvement chart
- [ ] Final project report, including SDG mapping, literature survey, gap analysis, and security/trust model documentation
- [ ] Panel demo rehearsed with error-state handling and live single-prompt replay ready for Q&A
