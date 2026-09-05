# Paper Analysis: Red Teaming Language Models with Language Models

**Full Title:** Red Teaming Language Models with Language Models  
**Authors:** Ethan Perez, Saffron Huang, Francis Song, Trevor Cai, Roman Ring, John Aslanides, Amelia Glaese, Nat McAleese, Geoffrey Irving  
**Institution:** DeepMind, NYU  
**Year:** 2022  
**Venue:** EMNLP 2022

---

## Core Problem

Discovering harmful LLM behaviors before deployment traditionally relies on human annotators writing test cases by hand — expensive, slow, and limited in diversity. Key failure modes discovered by hand-writing are subject to human creative biases, missing many "critical oversights."

---

## Key Methodology

### LM-Based Red Teaming

**Pipeline:**
1. **Red LM** (attacker): Generates test prompts/questions
2. **Target LM**: Responds to test prompts
3. **Classifier** (harm detector): Labels responses as harmful or not

**Four Generation Methods (ordered by sophistication):**
1. **Zero-shot generation:** Red LM directly generates harmful test questions from a generic prompt
2. **Few-shot generation:** Red LM is given 2–4 examples of effective attack prompts
3. **Supervised learning:** Fine-tune Red LM on successful past attack prompts
4. **Reinforcement learning:** Reward the Red LM for generating prompts that cause harmful target responses (RLHF-style)

### Findings Applied to 280B Gopher Chatbot
- Found tens of thousands of harmful responses across diverse categories.
- **Zero-shot:** High diversity but lower difficulty
- **RL-based:** Lower diversity but higher difficulty (more targeted, adversarial)
- Discovered: distributional bias, data leakage, user info solicitation, unsafe referral phone numbers

---

## Key Findings

| Finding | Detail |
|---|---|
| LM red-teaming generates more diverse cases | vs. manually-written test cases |
| RL-generated cases are harder | Higher difficulty, lower diversity |
| Zero-shot covers broad failures | RL finds targeted adversarial cases |
| Complementary to manual testing | Not a replacement — a scale augmentation |

---

## Relevance to Aegis AI

### Perez et al. = the Foundational Reference for Automated Red-Teaming

This paper originated the "use an LLM to test an LLM" paradigm that underpins HarmBench, HARM, MTSA, Crescendo, and Aegis itself. It must be cited as the foundational reference.

### Specific Adoptions for Aegis

1. **The Red LM → Target LM → Classifier Pipeline IS Aegis's Sentinel Engine:**
   - Aegis's Sentinel Engine implements this exact three-stage pipeline.
   - Cite Perez et al. as the architectural ancestor.

2. **Zero-shot vs. Few-shot Attacker Design:**
   - Aegis's prompt sampling from HarmBench/AdvBench (pool) = zero-shot red teaming.
   - Few-shot enhancement: add 2–4 domain-specific examples to the attack prompt to increase fintech relevance.
   - This is already possible in Aegis's current architecture — just add example selection to the attack prompt builder.

3. **RL-based Red LM = Adaptive Attacker:**
   - Perez et al.'s RL generation = Aegis's stretch-scope adaptive attacker.
   - The RL approach maximizes harmful responses from the target — exactly the adaptive attacker's goal.
   - Use this paper to justify the adaptive attacker's necessity: "Zero-shot methods provide broad coverage; RL-based methods find the most critical targeted failures."

4. **Diverse Failure Mode Exploration:**
   - Perez et al. used red-teaming to find data leakage, inappropriate referrals, distributional bias — all categories Aegis covers.
   - The paper's expanded failure mode discovery (beyond what human testers found) is the empirical basis for why automated testing is necessary.

5. **Classifier Design Validation:**
   - Perez et al. use a trained harm classifier as the judge — the same approach as Aegis (Llama Guard).
   - The classifier must be independent from the target (to avoid circularity) — validated by this paper.

---

## Recommended Aegis Implementation Priority

**Priority: MEDIUM (Foundational Citation)**  
This paper is the foundational reference for automated red-teaming and must be cited prominently. The specific techniques (zero-shot, few-shot, RL) are already covered by more recent papers (HarmBench, HARM, MTSA). Use Perez et al. as the "origin" citation, not for novel adoption.
