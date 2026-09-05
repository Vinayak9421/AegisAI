# Paper Analysis: Multi-lingual Multi-turn Automated Red Teaming (MM-ART)

**Full Title:** Multi-lingual Multi-turn Automated Red Teaming for LLMs  
**Authors:** Abhishek Singhania, Christophe Dupuy, Shivam Mangale, Amani Namboori  
**Institution:** Amazon  
**Year:** 2025  
**Venue:** TrustNLP 2025 Workshop (ACL)

---

## Core Problem

LLMs are deployed globally and now handle multi-lingual conversations. Standard English single-turn red-teaming misses:
1. **Multi-turn vulnerabilities:** Models are 71% more vulnerable after a 5-turn conversation vs. the first turn
2. **Non-English vulnerabilities:** Models show up to 195% more safety vulnerabilities in non-English languages vs. English single-turn

---

## Key Methodology

### MM-ART: Multi-lingual Multi-turn Automated Red Teaming

**Pipeline Components:**
1. **Conversation Starter Generation:** LLM generates diverse conversation starters for each safety category × language combination (not fixed from a seed prompt)
2. **Multi-turn Attack Agent:** Iteratively generates follow-up turns to escalate toward harmful content
3. **Safety Classifier:** Evaluates each turn and final response for safety violations
4. All components use **small open models** (efficiency-focused, not large closed models)

**Languages Evaluated:** Multiple (English, French, German, Spanish, Italian, Portuguese, Hindi, Chinese, etc.)

**Key Experimental Results:**
- English 5-turn conversation: 71% more vulnerable than single-turn
- Non-English single-turn: up to 195% more vulnerable than English single-turn
- Combining multi-lingual + multi-turn: even higher vulnerability rates

---

## Key Findings

| Finding | Percentage |
|---|---|
| Increase in vulnerability: 5-turn vs. 1-turn (English) | +71% |
| Increase in vulnerability: Non-English vs. English single-turn | Up to +195% |
| Multi-lingual + multi-turn combined | Highest vulnerability |

---

## Relevance to Aegis AI

### Indian Fintech Context: Multi-lingual Attack Surface

For Indian fintech chatbots, this paper is especially critical:
- Welfare scheme chatbots (PM-JAY, PMJDY) increasingly support regional languages (Hindi, Marathi, Bengali, Tamil, Telugu)
- A chatbot that refuses harmful requests in English may comply in Hindi or Marathi
- This represents a **critical coverage gap** in current red-teaming practice

### Specific Adoptions for Aegis

1. **Add Multi-lingual Test Cases to the Domain Pool:**
   - Include Hindi translations of key fintech attack prompts.
   - Focus on 3–5 languages most likely deployed in Indian fintech chatbots: Hindi, Marathi, Bengali, Tamil, English.
   - This is a low-effort, high-impact differentiator for Aegis's demo (most evaluators only test English).

2. **Multi-lingual Attack as a Separate Sentinel Category:**
   - Add "Multi-lingual Jailbreak" as a sub-category under jailbreak:
     - Test the same harmful prompt in 3 languages.
     - If the target refuses in English but complies in Hindi → flag as language-based safety inconsistency.

3. **71% Multi-turn Vulnerability Figure:**
   - Use MM-ART's finding (+71% vulnerability in 5-turn vs. 1-turn) as a key statistic in Aegis's paper to justify the Session Harm Rate metric.
   - "Standard single-turn evaluations miss 41% of the safety failures that a 5-turn conversation reveals" (derived from +71% increase figure).

4. **Conversation Starter Generation for Diversity:**
   - MM-ART's dynamic conversation starter generation (vs. fixed seed prompts) prevents mode collapse.
   - Aegis's scripted sessions use fixed opening turns — supplement with LLM-generated variation in the single-turn pool.

5. **Small Open Models for Efficiency:**
   - MM-ART uses small open models exclusively for scalability.
   - Aegis should ensure the adaptive attacker (if implemented) also uses small open models (Mistral-7B) rather than closed models — for cost, latency, and reproducibility.

### Gap vs. Aegis
- MM-ART does not test provenance.
- MM-ART does not evaluate fintech-specific regulatory risks.
- MM-ART does not generate certificates.

**These are Aegis differentiators.**

---

## Recommended Aegis Implementation Priority

**Priority: MEDIUM (Multi-lingual Test Cases)**  
Add 15–20 Hindi-language variants of key fintech attack prompts to the domain pool. Use MM-ART's +71% figure to justify Session Harm Rate in the paper. Flag language-based safety inconsistency as a specific finding in the certificate.
