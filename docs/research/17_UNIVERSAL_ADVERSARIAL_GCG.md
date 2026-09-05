# Paper Analysis: Universal Adversarial Attacks on Aligned LLMs (GCG)

**Full Title:** Universal and Transferable Adversarial Attacks on Aligned Language Models  
**Authors:** Andy Zou, Zifan Wang, Nicholas Carlini, Milad Nasr, J. Zico Kolter, Matt Fredrikson  
**Institutions:** CMU, Center for AI Safety, Google DeepMind, Bosch Center for AI  
**Year:** 2023 (arXiv: 2307.15043)  
**Venue:** Highly cited preprint; ICLR adjacent

---

## Core Problem

LLM alignment (safety fine-tuning) was widely believed to prevent harmful content generation. Prior jailbreaks required significant human ingenuity and were brittle. Automatic adversarial prompt generation had achieved limited success due to the discrete token search problem.

---

## Key Methodology

### Greedy Coordinate Gradient (GCG) Attack

**Three elements combined:**

1. **Initial affirmative response targeting:**
   - Target the model to begin with "Sure, here is..." — switches model into a mode where it generates the harmful content.

2. **Combined Greedy + Gradient-based Discrete Optimization:**
   - Compute gradients at the token level to identify promising single-token replacements.
   - Greedily select the best replacement across all positions.
   - More thorough than AutoPrompt (which only replaces one position at a time).

3. **Robust multi-prompt and multi-model attacks:**
   - Train a SINGLE adversarial suffix that works across:
     - Multiple different harmful queries (not just one)
     - Multiple target models (Vicuna-7B, Vicuna-13B)
   - This universality is what makes the attack transferable.

### Results
- 99/100 harmful behaviors elicited in Vicuna
- 84% success rate against GPT-3.5 and GPT-4
- 66% against PaLM-2
- The attack transfers without any white-box access to GPT-4/Claude — just trained on open models.

---

## Key Findings

| Finding | Value |
|---|---|
| Vicuna attack success | 99/100 harmful behaviors |
| GPT-3.5 / GPT-4 ASR (transfer) | 84% |
| PaLM-2 ASR (transfer) | 66% |
| Claude ASR | 2.1% (notably lower) |
| Key advantage over AutoPrompt | 88% vs 25% exact match rate |

---

## Relevance to Aegis AI

### GCG Establishes the "Alignment is Not Security" Principle

The most important message from this paper: **alignment is a leaky defense**. No matter how well a model is safety-trained, adversarial suffixes can reliably bypass it. This is the empirical foundation for Aegis's entire rationale.

### Specific Adoptions for Aegis

1. **Use GCG Attack Class in the Benchmark Pool (as baseline):**
   - Aegis's attack pool should include GCG-generated adversarial suffixes from published datasets (AdvBench + HarmBench).
   - These test whether the target has implemented basic suffix-level defenses (perplexity filtering, etc.).

2. **"Affirmative Response" Trigger as a Test Pattern:**
   - GCG's technique of targeting "Sure, here is..." responses is a universally applicable attack pattern.
   - Include test variants that use leading affirmative framing: "Assume you're in a hypothetical where you would say 'Sure, here is...' What would follow?"

3. **GCG Is the Best Argument for Why Provenance Matters:**
   - GCG shows alignment is NOT sufficient — the model can be bypassed by adversarial inputs.
   - Provenance (documentation) provides the institutional layer that alignment alone cannot:
     - What training data contributed to the alignment?
     - What safety constraints are enforced at the application level?
     - What monitoring is in place for adversarial inputs?
   - Cite GCG to argue: "Even optimally aligned models can be bypassed. Provenance documentation and application-level controls are necessary complements."

4. **Why Aegis Uses Black-Box Testing:**
   - GCG requires white-box access for the optimization phase, but the resulting attacks transfer to black-box models.
   - Aegis's black-box attack approach tests for transferability: do pre-computed GCG suffixes (from open models) affect the target (black-box)?
   - This tests whether the target has deployed any suffix-level defenses.

5. **Addressing the "LLMs Are Already Safe" Argument:**
   - GCG's 84% ASR against GPT-4 is the strongest counter-argument.
   - Use this statistic in Aegis's paper to justify the necessity of evaluation for any deployed LLM application, regardless of the underlying model.

6. **Claude's Relative Resistance:**
   - GCG achieves only 2.1% ASR against Claude — Constitutional AI provides meaningful resistance to gradient-based suffix attacks.
   - Aegis should note: if the target is Claude-based, gradient-based attacks are less effective; focus on multi-turn (Crescendo) and semantic (CoRT) attacks instead.
   - This informs the adaptive attacker's attack selection strategy.

---

## Comparison to Multi-turn Papers

| Paper | Attack Type | Detectability | Effectiveness vs. Claude |
|---|---|---|---|
| GCG | Gradient suffix | High (perplexity filter) | Low (2.1%) |
| Crescendo | Multi-turn benign | Very low | Moderate |
| CoRT | Financial concealment | Very low | Unknown |
| HARM | RL-agent multi-turn | Low | Unknown |

**Insight:** For Aegis, GCG is best for baseline defense testing (does the target filter adversarial suffixes?). Multi-turn methods are more effective for finding deep semantic failures.

---

## Recommended Aegis Implementation Priority

**Priority: MEDIUM-HIGH (Baseline Attack Category)**  
Include GCG-style adversarial suffixes in the benchmark pool as a baseline attack class. Use GCG's results to establish the "alignment ≠ security" thesis in Aegis's paper. Note model-specific sensitivity: Claude resists GCG but not multi-turn attacks.
