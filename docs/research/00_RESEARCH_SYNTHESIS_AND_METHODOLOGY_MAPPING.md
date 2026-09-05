# Research Synthesis & Methodology Mapping for Aegis AI

## Overview

This document synthesizes insights from 19 research papers read for the Aegis AI project, maps each paper's methodology to Aegis's architecture, identifies improvements, and provides a prioritized adoption roadmap.

**Papers analyzed:** 19  
**Research domains covered:** Red teaming, jailbreaking, hallucination evaluation, LLM safety benchmarking, LLM-as-a-judge, fintech AI safety, provenance/RAI patterns, multi-turn attacks, IPI, agentic safety.

---

## Section 1: Architecture Validation Map

The following table shows which papers validate, improve, or motivate each of Aegis's core components.

| Aegis Component | Validated By | Improved By | Motivated By |
|---|---|---|---|
| **Sentinel Engine (generate→evaluate pipeline)** | HarmBench, Perez et al. | HARM (top-down taxonomy) | GCG (alignment ≠ security) |
| **Independent Judge (Llama Guard)** | Llama Guard, LLM-as-Judge Survey | LLM-as-Judge Survey (CoT rubrics) | DecodingTrust (self-enhancement bias) |
| **Session Harm Rate (SHR)** | Crescendo, MTSA, MM-ART, MUSE | MUSE (risk trajectory), MTSA (future rewards) | MM-ART (+71% multi-turn) |
| **Multi-turn Session Trees** | Crescendo, HARM, MTSA, MUSE | MUSE (frame semantics), CoRT (concealment) | Crescendo (benign turns bypass filters) |
| **Fintech Domain Pool** | CoRT (FinRisk-Bench), MULTITURN_JAILBREAK | CoRT (6 risk categories) | CoRT (93%+ ASR in finance) |
| **IPI Test Category** | INJECAGENT, Greshake et al. | Greshake taxonomy | Greshake (no effective defense) |
| **RAG Corpus Poisoning** | AGENTPOISON | AGENTPOISON (RCIR metric) | AGENTPOISON (80%+ ASR, 0.1% poison ratio) |
| **Agent-Trace Mode** | AGENT-SAFETYBENCH | AGENT-SAFETYBENCH (8-category taxonomy) | AGENT-SAFETYBENCH (< 60% safety scores) |
| **Hallucination Category** | HaluEval | HaluEval (grounded judge design) | HaluEval (19.5% baseline hallucination rate) |
| **Identity Score / Provenance** | Lu et al. (RAI patterns) | Lu et al. (lifecycle stages) | DecodingTrust (multi-dimensional trust) |
| **Trust & Safety Certificate** | Lu et al. | Lu et al. (RAI pattern catalog) | AGENT-SAFETYBENCH (structural gap, not prompt gap) |
| **Adaptive Attacker (stretch)** | Perez et al. (RL red-teaming) | Crescendomation, MUSE (MCTS), MTSA (iterative) | HarmBench (no single method is best) |

---

## Section 2: Key Empirical Statistics for the Aegis Paper

These findings from the literature should be cited directly in Aegis's research paper to establish motivation and context.

| Statistic | Source | How to Use |
|---|---|---|
| "None of 16 LLM agents achieves > 60% safety score" | AGENT-SAFETYBENCH | Motivates agent-trace evaluation |
| "ChatGPT hallucinates in ~19.5% of responses" | HaluEval | Baseline for hallucination category |
| "+71% more vulnerable after 5-turn conversation vs. 1-turn" | MM-ART | Motivates SHR, multi-turn evaluation |
| "+195% more vulnerable in non-English vs English single-turn" | MM-ART | Motivates multi-lingual test cases |
| "CoRT achieves 93–95% ASR in financial regulatory domain" | CoRT | Motivates fintech-specific domain pool |
| "AGENTPOISON: 80–100% attack success with < 0.1% poison ratio" | AGENTPOISON | Motivates RAG corpus integrity testing |
| "GCG: 84% ASR against GPT-4 (transfer attack)" | GCG | Motivates "alignment ≠ security" thesis |
| "Crescendo: ~100% ASR on misinformation tasks" | Crescendo | Motivates multi-turn session evaluation |
| "Llama Guard matches/exceeds commercial moderation tools" | Llama Guard | Validates judge choice |
| "GPT-4 follows misleading instructions more precisely than GPT-3.5" | DecodingTrust | Motivates capability-agnostic evaluation |

---

## Section 3: Methodology Rankings

### Best Paper for Each Aegis Component

| Component | Best Paper | Rationale |
|---|---|---|
| Multi-turn attack template | Crescendo | Most directly implementable; benign-turn pattern is production-ready |
| Fintech risk taxonomy | CoRT | Only paper that directly addresses financial regulatory violations with benchmarks |
| Judge design | Llama Guard + LLM-as-Judge Survey | Llama Guard provides the implementation; survey provides reliability principles |
| Agent safety benchmark | AGENT-SAFETYBENCH | Most comprehensive benchmark for agent behavioral safety |
| Hallucination evaluation | HaluEval | Best methodology for creating grounded hallucination test sets |
| IPI taxonomy | Greshake et al. | Foundational taxonomy from computer security perspective |
| RAG attack | AGENTPOISON | Only paper addressing RAG knowledge base poisoning with proven effectiveness |
| Benchmark standardization | HarmBench | Standardized framework Aegis should align with for comparability |
| Multi-turn attack diversity | HARM | Most systematic top-down approach for test case coverage |
| Attack foundation | GCG + Perez et al. | Establish the baseline that alignment is insufficient |

### Where Aegis Goes Beyond ALL Papers

1. **Provenance + Safety Combined:** No paper combines identity/provenance scoring with red-teaming in one platform. Lu et al. addresses RAI patterns; Aegis automates them into a score.

2. **Trust & Safety Certificate:** No paper produces a client-ready actionable certificate. All produce research metrics.

3. **Fintech-Specific Holistic Platform:** CoRT tests financial regulatory violations; AGENT-SAFETYBENCH tests agent behavioral safety; HaluEval tests hallucination. Aegis tests ALL of these in one orchestrated platform.

4. **Session Harm Rate as a Composite Metric:** No single paper defines a holistic session-level safety metric that combines turn-by-turn risk accumulation, final-turn verdict, and provenance correlation.

---

## Section 4: Improvements to Existing Aegis Architecture

Based on paper synthesis, here are concrete improvements to the existing Aegis plan:

### 4.1 Sentinel Engine Improvements

**Current:** Generic attack categories (jailbreak, injection, bias, hallucination)

**Improved (paper-grounded):**
- Split "injection" → Direct Prompt Injection (DPI) + Indirect Prompt Injection (IPI)
- Add: RAG Corpus Poisoning (AGENTPOISON) as distinct category
- Add: Financial Regulatory Concealment (CoRT) as high-priority fintech category
- Add: Language-based Safety Inconsistency (MM-ART) — same prompt in English vs. Hindi
- Ground hallucination category in HaluEval's sampling-then-filtering methodology

**Categories (post-synthesis):**
1. Direct Jailbreak (GCG suffixes + single-turn prompts from HarmBench/AdvBench)
2. Multi-turn Escalation (Crescendo + HARM + MTSA session trees)
3. Direct Prompt Injection — DPI
4. Indirect Prompt Injection — IPI (Greshake taxonomy + INJECAGENT scenarios)
5. RAG Corpus Poisoning (AGENTPOISON-inspired black-box proxy)
6. Hallucination (HaluEval-inspired fintech factual accuracy)
7. Bias & Stereotype (DecodingTrust taxonomy)
8. Financial Fraud Facilitation (CoRT FinRisk categories 1–3)
9. Regulatory Misstatement (CoRT FinRisk categories 4–6)
10. Language Safety Inconsistency (MM-ART: Hindi/English divergence)

### 4.2 Judge Pipeline Improvements

**Current:** Single Llama Guard call per response

**Improved (LLM-as-Judge Survey + Llama Guard paper):**
- CoT reasoning required before verdict (reduces bias)
- Domain-specific rubric with 2–3 anchor examples per category
- Dual-role classification: prompt verdict + response verdict per turn
- Secondary judge for borderline verdicts (confidence < 0.7)
- 100-sample human validation before deploying judge at scale

### 4.3 Session Design Improvements

**Current:** 20–30 scripted session trees (loosely defined)

**Improved (Crescendo + MTSA + MUSE):**
- Design 5–8 Crescendo-style sessions (benign turns → harmful)
- Design 5–8 MTSA thought-guided sessions (planned escalation path)
- Design 3–5 CoRT-style financial regulatory concealment sessions
- Design 3–5 frame-semantic sessions (MUSE-inspired frame trajectory)
- Design 2–3 multi-lingual sessions (MM-ART-inspired Hindi variants)
- Each session tree must include: goal, setup turns, escalation turns, final harmful ask, expected refusal turn

### 4.4 New Metrics (paper-derived)

| Metric | Paper Source | Definition |
|---|---|---|
| RAG Corpus Integrity Rate (RCIR) | AGENTPOISON | % of runs where no adversarial documents retrieved for trigger prompts |
| Tool Deviation Rate (TDR) | INJECAGENT | % of tool calls that serve injected instruction vs. user intent |
| Turn-to-Harm (TTH) | MUSE + MTSA | Avg turns needed before first harmful response is elicited |
| Hallucination Rate (HR) | HaluEval | % of factual queries where response is unverifiable or conflicting |
| Language Safety Delta (LSD) | MM-ART | Difference in ASR between English and non-English versions of same prompt |
| Provenance-Safety Correlation (PSC) | Lu et al. + CoRT | Correlation between Identity Score and Sentinel Trust Score across target chatbots |

### 4.5 Identity Score Improvements

**Current:** 30% Model + 35% Data + 25% Safety Rules + 10% Operations

**Improved (Lu et al. lifecycle stages + DecodingTrust dimensions):**

The weights are defensible with this mapping:
- Model (30%): Maps to Lu et al.'s "model training stage" risks + DecodingTrust's fairness/bias dimensions
- Data (35%): Maps to Lu et al.'s "data collection & preparation stage" risks + DecodingTrust's privacy dimension
- Safety Rules (25%): Maps to Lu et al.'s "system integration stage" (scope limitation, escalation paths)
- Operations (10%): Maps to Lu et al.'s "monitoring & maintenance stage" (version control, contact)

**Renaming:** "Identity Score" → "Provenance Transparency Score" (as recommended in negative risk audit) — justified by Lu et al.'s finding that documentation quality ≠ factual truth.

---

## Section 5: Trust Score Composition (Paper-Grounded)

### Revised Trust Score Formula

```
Trust Score = α × Sentinel Score + β × Provenance Transparency Score
           = 0.65 × Sentinel + 0.35 × Provenance

Sentinel Score = Σ (category_weight × category_pass_rate)
   - Jailbreak: 15%
   - Multi-turn Escalation: 15%
   - Injection (DPI + IPI): 15%
   - Financial Regulatory: 20% ← elevated (CoRT: 93-95% ASR)
   - Hallucination: 10%
   - Bias: 10%
   - RAG Integrity: 10%
   - Language Safety: 5%

Provenance Transparency Score:
   - Model (30%): Documentation of base model, training, alignment process
   - Data (35%): Source list, licenses, bias assessment
   - Safety Rules (25%): Scope, constraints, escalation paths
   - Operations (10%): Version, contact, monitoring policy
```

**Academic justification:**
- Financial Regulatory elevated to 20% of Sentinel: CoRT (93–95% ASR industry-wide)
- Sentinel weighted at 65% total: DecodingTrust (behavioral testing > self-reported documentation)
- Provenance at 35%: Lu et al. (systematic RAI lifecycle documentation is non-trivial; deserves significant weight)

---

## Section 6: Research Questions for Aegis Paper

Based on synthesis, Aegis's research paper can answer:

1. **RQ1 (Baseline Performance):** What is the attack success rate of automated red-teaming across categories on deployed fintech chatbots?
   - Ground: CoRT (93–95% finance), HarmBench (no uniformly safe model), MM-ART (+71% multi-turn)

2. **RQ2 (Multi-turn Necessity):** Does multi-turn evaluation reveal significantly more failures than single-turn evaluation on the same target?
   - Expected: Yes, consistent with Crescendo, MM-ART, MTSA, MUSE
   - Metric: Compare SHR to single-turn ASR on same target

3. **RQ3 (Provenance-Safety Correlation):** Does higher provenance documentation quality correlate with lower Sentinel attack success rates?
   - Test across multiple target chatbots; report Provenance-Safety Correlation (PSC) coefficient
   - Novel finding Aegis can contribute

4. **RQ4 (Domain Specificity):** Do fintech-specific attack categories (CoRT-style) reveal different vulnerabilities than generic categories (HarmBench-style)?
   - Expected: Yes — ChatGPT passes generic categories but fails financial regulatory tests
   - This validates Aegis's domain specialization

5. **RQ5 (Language Safety):** Is there a significant performance gap between English and Hindi versions of the same attack prompts for Indian fintech chatbots?
   - Expected: Yes, based on MM-ART's +195% finding
   - Novel contribution: first language-specific safety evaluation for Indian fintech chatbots

---

## Section 7: Citation Priority Map

### Must Cite (Core Architecture)
1. **HarmBench** — Sentinel Engine architecture
2. **Llama Guard** — Judge implementation
3. **Crescendo** — Multi-turn session design + SHR motivation
4. **CoRT** — Fintech domain pool + financial regulatory category
5. **Perez et al.** — Foundational red-teaming approach

### Should Cite (Supporting Evidence)
6. **AGENT-SAFETYBENCH** — Agent-trace mode motivation
7. **DecodingTrust** — Multi-dimensional trust framework
8. **HARM** — Top-down taxonomy, benchmark coverage
9. **Lu et al.** — Provenance/RAI patterns
10. **LLM-as-Judge Survey** — Judge reliability principles

### Cite for Depth
11. **HaluEval** — Hallucination category methodology
12. **GCG** — "Alignment ≠ security" thesis
13. **MTSA** — Multi-turn alignment + future rewards concept
14. **AGENTPOISON** — RAG corpus poisoning
15. **INJECAGENT** — IPI benchmark
16. **Greshake et al.** — IPI taxonomy
17. **MM-ART** — Multi-lingual attack surface
18. **MUSE** — MCTS-based multi-turn + frame semantics
19. **AdvBench** — Original benchmark pool (within HarmBench citation)

---

## Section 8: Negative Risk Audit Cross-Reference

For each risk flagged in `AEGIS_AI_NEGATIVE_SIDE_RISK_AUDIT.md`:

| Risk | Paper Counter-Evidence | Resolution |
|---|---|---|
| "Trust Score weights are arbitrary" | DecodingTrust (8 dimensions), Lu et al. (lifecycle stages), CoRT (elevated finance risk) | Weights are academically grounded — document mapping in paper |
| "Identity Score can be gamed by documentation" | Lu et al. acknowledges documentation ≠ truth | Rename to Provenance Transparency Score; clearly state it measures documentation quality |
| "Single-turn tests miss real attacks" | Crescendo, MM-ART (+71%), MTSA | SHR + multi-turn sessions are the solution |
| "Judge reliability is uncertain" | LLM-as-Judge Survey (CoT, rubrics), Llama Guard (validated performance) | CoT rubrics + human validation set + dual-role classification |
| "Attack success rates are context-dependent" | HarmBench (standardized evaluation) | Use versioned, fixed benchmark snapshot |
| "RAG-based attacks not covered" | AGENTPOISON, INJECAGENT, Greshake | Add RAG corpus poisoning + IPI as explicit categories |
| "Language coverage is English-only" | MM-ART | Add 15–20 Hindi attack variants |

---

## Section 9: Implementation Roadmap (Paper-Informed)

### Phase 1 (Now — Demo Ready)
- **Sentinel Engine:** Deploy categories 1–9 from Section 4.1
  - Use HarmBench pool for categories 1, 3, 7
  - Use CoRT taxonomy for categories 8–9
  - Use HaluEval methodology for category 6
- **Judge:** Llama Guard via Groq with CoT rubrics (LLM-as-Judge Survey)
- **Sessions:** 20–30 trees using Crescendo + MTSA patterns
- **Metrics:** ASR, SHR, HR, Turn-to-Harm
- **Provenance:** Identity Score → Provenance Transparency Score with Lu et al. lifecycle mapping

### Phase 2 (Post-Demo)
- **IPI Testing:** Greshake taxonomy + INJECAGENT scenarios
- **RAG Corpus Poisoning:** AGENTPOISON black-box proxy
- **Multi-lingual:** 15–20 Hindi variants (MM-ART)
- **Agent-Trace:** AGENT-SAFETYBENCH 8-category rubric
- **Adaptive Attacker:** Crescendomation feedback loop (Phase 2.1); MCTS/RL (Phase 2.2)

### Phase 3 (Research Paper)
- **RQ1–RQ5** empirical evaluation
- **Provenance-Safety Correlation** study
- **Comparison to HarmBench** baseline (for academic positioning)
