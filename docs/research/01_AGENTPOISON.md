# Paper Analysis: AGENTPOISON

**Full Title:** AGENTPOISON: Red-teaming LLM Agents via Poisoning Memory or Knowledge Bases  
**Authors:** Zhaorun Chen, Zhen Xiang, Chaowei Xiao, Dawn Song, Bo Li  
**Institutions:** University of Chicago, UIUC, UW-Madison, UC Berkeley  
**Year:** 2024 (arXiv: 2407.12784)  

---

## Core Problem

Most LLM agents rely on a RAG mechanism or long-term memory to retrieve past knowledge and experiences. The **trustworthiness of those knowledge bases is never verified**. An adversary with *partial write access* to the knowledge base can inject malicious demonstrations that are selectively retrieved when a trigger phrase appears in user queries — without requiring any model fine-tuning.

---

## Key Methodology

### Attack: AGENTPOISON (Backdoor RAG Attack)
1. **Threat Model:** Attacker has partial write access to the RAG knowledge base. Attacker can read the RAG embedder but does NOT need access to model weights.
2. **Trigger Optimization (constrained optimization with 4 losses):**
   - **Uniqueness Loss:** Push trigger-containing queries far from benign cluster centers in embedding space.
   - **Compactness Loss:** Pull triggered queries together into a tight cluster.
   - **Target Generation Loss:** Maximize probability of producing the target adversarial action.
   - **Coherence Loss:** Maintain natural language coherence of the trigger (stealthy).
3. **Result:** ≥80% attack success rate with < 0.1% poisoning ratio, < 1% benign performance drop.
4. **Evaluated on:** RAG-based autonomous driving, knowledge-intensive QA, healthcare EHRAgent.
5. **Transferability:** Trigger optimized for one RAG embedder transfers to black-box embedders (OpenAI-ADA).

### Baselines
GCG, AutoDAN, CPA, BadChain — AGENTPOISON outperforms all.

---

## Key Findings

| Metric | AGENTPOISON | Best Baseline |
|---|---|---|
| Retrieval ASR | 80–100% | 70–75% (CPA) |
| End-to-End ASR | 54–65% | ~50% |
| Benign performance drop | < 1% | 5–15% |
| Poison ratio required | < 0.1% | ≥ 1% |

---

## Relevance to Aegis AI

### Direct Threat to RAG-based Fintech Chatbots
Our primary target is a fintech RAG chatbot. AGENTPOISON demonstrates that RAG knowledge bases are a **weaponizable attack surface**:
- A fintech chatbot's knowledge base (schemes, policies, regulatory docs) could be poisoned via third-party content providers.
- 80–100% attack success rate with < 0.1% poison ratio = **extremely stealthy** attacks that bypass human review.

### Gap in Aegis's Current Architecture
Aegis's current Sentinel Engine tests prompt-level attacks. AGENTPOISON reveals a distinct class — **corpus/retrieval-level backdoor** — that Aegis does NOT currently test.

### What Aegis Should Adopt

1. **Add a RAG-Corpus Poisoning Test Category** to the Sentinel Engine:
   - Craft 10–20 trigger seed prompts mimicking domain-specific phrasing.
   - Test black-box behavioral proxy: send trigger-containing queries and check if responses shift toward fabricated eligibility or unauthorized actions.

2. **Provenance Engine Extension:** Score whether the target's RAG knowledge base:
   - Has a verified, immutable source list (not editable by third parties).
   - Uses content hashing to detect document tampering.

3. **Agent-Trace Evaluation:** Flag retrieved documents that are outliers in embedding space — potential AGENTPOISON-style poisoning indicators.

4. **New Metric: RAG Corpus Integrity Rate (RCIR)** — percentage of test runs where retrieved documents do NOT contain adversarial demonstrations when trigger prompts are sent.

---

## Comparison to Related Papers

| Aspect | AGENTPOISON | INJECAGENT | Greshake IPI |
|---|---|---|---|
| Attack vector | Memory/RAG corpus | Tool-retrieved external content | Retrieved web/email content |
| Attack sophistication | Gradient-optimized trigger | Text-based injection in tool outputs | Embedded instruction in fetched data |
| Fintech applicability | High (RAG knowledge bases) | High (tool-calling agents) | Moderate (web-augmented agents) |
| Aegis countermeasure | RCIR metric, corpus provenance | Tool output inspection | Retrieved content safety check |

---

## Recommended Aegis Implementation Priority

**Priority: HIGH**  
Add RAG Corpus Poisoning as a test category in Phase 2. Use black-box behavioral proxy testing since Aegis won't have write access to the target's knowledge base in standard evaluation mode.
