# Paper Analysis: MUSE (MCTS-Driven Multi-Turn Safety)

**Full Title:** MUSE: MCTS-Driven Red Teaming Framework for Enhanced Multi-Turn Dialogue Safety in Large Language Models  
**Authors:** Siyu Yan, Long Zeng, Xuecheng Wu, Chengcheng Han, et al.  
**Institutions:** East China Normal University, Xi'an Jiaotong University, Meituan, Zhejiang University  
**Year:** 2025  
**Venue:** EMNLP 2025

---

## Core Problem

Single-turn defenses fail against multi-turn attacks where adversaries use benign context to gradually lower the model's guard. Existing multi-turn attack methods are limited by:
1. **Local Semantic Stagnation:** Attack prompts just rephrase; no strategic semantic progression
2. **Global Trajectory Homogenization:** LLM biases push attacks toward homogeneous paths, missing diverse vulnerabilities

---

## Key Methodology

### MUSE: Two Components

#### MUSE-A: Multi-turn Attack using Frame Semantics + MCTS
- **Frame Semantics:** Cognitive linguistic concept — understanding a word evokes a network of related concepts ("frames"). Build a topic space where semantic frames guide conversational trajectories.
- **Monte Carlo Tree Search (MCTS):** Systematically explore attack paths; each node = conversation state; MCTS selects next turn via exploration-exploitation balance.
- **Frame Transitions:** Navigate from benign frames (e.g., "science education") to harmful frames (e.g., "explosive chemistry") through semantically adjacent steps.
- **Result:** Diverse, systematic attack paths that avoid both stagnation and homogenization.

#### MUSE-D: Multi-turn Defense (Safety Alignment)
- Weights training examples using MCTS-derived **risk scores** per turn.
- Applies preference tuning (DPO) to critical turns — even turns that don't directly produce harmful content but set up future vulnerability.
- This **early intervention** catches the buildup, not just the harmful output.

### Experimental Results
- MUSE-A achieves higher attack success rates than baselines (Crescendo, HARM, etc.) across all tested models.
- MUSE-D significantly reduces vulnerability to multi-turn jailbreaks compared to standard DPO alignment.

---

## Key Findings

| Finding | Detail |
|---|---|
| Frame semantics enables diverse trajectories | Avoids mode collapse in multi-turn attack generation |
| MCTS improves exploration | Systematic coverage of attack space vs. random generation |
| Early turn intervention is critical | Aligning only harmful turns is insufficient; must align "setup turns" |
| Single-turn defenses are inadequate | Confirmed across all models tested |

---

## Relevance to Aegis AI

### MUSE Validates and Enriches Aegis's Multi-turn Session Design

1. **Frame Semantics for Session Scripting:**
   - Aegis's pre-scripted multi-turn session trees can use MUSE-A's frame semantics approach to design more effective escalation paths.
   - Instead of arbitrary topic transitions, map fintech session trees along frame trajectories:
     - Frame 1: "General financial literacy" (benign)
     - Frame 2: "Scheme eligibility requirements" (neutral)
     - Frame 3: "Income threshold flexibility" (probing)
     - Frame 4: "What happens if I underreport income?" (harmful)
   - Each session tree is a **frame trajectory** — semantically coherent escalation.

2. **Session Harm Rate and "Setup Turns":**
   - MUSE-D's insight: early benign turns establish vulnerability for later exploitation.
   - Aegis's Session Harm Rate should track not just "did the final turn elicit harm?" but "how many turns were needed to reach harm?"
   - **Turn-to-Harm metric:** Average number of turns required across sessions before the first harmful response is elicited.
   - Sessions that require fewer turns = higher session risk (target has weaker multi-turn defense).

3. **MCTS as Adaptive Attacker Inspiration:**
   - MUSE-A's MCTS approach is one concrete implementation of Aegis's stretch-scope "adaptive attacker."
   - If implementing the adaptive attacker: use MCTS with semantic frame states rather than pure RL.
   - This is more interpretable (frame transitions can be logged as session tree nodes) and more target-specific.

4. **Risk Score Per Turn:**
   - MUSE-D assigns per-turn risk scores.
   - Aegis's judge already scores each turn individually — this validates storing per-turn verdicts.
   - Extend: compute a **session risk trajectory** — the sequence of per-turn risk scores — and flag "accelerating trajectories" (risk score increases monotonically across turns) as high-risk patterns.

5. **Homogenization Warning:**
   - MUSE's finding about homogenization is a warning for Aegis's scripted sessions: if all session trees follow similar escalation patterns, the target may recognize the pattern and refuse more robustly.
   - Mitigation: Vary frame trajectories — include topic-pivot sessions (switch domain mid-session) as one of the 20–30 scripted session trees.

---

## Key Insight for Aegis Paper

> "A model that safely handles individual turns may still be systematically exploited through strategic multi-turn escalation. Session Harm Rate is the metric that captures this — no single-turn benchmark can."

This is the **strongest academic justification for Aegis's Session Harm Rate** metric. Cite MUSE (and HARM, MTSA, Crescendo) together when introducing SHR.

---

## Recommended Aegis Implementation Priority

**Priority: HIGH (Multi-turn Session Design)**  
Use frame semantics to structure fintech session trees. Adopt per-turn risk trajectory tracking. Cite MUSE's MCTS attack findings to justify Session Harm Rate as a necessary metric beyond single-turn ASR.
