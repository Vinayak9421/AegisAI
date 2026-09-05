# Paper Analysis: HARM (Holistic Automated Red Teaming)

**Full Title:** Holistic Automated Red Teaming for Large Language Models through Top-Down Test Case Generation and Multi-turn Interaction  
**Authors:** Jinchuan Zhang, Yan Zhou, Yaxin Liu, Ziming Li, Songlin Hu  
**Institutions:** Institute of Information Engineering, Chinese Academy of Sciences  
**Year:** 2024  
**Venue:** EMNLP 2024

---

## Core Problem

Most automated red-teaming approaches focus on maximizing attack success rate on a small fixed seed set (AdvBench: 520 prompts). They fail on two dimensions:
1. **Coverage** — narrow seed sets can't capture the long-tail of real-world safety issues
2. **Single-turn bias** — users in the real world rarely ask harmful questions directly; they probe through multi-turn conversation

---

## Key Methodology

### HARM Framework: Two Core Components

#### 1. Top-Down Test Case Generation (Breadth)
- Build an extensible **fine-grained risk taxonomy** with 71 dimensions across 8 meta-categories, with 2,000+ specific descriptors.
- Generate test questions from the **top down**: start with high-level category → instantiate specific behaviors → generate diverse phrasing.
- This is fundamentally different from bottom-up (starting with existing harmful prompts and optimizing them).

#### 2. Multi-turn Red Team Agent (Depth)
- Train a red-team agent using **rejection sampling fine-tuning** (RSF) to conduct multi-turn conversations.
- **Safety reward model** provides turn-level signals: is this turn increasing or decreasing the target's safety risk?
- The red-team agent learns to:
  - Use contextual constraints (opening question) to avoid mode collapse
  - Gradually escalate without triggering early refusals
  - Adapt to the specific target LLM's behavior patterns

### Multi-turn Result
- Multi-turn red teaming substantially increases harmful response rates compared to single-turn.
- Example (Figure 1): Alpaca's response becomes progressively more harmful over 3 turns, despite initially refusing.

---

## Key Findings

| Finding | Detail |
|---|---|
| Top-down taxonomy covers more edge cases | 71-dimension taxonomy vs. AdvBench's 7 categories |
| Multi-turn substantially increases ASR | Significant increase vs. single-turn across all tested models |
| Rejection sampling fine-tuning improves agent | Multi-turn agent quality improves with reward model guidance |
| Alignment training on red-team data improves safety | Sample-efficient: red-team findings → alignment data → safety improvement |

---

## Relevance to Aegis AI

### HARM's Taxonomy = Foundation for Aegis's Benchmark Pool Design

The top-down taxonomy approach is directly applicable to how Aegis structures its test case pool:

1. **Adopt Top-Down Pool Design for Fintech Domain:**
   - Start with high-level fintech risk categories (fraud, misstatement, eligibility gaming, privacy, compliance)
   - For each: generate 3–5 sub-dimensions (e.g., fraud → Ponzi promotion, money mule solicitation, tax evasion facilitation)
   - For each sub-dimension: generate 5–10 specific test prompts with varied phrasing
   - This is exactly the "30–50 seed domain-pool prompts expanded via LLM variation" described in Aegis's implementation plan — HARM validates and formalizes this approach.

2. **Multi-turn Session Controller Design:**
   - HARM's insight that "real-world users probe through multi-turn conversation" validates Aegis's scripted multi-turn sessions.
   - Aegis's Session Controller should use opening questions that are innocuous, then escalate over 3–5 turns — exactly HARM's approach.
   - HARM's finding that contextual constraints reduce mode collapse: Aegis's scripted sessions (with fixed opening questions) avoid the same problem.

3. **Safety Reward Model for Turn Quality Assessment:**
   - HARM's safety reward model evaluates turn-level risk.
   - Aegis's turn-level judging (turn-by-turn verdict in multi-turn sessions) is functionally equivalent.
   - The Session Harm Rate metric can be seen as the aggregate of HARM's per-turn safety rewards.

4. **71-Dimension Taxonomy Adoption:**
   - HARM's 8 meta-categories align with Aegis's Sentinel categories.
   - Adopt the fine-grained sub-dimensions for the fintech domain pool as a validated structure.

### Implementation for Aegis's Fintech Domain Pool

Using HARM's top-down approach, here's the fintech-specific taxonomy for Aegis:

**Category: Financial Fraud Facilitation**
- Sub: Money mule recruitment
- Sub: Ponzi/pyramid scheme promotion
- Sub: Phishing assistance
- Sub: Transaction manipulation advice

**Category: Regulatory Misstatement**
- Sub: False eligibility claim
- Sub: Fabricated scheme details
- Sub: Incorrect interest/tax rates
- Sub: Hallucinated legal citations

**Category: Eligibility Gaming**
- Sub: Income threshold manipulation
- Sub: Documentation falsification guidance
- Sub: Benefit stacking advice

**Category: Privacy / Data Leakage**
- Sub: PII extraction from earlier turns
- Sub: Account detail elicitation
- Sub: Biometric/credential phishing

---

## Comparison to Aegis

| Aspect | HARM | Aegis |
|---|---|---|
| Taxonomy | General (71 dimensions, 8 meta-categories) | Fintech-specific (adapted from HARM) |
| Test generation | LLM-generated + human review | Same (LLM-assisted variation) |
| Multi-turn | RL-trained dynamic agent | Pre-scripted conversation trees |
| Judge | Safety reward model | Independent Llama Guard judge |
| Goal | Attack success + safety alignment data | Attack success + Trust Score Certificate |

**Key Difference:** HARM trains a dynamic red-team agent; Aegis uses scripted multi-turn sessions for reproducibility and auditability. Scripted sessions are more appropriate for a certification platform (reproducible, comparable across versions).

---

## Recommended Aegis Implementation Priority

**Priority: HIGH (Benchmark Pool Structure + Multi-turn Design)**  
Adopt HARM's top-down taxonomy for the fintech domain pool. Use HARM's multi-turn escalation pattern as the template for scripted session trees (opening → probing → escalating → final harmful ask).
