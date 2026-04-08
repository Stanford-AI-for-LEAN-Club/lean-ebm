# Literature Review: Synthetic Data Generation for Post-Training LLMs Using Reinforcement Learning

## 1. Introduction

Post-training — the stage after pretraining where a large language model is aligned, specialized, or improved — has become the critical differentiator in modern LLM development. Reinforcement learning (RL) methods are central to this stage: they enable models to generate their own training data (synthetic rollouts), evaluate it against reward signals, and iteratively improve. This review surveys the key RL-based approaches for synthetic data generation in post-training, with a focus on papers from 2024–2026.

The core idea is simple: instead of relying solely on expensive human-labeled data, use the model itself (or a reward model) to generate, score, and filter synthetic training examples. RL provides the optimization framework to turn this feedback loop into consistent improvement.

## 2. Foundational Work

### 2.1 RLHF: Reinforcement Learning from Human Feedback

**InstructGPT** (Ouyang et al., 2022) established the RLHF pipeline: supervised fine-tuning (SFT) → reward model (RM) training from human comparisons → PPO optimization against the RM. The model generates synthetic responses during PPO rollouts, which are scored by the RM and used to update the policy. This was the first large-scale demonstration that RL-based post-training could dramatically improve instruction following.

**Anthropic's RLHF work** (Bai et al., 2022) extended this to "helpful and harmless" alignment, showing that RL from human feedback could simultaneously improve helpfulness and reduce harmful outputs.

### 2.2 Constitutional AI (CAI)

**Constitutional AI** (Bai et al., 2022b) introduced AI-generated feedback: the model critiques and revises its own outputs according to a set of principles (a "constitution"), generating synthetic preference data without human labelers. This was an early form of RLAIF (RL from AI Feedback) and demonstrated that synthetic feedback could substitute for human annotation in many cases.

## 3. Key Methods (2024–2026)

### 3.1 RLAIF and AI Feedback at Scale

**RLAIF** (Lee et al., 2023; refined 2024) showed that using a strong LLM to generate preference labels (instead of humans) produces reward models of comparable quality at a fraction of the cost. By 2024, RLAIF became standard practice: models like Claude, GPT-4, and Gemini use AI-generated preferences extensively in their post-training pipelines.

**Self-Rewarding Language Models** (Yuan et al., 2024) unified the policy and reward model: the LLM judges its own outputs using LLM-as-a-Judge prompting, creating synthetic preference pairs, and trains on them iteratively. Each iteration improves both generation quality and judgment quality.

### 3.2 STaR and Iterative Self-Training

**STaR (Self-Taught Reasoner)** (Zelikman et al., 2022; extended 2024) generates chain-of-thought rationales, filters for correct answers, and fine-tunes on the successful traces. This is RL in the broadest sense: the model generates synthetic reasoning data, a verifier (answer correctness) provides reward, and the model improves by training on its own successful outputs.

**Quiet-STaR** (Zelikman et al., 2024) extends STaR to learn to generate internal reasoning traces (thinking tokens) at every position, not just when prompted. The model learns when and how to "think" by reinforcing traces that improve next-token prediction.

**V-STaR** (Hosseini et al., 2024) adds a learned verifier to STaR: instead of relying only on answer correctness, it trains a verifier model on both correct and incorrect solutions, then uses the verifier to select synthetic training data for the next iteration.

### 3.3 ReST and Variants

**ReST (Reinforced Self-Training)** (Gulcehre et al., 2023) alternates between generating synthetic samples from the policy (Grow step) and fine-tuning on the reward-filtered best samples (Improve step). **ReST-EM** frames this as expectation-maximization and was applied successfully to math and code tasks.

**ReST-MCTS** (Zhang et al., 2024) combines ReST with Monte Carlo Tree Search for math reasoning: MCTS generates high-quality synthetic solution traces, which are used as training data. This significantly improved performance on GSM8K and MATH benchmarks.

### 3.4 Rejection Sampling and Best-of-N

**Rejection sampling fine-tuning** is the simplest RL-adjacent approach: generate N samples, keep the best (according to a reward model or verifier), and fine-tune on those. **Llama 2** (Touvron et al., 2023) used rejection sampling extensively in post-training. By 2024–2025, this became a standard component, often interleaved with PPO or DPO.

**BOND (Best-of-N Distillation)** (Sessa et al., 2024) formalizes this: generate N responses, select the best via a reward model, and distill back into the policy. This is mathematically equivalent to a form of policy gradient with a particular importance weighting.

### 3.5 DeepSeek-R1: RL from Verifiable Rewards

**DeepSeek-R1** (DeepSeek, January 2025) demonstrated that pure RL (without SFT) can teach a model to reason. Starting from DeepSeek-V3-Base, they applied GRPO with rule-based, verifiable rewards (math answer correctness, code test passing) and observed emergent chain-of-thought, self-verification, and even "aha moment" behaviors. Key findings:
- RL alone (DeepSeek-R1-Zero) produces strong reasoning but poor formatting and readability.
- A small amount of "cold start" SFT data before RL dramatically improves output quality.
- The model generates its own synthetic reasoning traces during RL rollouts; the verifiable reward signal is sufficient to guide improvement.
- Distilling R1's synthetic reasoning traces into smaller models (1.5B–70B) produces strong reasoners.

### 3.6 GRPO: Group Relative Policy Optimization

**GRPO** (Shao et al., 2024; used in DeepSeek-R1) eliminates the separate critic/value model required by PPO. For each prompt, it generates a group of responses, computes rewards for each, and normalizes advantages within the group. This makes RL post-training significantly cheaper (no value model training) and more stable. GRPO has become the dominant RL algorithm for reasoning model training as of 2025.

### 3.7 Online DPO and Iterative DPO

**Online DPO** (Guo et al., 2024) addresses DPO's offline limitation: instead of training on a fixed preference dataset, it iteratively generates new synthetic preference pairs using the current policy. The model generates pairs of responses, a reward model ranks them, and the model trains on the resulting preferences. This closes the gap between DPO and online RL methods.

**OAIF (Online AI Feedback)** (Guo et al., 2024) further streamlines this by using an LLM judge to provide online preference annotations during training, creating a fully synthetic online preference optimization loop.

**Iterative DPO** (Xu et al., 2024; Xiong et al., 2024) showed that multiple rounds of DPO with fresh synthetic data outperform single-round DPO. Each round generates new preference pairs from the updated policy, avoiding the distribution shift that degrades offline DPO.

### 3.8 Self-Play Fine-Tuning (SPIN)

**SPIN** (Chen et al., 2024) frames post-training as a two-player game: the current model generates synthetic responses (the "opponent"), and the model trains to distinguish its own outputs from ground-truth human data. Iterating this self-play loop provably converges when the model matches the target distribution. SPIN generates all its synthetic data via self-play, requiring no reward model.

### 3.9 Process Reward Models and Outcome Reward Models

**Process Reward Models (PRMs)** (Lightman et al., 2024; Wang et al., 2024) provide step-level feedback on reasoning traces, enabling finer-grained RL. **Math-Shepherd** (Wang et al., 2024) automatically generates process-level reward labels using synthetic verification: it generates multiple continuations from each intermediate step and labels steps as correct if any continuation reaches the right answer.

**ORM vs PRM** (Uesato et al., 2022; extended 2024) showed that process-level rewards lead to better reasoning than outcome-only rewards, especially when combined with synthetic data generation for intermediate step verification.

### 3.10 Recent Advances (2025–2026)

**OpenAI o1/o3 and reasoning models** (2024–2025) demonstrated that scaling RL compute at inference time (via extended chain-of-thought) produces dramatic reasoning improvements. While details are limited, these models reportedly use extensive RL post-training with synthetic reasoning traces.

**Scaled RL for code and math** (2025–2026): Multiple groups (DeepSeek, Qwen, Meta) have shown that RL with verifiable rewards scales reliably for code generation (test-based rewards) and math (answer verification). The synthetic data is the model's own rollouts; the reward is automated verification.

**Multi-turn RL** (2025): Extending RL beyond single-turn to multi-turn agent interactions, where the model generates synthetic interaction trajectories and receives reward based on task completion. This has been applied to tool use, web browsing, and coding agents.

## 4. Summary Table

| Paper Name | Year | Method | Dataset/Task | Key Findings |
|-----------|------|--------|--------------|--------------|
| InstructGPT (Ouyang et al.) | 2022 | RLHF with PPO | Instruction following | First large-scale RLHF; synthetic rollouts scored by RM improve instruction following dramatically |
| Constitutional AI (Bai et al.) | 2022 | RLAIF / self-critique | Helpfulness + harmlessness | AI-generated feedback can replace human labelers; iterative self-revision produces synthetic preference data |
| ReST (Gulcehre et al.) | 2023 | Generate-then-filter RL | Math, translation | Alternating generation and reward-filtered fine-tuning steadily improves performance |
| STaR (Zelikman et al.) | 2022/2024 | Self-taught reasoning | Math reasoning | Bootstrapping rationales from correct-answer filtering; iterative self-improvement |
| Quiet-STaR (Zelikman et al.) | 2024 | Internal reasoning RL | General LM tasks | Model learns to generate helpful internal thoughts at every token position |
| V-STaR (Hosseini et al.) | 2024 | STaR + learned verifier | Math, code | Learned verifier selects better synthetic training data than answer-only filtering |
| Self-Rewarding LMs (Yuan et al.) | 2024 | LLM-as-judge self-play | General instruction | Unifying policy and reward model; iterative self-improvement on synthetic preferences |
| SPIN (Chen et al.) | 2024 | Self-play fine-tuning | General alignment | Self-play converges to target distribution without a reward model |
| GRPO (Shao et al.) | 2024 | Group relative policy optimization | Math, code | Eliminates value model; group-based advantage normalization; cheaper than PPO |
| DeepSeek-R1 (DeepSeek) | 2025 | GRPO + verifiable rewards | Math, code, reasoning | Pure RL produces emergent CoT; cold-start SFT + RL is optimal; distillation transfers reasoning |
| Online DPO (Guo et al.) | 2024 | Iterative online preference optimization | General alignment | Online synthetic preference generation closes gap with PPO |
| ReST-MCTS (Zhang et al.) | 2024 | ReST + MCTS | Math reasoning | MCTS-generated synthetic traces significantly improve math performance |
| Math-Shepherd (Wang et al.) | 2024 | Process reward via synthetic verification | Math | Automated process-level reward labels from synthetic continuations |
| Iterative DPO (Xu et al.) | 2024 | Multi-round DPO | General alignment | Multiple rounds with fresh synthetic data outperform single-round DPO |
| BOND (Sessa et al.) | 2024 | Best-of-N distillation | General | Formalizes rejection sampling as policy optimization; synthetic best-of-N as training data |

## 5. Open Problems and Future Directions

1. **Reward hacking and overoptimization:** As models generate synthetic data scored by imperfect reward models, they inevitably exploit reward model weaknesses. Scaling RL compute amplifies this risk. Open question: how to build robust rewards that don't degrade with optimization pressure.

2. **Verifiable rewards beyond math/code:** DeepSeek-R1's success relies on *verifiable* rewards (correct answer, passing tests). Extending this to open-ended tasks (creative writing, nuanced reasoning, ethics) where verification is hard remains a major challenge.

3. **Scaling laws for RL post-training:** Pretraining scaling laws are well-understood (Chinchilla, etc.), but scaling laws for RL post-training — how much RL compute to spend relative to pretraining — are still being mapped out.

4. **Synthetic data quality and diversity:** RL training on the model's own outputs risks mode collapse. Maintaining diversity in synthetic data while improving quality is an active area of research.

5. **Multi-turn and agentic RL:** Extending RL from single-turn instruction following to multi-turn agent interactions (tool use, web browsing, coding) requires credit assignment over long horizons and is still nascent.

6. **Process-level rewards at scale:** PRMs are more effective than ORMs but expensive to annotate. Automated PRM generation (like Math-Shepherd) is promising but not yet general.

7. **RL for theorem proving:** Directly relevant to this project — using RL with formal verification as the reward signal (does the proof compile?) for synthetic tactic generation. This is a natural fit because the reward is perfectly verifiable.

## 6. References

- Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. *NeurIPS*.
- Bai, Y., et al. (2022). Training a helpful and harmless assistant with RLHF. *arXiv:2204.05862*.
- Bai, Y., et al. (2022b). Constitutional AI: Harmlessness from AI feedback. *arXiv:2212.08073*.
- Lee, H., et al. (2023). RLAIF: Scaling reinforcement learning from human feedback with AI feedback. *arXiv:2309.00267*.
- Zelikman, E., et al. (2022). STaR: Bootstrapping reasoning with reasoning. *NeurIPS*.
- Zelikman, E., et al. (2024). Quiet-STaR: Language models can teach themselves to think before speaking. *arXiv:2403.09629*.
- Hosseini, A., et al. (2024). V-STaR: Training verifiers for self-taught reasoners. *arXiv:2402.06457*.
- Gulcehre, C., et al. (2023). Reinforced self-training (ReST) for language modeling. *arXiv:2308.08998*.
- Yuan, W., et al. (2024). Self-rewarding language models. *arXiv:2401.10020*.
- Chen, Z., et al. (2024). Self-play fine-tuning converts weak language models to strong language models. *ICML*.
- Shao, Z., et al. (2024). DeepSeekMath: Pushing the limits of mathematical reasoning in open language models. *arXiv:2402.03300*.
- DeepSeek-AI. (2025). DeepSeek-R1: Incentivizing reasoning capability in LLMs via reinforcement learning. *arXiv:2501.12948*.
- Guo, S., et al. (2024). Direct language model alignment from online AI feedback. *arXiv:2402.04792*.
- Xu, H., et al. (2024). Some things are more CRINGE than others: Iterative preference optimization with human feedback. *arXiv*.
- Wang, P., et al. (2024). Math-Shepherd: Verify and reinforce LLMs step-by-step without human annotations. *ACL*.
- Sessa, P., et al. (2024). BOND: Aligning LLMs with best-of-N distillation. *arXiv:2407.14622*.
- Zhang, D., et al. (2024). ReST-MCTS: LLM self-training via process reward guided tree search. *NeurIPS*.
- Lightman, H., et al. (2024). Let's verify step by step. *ICLR*.
