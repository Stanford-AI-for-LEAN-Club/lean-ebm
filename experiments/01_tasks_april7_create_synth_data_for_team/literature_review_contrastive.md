# Literature Review: Synthetic Data Generation for Post-Training LLMs Using Contrastive Learning

## 1. Introduction

Contrastive learning approaches to LLM post-training optimize models by comparing pairs (or groups) of outputs — preferred vs. dispreferred, positive vs. negative — rather than maximizing a scalar reward via policy gradient. These methods have surged in popularity since 2023 because they avoid the complexity and instability of RL training (no separate reward model, no PPO critic, no KL divergence tuning). At their core, they generate or curate synthetic preference pairs and train the model to increase the likelihood gap between good and bad responses.

This review surveys contrastive methods for post-training, with a focus on how they generate and use synthetic data. We compare to RL-based methods where relevant.

## 2. Foundational Work

### 2.1 Direct Preference Optimization (DPO)

**DPO** (Rafailov et al., 2023) is the foundational contrastive method for LLM alignment. It reparameterizes the RLHF objective to derive a closed-form loss that directly optimizes the policy on preference pairs, eliminating the reward model and PPO entirely. The loss increases log-probability of preferred responses relative to dispreferred ones, with implicit KL regularization against a reference policy.

DPO was originally designed for human-annotated preference data, but its simplicity made it the natural framework for synthetic preference generation: any method that can produce (prompt, preferred, dispreferred) triples can plug into DPO.

### 2.2 SLiC-HF: Sequence Likelihood Calibration

**SLiC-HF** (Zhao et al., 2023) predates DPO and uses a contrastive ranking loss (hinge loss) on preference pairs. It demonstrated that simple contrastive calibration of sequence likelihoods can align models without RL. SLiC-HF also introduced the idea of using the model's own generations as negative examples — an early form of synthetic contrastive data.

## 3. Key Methods (2024–2026)

### 3.1 DPO Variants

The DPO framework spawned numerous variants, each addressing specific limitations:

**IPO (Identity Preference Optimization)** (Azar et al., 2024) replaces DPO's log-sigmoid loss with a squared-error loss on the preference margin. This prevents the "log-probability collapse" where DPO pushes dispreferred response probabilities to zero. IPO is more stable when preferences are noisy or when synthetic data contains borderline pairs.

**KTO (Kahneman-Tversky Optimization)** (Ethayarajh et al., 2024) eliminates the need for paired preferences entirely. Instead, it works with unpaired "good" and "bad" examples, applying a loss inspired by Kahneman and Tversky's prospect theory (asymmetric treatment of gains vs. losses). This is significant for synthetic data because it's easier to generate labeled examples (good/bad) than matched pairs (better/worse for the same prompt).

**ORPO (Odds Ratio Preference Optimization)** (Hong et al., 2024) combines SFT and alignment into a single loss by adding a preference penalty based on the odds ratio of preferred vs. dispreferred responses. It eliminates the need for a separate SFT stage and reference model, simplifying the pipeline for synthetic preference training.

**SimPO (Simple Preference Optimization)** (Meng et al., 2024) uses length-normalized log-probability as an implicit reward and adds a target margin to the preference loss. SimPO removes the need for a reference model (unlike DPO, which requires the frozen reference for KL regularization), making it cheaper to run on synthetic data.

**CPO (Contrastive Preference Optimization)** (Xu et al., 2024) adds an explicit SFT term on the preferred response to the DPO loss, preventing the model from degrading the preferred response's absolute likelihood while increasing the relative gap.

### 3.2 Contrastive Decoding

**Contrastive Decoding** (Li et al., 2023) improves generation quality at inference time by contrasting the logits of a strong (expert) model with a weak (amateur) model. Tokens that the expert favors more than the amateur are upweighted. While not a training method, it motivates contrastive approaches and can be used to generate synthetic data: outputs from contrastive decoding can serve as preferred examples, while amateur-only outputs serve as dispreferred.

**DExperts** (Liu et al., 2021; extended 2024) uses expert and anti-expert models to steer generation. The synthetic data angle: DExperts can generate contrastive pairs (expert output vs. anti-expert output) for training.

### 3.3 Synthetic Preference Pair Generation

A critical question for all contrastive methods: where do the preference pairs come from?

**Self-generated pairs:** The model generates multiple responses per prompt; a reward model, LLM judge, or verifier ranks them. The best and worst become the preferred/dispreferred pair. This is used in Online DPO, OAIF, and Self-Play Preference Optimization (SPPO).

**Rejection sampling pairs:** Generate N responses, keep the highest-scored as preferred and lowest as dispreferred. This naturally produces synthetic contrastive data with large quality gaps.

**Model-as-judge pairs:** A stronger model (e.g., GPT-4) evaluates pairs from a weaker model, generating preference labels. This is RLAIF applied to contrastive training.

**Targeted negative generation:** Specifically craft dispreferred responses that are challenging (hard negatives). Methods include:
- Perturbing good responses to introduce subtle errors
- Using the model's own common failure modes
- Adversarial generation targeting known weaknesses

### 3.4 SPIN: Self-Play from a Contrastive Perspective

**SPIN** (Chen et al., 2024) can be viewed as a contrastive method: human-written responses are the positive examples, and the model's own current generations are the negatives. The model trains to distinguish the two. Over iterations, as the model improves, the negatives get harder (closer to the positives), creating a curriculum of increasingly difficult contrastive pairs. SPIN uses no reward model and generates all its synthetic negatives via self-play.

### 3.5 CLICK: Contrastive Learning for Instruction-following with Knowledge

**CLICK** (Zheng et al., 2024) applies contrastive learning to instruction following by generating synthetic positive/negative pairs based on instruction adherence. For each instruction, it generates responses that follow the instruction (positive) and responses that plausibly violate it (negative), then trains with a contrastive loss to sharpen instruction discrimination.

### 3.6 Self-Play Preference Optimization (SPPO)

**SPPO** (Wu et al., 2024) extends SPIN by generating preference pairs through self-play: the model generates two responses per prompt, an LLM judge evaluates them, and the model trains on the resulting preferences. Unlike SPIN, both responses are model-generated (no human reference needed), making it fully synthetic.

### 3.7 Contrastive Post-Training for Reasoning

**Contrastive chain-of-thought** approaches (2024–2025) generate paired reasoning traces:
- Correct trace (reaches right answer) → preferred
- Incorrect trace (plausible but wrong) → dispreferred

This creates synthetic contrastive data for reasoning improvement. **Orca-2.5** and related work uses this approach: generate many CoT traces, verify answers, and create contrastive pairs from correct/incorrect traces.

### 3.8 Negative-Aware Training and Hard Negative Mining

**West-of-N** (Pace et al., 2024) shows that the quality of dispreferred responses matters significantly. Using the *worst* of N responses (rather than a random dispreferred response) as the negative creates harder contrastive pairs and leads to stronger alignment. This parallels hard negative mining in metric learning.

**Iterative negative refinement** (2024–2025): Multiple groups have shown that iteratively refining the negative examples — making them more subtle and harder to distinguish — produces better contrastive training. This is analogous to curriculum learning with synthetic hard negatives.

### 3.9 Token-Level Contrastive Methods

**DPO and its variants operate at the sequence level.** Recent work (2024–2025) has explored token-level contrastive losses:

**TDPO (Token-level DPO)** applies the preference loss at each token position, enabling finer-grained credit assignment. This pairs naturally with synthetic data where specific tokens or phrases are identified as the quality-differentiating elements.

**Step-DPO** (Lai et al., 2024) applies DPO at the reasoning step level for math problems: each step in a solution is treated as a contrastive pair (correct step vs. incorrect step), using synthetic step-level labels.

### 3.10 Recent Advances (2025–2026)

**Hybrid RL + contrastive methods**: Several 2025 approaches combine RL and contrastive training. For example, using GRPO to generate rollouts and verifiable rewards, then constructing contrastive pairs from the rollouts for DPO-style training. This gets the best of both: RL's exploration with contrastive training's stability.

**Length-controlled contrastive training** (2025): Addressing the "verbosity bias" in DPO (models learn to be verbose because longer responses are often preferred), recent methods normalize the contrastive loss by response length or explicitly control for length when constructing synthetic pairs.

## 4. Comparison: RL-Based vs. Contrastive Approaches

| Dimension | RL-Based (PPO, GRPO) | Contrastive (DPO, KTO, etc.) |
|-----------|---------------------|------------------------------|
| **Training stability** | Less stable; reward hacking, KL divergence explosion, value model collapse | More stable; simpler loss landscape, fewer hyperparameters |
| **Compute cost** | Higher: need reward model + value model + policy rollouts (PPO) or grouped rollouts (GRPO) | Lower: single forward/backward pass on preference pairs; no rollouts during training |
| **Synthetic data usage** | Online: generates synthetic data during training (rollouts) | Offline or semi-online: preference pairs can be pre-generated or iteratively refreshed |
| **Reward model dependency** | Explicit reward model required (PPO) or verifiable reward (GRPO/R1) | No reward model needed; preferences can come from judges, verifiers, or heuristics |
| **Exploration** | Natural exploration via stochastic rollouts | Limited exploration; constrained by preference data distribution |
| **Scalability** | Scales well with compute (more rollouts, more RL steps) | Scales well with data (more preference pairs); less clear scaling with compute |
| **Performance ceiling** | Higher for reasoning tasks (DeepSeek-R1, o1 are RL-based) | Slightly lower on complex reasoning; competitive on alignment and instruction following |
| **Ease of implementation** | Complex (PPO has many moving parts; GRPO is simpler) | Simple (DPO is ~20 lines of loss code) |

**Key insight:** RL methods excel when there is a *verifiable reward signal* (math correctness, code tests, proof compilation). Contrastive methods excel when reward is *implicit in preferences* (helpfulness, style, safety) and training stability matters more than pushing the performance frontier.

**Convergence:** By 2025–2026, the distinction is blurring. Online DPO with iterative synthetic data is functionally similar to simplified RL. GRPO with preference-based reward is functionally contrastive. The field is converging on hybrid approaches.

## 5. Summary Table

| Paper Name | Year | Method | Dataset/Task | Key Findings |
|-----------|------|--------|--------------|--------------|
| DPO (Rafailov et al.) | 2023 | Direct preference optimization | Helpfulness, safety | Closed-form RLHF alternative; eliminates reward model and PPO; competitive with RLHF |
| SLiC-HF (Zhao et al.) | 2023 | Contrastive ranking loss | Alignment | Hinge loss on preference pairs; self-generated negatives; simpler than RLHF |
| IPO (Azar et al.) | 2024 | Squared-error preference loss | Alignment | Fixes DPO's probability collapse; more robust to noisy synthetic preferences |
| KTO (Ethayarajh et al.) | 2024 | Prospect-theory loss, unpaired | Alignment | No need for paired preferences; works with labeled good/bad examples independently |
| ORPO (Hong et al.) | 2024 | Odds ratio + SFT | Instruction following | Combines SFT and alignment; no reference model needed |
| SimPO (Meng et al.) | 2024 | Length-normalized implicit reward | Alignment | Reference-model-free DPO variant; length normalization prevents verbosity bias |
| SPIN (Chen et al.) | 2024 | Self-play contrastive | General alignment | Human = positive, self-generated = negative; converges without reward model |
| SPPO (Wu et al.) | 2024 | Self-play preference optimization | Instruction following | Fully synthetic: both preferred/dispreferred from self-play + LLM judge |
| CLICK (Zheng et al.) | 2024 | Contrastive instruction learning | Instruction following | Synthetic positive/negative pairs based on instruction adherence |
| Step-DPO (Lai et al.) | 2024 | Step-level DPO | Math reasoning | Applies contrastive loss at each reasoning step; synthetic step-level labels |
| West-of-N (Pace et al.) | 2024 | Hard negative selection | Alignment | Worst-of-N as dispreferred example; hard negatives improve contrastive training |
| CPO (Xu et al.) | 2024 | DPO + SFT term | Alignment | Prevents preferred response degradation; SFT regularization on positive examples |
| Online DPO (Guo et al.) | 2024 | Iterative online DPO | General | Online synthetic pair generation closes gap with RL methods |
| Contrastive Decoding (Li et al.) | 2023 | Expert-amateur logit contrast | Generation quality | Inference-time contrastive improvement; expert/amateur gap as quality signal |
| TDPO | 2024 | Token-level DPO | Alignment | Finer-grained credit assignment; token-level contrastive pairs |

## 6. Open Problems and Future Directions

1. **Hard negative generation at scale:** Current methods use simple heuristics (worst-of-N, random perturbation). Systematic, targeted generation of hard negatives — responses that are subtly wrong or almost-preferred — could significantly improve contrastive training.

2. **Contrastive learning for reasoning:** DPO and variants work well for alignment but lag behind RL for complex reasoning (math, code, proofs). Developing contrastive methods that match RL's reasoning performance is an open challenge.

3. **Combining contrastive and RL signals:** Hybrid methods that use contrastive training for stability and RL for exploration are emerging but not yet well-understood theoretically.

4. **Contrastive learning beyond pairs:** Most methods use binary preferences (better/worse). Listwise and setwise preference learning, where the model learns from ranked lists of K responses, could make better use of synthetic data.

5. **Distribution shift in iterative training:** As the model improves, previously synthetic preference pairs become off-policy. Managing this distribution shift without full online RL is an active problem.

6. **Contrastive methods for EBMs:** Directly relevant to this project — contrastive divergence and noise-contrastive estimation are the training methods for EBMs. Connecting LLM contrastive post-training to EBM training could unify the frameworks: an EBM's energy function *is* a contrastive scorer over responses.

## 7. References

- Rafailov, R., et al. (2023). Direct preference optimization: Your language model is secretly a reward model. *NeurIPS*.
- Zhao, Y., et al. (2023). SLiC-HF: Sequence likelihood calibration with human feedback. *arXiv:2305.10425*.
- Azar, M., et al. (2024). A general theoretical paradigm to understand learning from human feedback. *AISTATS*.
- Ethayarajh, K., et al. (2024). KTO: Model alignment as prospect theoretic optimization. *arXiv:2402.01306*.
- Hong, J., et al. (2024). ORPO: Monolithic preference optimization without reference model. *arXiv:2403.07691*.
- Meng, Y., et al. (2024). SimPO: Simple preference optimization with a reference-free reward. *arXiv:2405.14734*.
- Chen, Z., et al. (2024). Self-play fine-tuning converts weak language models to strong language models. *ICML*.
- Wu, Y., et al. (2024). Self-play preference optimization for language model alignment. *arXiv:2405.00675*.
- Zheng, C., et al. (2024). CLICK: Contrastive learning for instruction-following with knowledge. *arXiv*.
- Lai, X., et al. (2024). Step-DPO: Step-wise preference optimization for long-chain reasoning. *arXiv:2406.18629*.
- Pace, A., et al. (2024). West-of-N: Synthetic preference generation for improved reward modeling. *arXiv*.
- Xu, H., et al. (2024). Contrastive preference optimization. *arXiv:2401.08417*.
- Guo, S., et al. (2024). Direct language model alignment from online AI feedback. *arXiv:2402.04792*.
- Li, X., et al. (2023). Contrastive decoding: Open-ended text generation as optimization. *ACL*.
- Liu, A., et al. (2021). DExperts: Decoding-time controlled text generation with experts and anti-experts. *ACL*.
