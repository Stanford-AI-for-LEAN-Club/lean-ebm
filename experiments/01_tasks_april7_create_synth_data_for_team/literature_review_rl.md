# Literature Review: Synthetic Data Generation for Post-Training LLMs via Reinforcement Learning (2024--2026)

**Date:** April 7, 2026  
**Author:** Auto-generated literature survey  
**Scope:** Reinforcement learning methods for synthetic data generation in LLM post-training, with emphasis on 2024--2026 publications and foundational work where needed for context.

---

## Table of Contents

1. [Introduction and Motivation](#1-introduction-and-motivation)
2. [Foundational RLHF Approaches](#2-foundational-rlhf-approaches)
3. [RLAIF and AI Feedback Methods](#3-rlaif-and-ai-feedback-methods)
4. [Self-Play and Self-Improvement](#4-self-play-and-self-improvement)
5. [Reinforcement Learning from Verifiable Rewards (RLVR)](#5-reinforcement-learning-from-verifiable-rewards-rlvr)
6. [STaR, ReST, and Iterative Self-Training](#6-star-rest-and-iterative-self-training)
7. [GRPO and Group Relative Policy Optimization](#7-grpo-and-group-relative-policy-optimization)
8. [Online DPO Variants](#8-online-dpo-variants)
9. [Rejection Sampling and Best-of-N Approaches](#9-rejection-sampling-and-best-of-n-approaches)
10. [Process and Outcome Reward Models](#10-process-and-outcome-reward-models)
11. [Notable 2025--2026 Papers on RL for Synthetic Data Generation](#11-notable-2025-2026-papers-on-rl-for-synthetic-data-generation)
12. [Model Collapse and Risks of Synthetic Data](#12-model-collapse-and-risks-of-synthetic-data)
13. [Summary Table](#13-summary-table)
14. [Open Problems and Future Directions](#14-open-problems-and-future-directions)
15. [References](#15-references)

---

## 1. Introduction and Motivation

Large language models (LLMs) are typically developed in two stages: *pre-training* on massive web-scale corpora, followed by *post-training* (alignment, instruction tuning, reasoning enhancement) that tailors the model for downstream use. The post-training phase has become a critical bottleneck because it traditionally depends on expensive, hard-to-scale human annotation -- whether in the form of demonstration data for supervised fine-tuning (SFT) or preference labels for reward model training.

Reinforcement learning (RL) provides a principled framework for generating and leveraging *synthetic data* during post-training. The core insight is that a model can sample its own outputs, evaluate them (via learned reward models, verifiable signals, or self-judgment), and then update its parameters to produce better outputs in the next iteration. This creates a virtuous cycle where the model is simultaneously the data generator and the learner, reducing or eliminating the dependence on human-written data.

Several forces drive current interest in RL-based synthetic data generation for LLMs:

- **Scalability beyond human data.** Human annotation does not scale to the trillions of tokens modern models consume. RL enables models to generate their own training signal, as demonstrated spectacularly by DeepSeek-R1 (Guo et al., 2025) and ReST-EM (Singh et al., 2024).
- **Emergent reasoning from reward shaping.** When LLMs are trained with RL using only outcome-level rewards (e.g., correctness on math problems), they spontaneously develop chain-of-thought reasoning, self-verification, and backtracking behaviors -- without any explicit supervision of these intermediate steps.
- **Cost reduction.** Replacing human preference annotators with AI feedback (RLAIF) or verifiable reward functions reduces the marginal cost of generating preference data by orders of magnitude.
- **Iterative self-improvement.** Methods such as STaR, Self-Rewarding LMs, and SPIN demonstrate that models can bootstrap from weak initial policies to strong ones through repeated self-play or self-evaluation cycles.

This review surveys the landscape of RL-based methods for synthetic data generation in LLM post-training, organized by methodological family. We focus on papers from 2024--2026 while including foundational work (2022--2023) where necessary for context.

---

## 2. Foundational RLHF Approaches

### 2.1 InstructGPT and the RLHF Pipeline

**Paper:** Ouyang et al., "Training language models to follow instructions with human feedback," NeurIPS 2022. ([arXiv:2203.02155](https://arxiv.org/abs/2203.02155))

InstructGPT established the canonical three-stage RLHF pipeline that remains the foundation of most post-training work:

1. **Supervised Fine-Tuning (SFT):** Fine-tune a pre-trained LM on human-written demonstrations of desired behavior.
2. **Reward Model (RM) Training:** Collect human comparisons of model outputs and train a scalar reward model on these preferences.
3. **RL Fine-Tuning via PPO:** Optimize the LM policy against the learned reward model using Proximal Policy Optimization (PPO), with a KL penalty to prevent divergence from the SFT policy.

Key findings: (a) A 1.3B InstructGPT model was preferred by human evaluators over the 175B GPT-3, demonstrating that alignment via RLHF can be more cost-effective than raw scaling. (b) RLHF improved truthfulness and reduced toxicity with minimal regression on standard NLP benchmarks.

**Relevance to synthetic data:** In InstructGPT, the RL phase generates on-policy rollouts (model completions) that are scored by the reward model. These scored rollouts are the synthetic training signal. The model never sees the human preference labels directly during RL -- it learns from synthetic reward signals applied to its own synthetic outputs.

### 2.2 Anthropic's Constitutional AI (CAI)

**Paper:** Bai et al., "Constitutional AI: Harmlessness from AI Feedback," arXiv 2022. ([arXiv:2212.08073](https://arxiv.org/abs/2212.08073))

Constitutional AI introduced two key innovations:

1. **Critique-and-revision (CAI-SL):** The model critiques its own outputs against a set of principles ("the constitution") and revises them. The revised outputs serve as synthetic SFT data.
2. **AI-generated preference labels (CAI-RL):** Instead of humans labeling preferences, a separate AI model evaluates pairs of responses against constitutional principles, generating synthetic preference data for reward model training.

This was one of the earliest demonstrations that high-quality alignment could be achieved with minimal human labeling, by using the model itself (guided by principles) to generate both the training data and the preference labels.

---

## 3. RLAIF and AI Feedback Methods

### 3.1 RLAIF: Reinforcement Learning from AI Feedback

**Paper:** Lee et al., "RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback," arXiv 2023; updated 2024. ([arXiv:2309.00267](https://arxiv.org/abs/2309.00267))

RLAIF replaces human preference annotators with an LLM judge. Google's study demonstrated that RLAIF achieves comparable performance to RLHF on summarization tasks, with significantly lower cost. The approach generates synthetic preference pairs by prompting a large model (e.g., PaLM 2) to compare two candidate outputs and select the better one.

**Key findings:** RLAIF and RLHF produce policies of similar quality when the AI labeler is sufficiently capable. The approach has become a default method in the post-training literature, with most major labs (Anthropic, Google, Meta) incorporating some form of AI feedback.

### 3.2 Self-Rewarding Language Models

**Paper:** Yuan et al., "Self-Rewarding Language Models," ICML 2024. ([arXiv:2401.10020](https://arxiv.org/abs/2401.10020))

This Meta/NYU paper takes RLAIF to its logical conclusion: the *same* model acts as both the policy being trained and the judge providing reward signals. The approach uses "LLM-as-a-Judge" prompting to have the model score its own outputs, then applies iterative DPO on the resulting synthetic preference data.

**Key innovation:** Unlike standard RLAIF where the judge model is frozen, self-rewarding models improve *both* their generation ability and their judging ability simultaneously across iterations. Fine-tuning Llama 2 70B for three iterations yielded a model outperforming Claude 2, Gemini Pro, and GPT-4 0613 on AlpacaEval 2.0.

### 3.3 Meta-Rewarding Language Models

**Paper:** Wu et al., "Meta-Rewarding Language Models: Self-Improving Alignment with LLM-as-a-Meta-Judge," arXiv 2024. ([arXiv:2407.19594](https://arxiv.org/abs/2407.19594))

An extension of self-rewarding that adds a meta-judge layer: the model evaluates not just responses, but also the quality of its own judgments, creating a higher-order self-improvement loop.

---

## 4. Self-Play and Self-Improvement

### 4.1 SPIN: Self-Play Fine-Tuning

**Paper:** Chen et al., "Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models," ICML 2024. ([arXiv:2401.01335](https://arxiv.org/abs/2401.01335))

SPIN frames alignment as a two-player game: the current model plays against its previous iteration. In each round:

1. The previous-iteration model generates synthetic responses.
2. The current model is trained to distinguish between these synthetic responses and human-written target responses, using a DPO-style objective.
3. The process repeats, with the newly trained model becoming the "previous iteration."

**Theoretical result:** The authors prove that the global optimum of the SPIN objective is reached only when the model's distribution matches the target (human) data distribution.

**Empirical result:** SPIN significantly improves LLM performance across HuggingFace Open LLM Leaderboard, MT-Bench, and Big-Bench tasks, and outperforms standard DPO even when DPO is supplemented with GPT-4-generated preference data.

### 4.2 Self-Play Preference Optimization (SPPO)

**Paper:** Wu et al., "Self-Play Preference Optimization for Language Model Alignment," ICLR 2025. ([OpenReview](https://openreview.net/forum?id=a3PmRgAB5T))

SPPO extends the self-play paradigm by applying the same optimization procedure repeatedly for multiple iterations in a self-play manner, where each iteration generates new data from the policy obtained in the last iteration for training a new policy that can provably outperform the old one.

### 4.3 Self-Instruct and Alpaca

**Paper:** Wang et al., "Self-Instruct: Aligning Language Models with Self-Generated Instructions," ICLR 2024. ([arXiv:2212.10560](https://arxiv.org/abs/2212.10560))

While not strictly an RL method, Self-Instruct is a foundational synthetic data generation technique. A strong LLM generates instruction-input-output triples, which are then used for SFT. Stanford Alpaca (Taori et al., 2023) demonstrated that 52K self-instruct examples generated from text-davinci-003 at less than $500 could train a 7B LLaMA model to near-ChatGPT quality on instruction following.

Self-Instruct is the precursor to many RL-based self-improvement methods: it generates synthetic data but lacks a feedback loop. The methods in this section close that loop by iterating the generate-evaluate-train cycle.

---

## 5. Reinforcement Learning from Verifiable Rewards (RLVR)

### 5.1 DeepSeek-R1

**Paper:** Guo et al., "DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning," Nature 2025. ([arXiv:2501.12948](https://arxiv.org/abs/2501.12948))

DeepSeek-R1 is arguably the most significant paper in this space from 2025. It demonstrates that reasoning abilities can be *incentivized purely through RL*, without any human-labeled reasoning trajectories. The approach uses **reinforcement learning with verifiable rewards (RLVR)**: for tasks with deterministic answers (math, code), the reward is simply whether the final answer is correct.

**Key components:**
- **Rule-based rewards:** Accuracy rewards (is the answer correct?) and format rewards (did the model use the specified output format?).
- **GRPO as the RL algorithm** (see Section 7).
- **No supervised reasoning data needed:** DeepSeek-R1-Zero is trained with pure RL from a base model, with no SFT stage.

**Emergent behaviors:** During training, DeepSeek-R1-Zero spontaneously develops:
- Chain-of-thought reasoning
- Self-reflection and self-verification
- Dynamic strategy adaptation (trying different approaches when one fails)
- "Aha moments" where the model reconsiders and corrects its reasoning

**Results:** DeepSeek-R1 achieves state-of-the-art performance on mathematics, coding competitions, and STEM reasoning benchmarks, surpassing models trained via conventional supervised learning.

**Synthetic data implications:** The entire training pipeline generates synthetic reasoning traces through RL rollouts. The model's own on-policy generations, filtered by verifiable correctness, constitute the synthetic training data. Furthermore, distillation of DeepSeek-R1's reasoning traces into smaller models (1.5B to 70B) achieves strong performance, demonstrating the transferability of RL-generated synthetic reasoning data.

### 5.2 DeepSeek-R1-Zero

The paper also describes DeepSeek-R1-Zero, which removes the SFT warmup entirely and trains from the base model using only RL. While R1-Zero exhibits interesting emergent reasoning, it suffers from readability issues and language mixing. The full DeepSeek-R1 pipeline uses a multi-stage approach: cold-start SFT with a small amount of long-CoT data, then RLVR, then rejection sampling to create new SFT data, and finally another round of RL.

### 5.3 Kimi k1.5

**Paper:** Kimi Team, "Kimi k1.5: Scaling Reinforcement Learning with LLMs," arXiv 2025. ([arXiv:2501.12599](https://arxiv.org/abs/2501.12599))

Kimi k1.5 introduces several innovations for scaling RL with LLMs:
- **Long-context RL:** Scales the RL context window to 128K tokens, showing continued performance improvement with increased context length.
- **Partial rollouts:** Improves training efficiency by reusing chunks of previous trajectories instead of regenerating from scratch.
- **Simplicity:** Achieves strong results without Monte Carlo tree search, value functions, or process reward models -- using only policy optimization with outcome rewards.
- **Multi-modal RL:** Jointly trains on text and vision data with RL.

The learned chain-of-thought traces exhibit planning, reflection, and correction behaviors, with longer contexts enabling more search steps within a single generation.

### 5.4 Theoretical Understanding of RLVR

**Paper:** "Reinforcement Learning with Verifiable Rewards Implicitly Incentivizes Correct Reasoning in Base LLMs," arXiv 2025. ([arXiv:2506.14245](https://arxiv.org/abs/2506.14245))

This paper provides a systematic investigation of how RLVR impacts LLM reasoning. It demonstrates that RLVR can extend the reasoning boundary for both mathematical and coding tasks and provides theoretical grounding for why verifiable rewards lead to correct intermediate reasoning steps, not just correct final answers.

---

## 6. STaR, ReST, and Iterative Self-Training

These methods share a common structure: generate synthetic solutions, filter by correctness, fine-tune on the filtered set, and iterate. They differ in the filtering mechanism, the fine-tuning objective, and whether they include rationalization or reward model guidance.

### 6.1 STaR: Self-Taught Reasoner

**Paper:** Zelikman et al., "STaR: Bootstrapping Reasoning With Reasoning," NeurIPS 2022. ([arXiv:2203.14465](https://arxiv.org/abs/2203.14465))

STaR is a foundational iterative self-training method:
1. Generate rationales for a dataset of questions using few-shot prompting.
2. Keep rationales that led to correct answers.
3. For incorrect answers, perform *rationalization*: generate a rationale conditioned on the correct answer.
4. Fine-tune the model on the combined set of correct rationales and rationalizations.
5. Repeat.

**Key insight:** Rationalization (step 3) is crucial -- it provides training signal from problems the model initially cannot solve, bootstrapping the model toward harder reasoning.

### 6.2 V-STaR: Verifier-Augmented STaR

**Paper:** Hosseini et al., "V-STaR: Training Verifiers for Self-Taught Reasoners," COLM 2024. ([arXiv:2402.06457](https://arxiv.org/abs/2402.06457))

V-STaR improves upon STaR by training a *verifier* (using DPO) on both correct and incorrect solutions generated during the self-improvement loop. Standard STaR discards incorrect solutions; V-STaR uses them as negative examples for verifier training. The verifier then selects the best solution from multiple candidates at test time.

### 6.3 RL-STaR: Theoretical Analysis

**Paper:** Luong et al., "RL-STaR: Theoretical Analysis of Reinforcement Learning Frameworks for Self-Taught Reasoner," arXiv 2024. ([arXiv:2410.23912](https://arxiv.org/abs/2410.23912))

This paper provides a theoretical framework for understanding why STaR and related methods work. It connects STaR to reinforcement learning, showing that the filtering-and-fine-tuning procedure can be understood as a form of policy gradient with implicit reward shaping.

### 6.4 Further STaR Extensions (2025)

- **CARE-STaR** (ACL Findings 2025): Handles instructions with multiple constraints by generating differentiating chain-of-thought rationales.
- **STaR-SQL** (ACL 2025): Applies STaR to text-to-SQL, treating SQL generation as a reasoning problem.
- **START: Self-Taught Reasoner with Tools** (arXiv 2025, [arXiv:2503.04625](https://arxiv.org/abs/2503.04625)): Enhances reasoning capabilities by integrating external tool use (calculators, code interpreters) into the STaR loop, enabling self-checking and self-debugging.

### 6.5 ReST: Reinforced Self-Training

**Paper:** Gulcehre et al., "Reinforced Self-Training (ReST) for Language Modeling," arXiv 2023. ([arXiv:2308.08998](https://arxiv.org/abs/2308.08998))

ReST (inspired by growing-batch RL) alternates between:
1. **Generate:** Sample a dataset from the current policy.
2. **Improve:** Fine-tune on the highest-reward subset using offline RL.

Unlike online RLHF (PPO), the dataset is generated offline, enabling data reuse and greater computational efficiency.

### 6.6 ReST-EM (Beyond Human Data)

**Paper:** Singh et al., "Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models," TMLR 2024. ([arXiv:2312.06585](https://arxiv.org/abs/2312.06585))

ReST-EM is a Google DeepMind paper that formalizes ReST as an expectation-maximization algorithm:
- **E-step:** Generate samples, filter by binary feedback (correct/incorrect).
- **M-step:** Fine-tune the model on the filtered (correct) samples.
- Repeat for a few iterations.

**Critical finding:** Models fine-tuned on *model-generated* synthetic data exhibit remarkably larger performance gains than those trained on *human-written* data, on competition-level math (MATH) and code generation (APPS). ReST-EM scales favorably with model size and generalizes to held-out benchmarks (GSM8K, HumanEval, Big-Bench Hard).

### 6.7 ReST-MCTS*

**Paper:** Zhang et al., "ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search," NeurIPS 2024. ([OpenReview](https://openreview.net/forum?id=8rcFOqEud5))

Integrates process reward models with tree search (MCTS*) to collect higher-quality reasoning traces. Unlike standard ReST which uses binary filtering, ReST-MCTS* uses step-level value estimates from tree search to identify and collect per-step training signal, circumventing the need for per-step human annotation.

### 6.8 Re-ReST: Reflection-Reinforced Self-Training

**Paper:** Dou et al., "Reflection-Reinforced Self-Training for Language Agents," EMNLP 2024. ([arXiv:2406.01495](https://arxiv.org/abs/2406.01495))

Re-ReST incorporates a *reflector* model during the self-training loop. When the agent fails (e.g., execution errors, unit test failures), the reflector uses environmental feedback to improve sample quality before the next round of fine-tuning.

### 6.9 ReST-RL

**Paper:** "ReST-RL: Achieving Accurate Code Reasoning of LLMs with Optimized Self-Training and Decoding," arXiv 2025. ([arXiv:2508.19576](https://arxiv.org/abs/2508.19576))

Combines an improved GRPO algorithm with test-time decoding methods for code reasoning. Represents the convergence of ReST-style self-training with modern RL optimization techniques.

---

## 7. GRPO and Group Relative Policy Optimization

### 7.1 DeepSeekMath and the Introduction of GRPO

**Paper:** Shao et al., "DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models," arXiv 2024. ([arXiv:2402.03300](https://arxiv.org/abs/2402.03300))

GRPO was introduced in this paper as a memory-efficient alternative to PPO for RL post-training. The key innovation: **eliminate the critic (value) network entirely** and instead sample multiple outputs for each prompt, using their *group average reward* as the baseline for advantage estimation.

**Formal description:** For a prompt, sample G outputs. Compute the reward for each. Normalize rewards within the group (subtract mean, divide by standard deviation). Use the normalized reward as the advantage in a clipped policy gradient update (similar to PPO but without the value network).

**Results:** DeepSeekMath 7B achieves 51.7% on the competition-level MATH benchmark (60.9% with self-consistency over 64 samples), approaching GPT-4 and Gemini Ultra performance.

**Why GRPO matters for synthetic data:** GRPO generates G synthetic completions per prompt during training. The group-level normalization ensures that even when absolute reward is low (hard problems), relative differences within the group still provide learning signal. This makes GRPO particularly well-suited for generating and learning from synthetic data on challenging reasoning tasks.

### 7.2 GRPO in DeepSeek-R1

DeepSeek-R1 (Section 5.1) uses GRPO as its primary RL algorithm. The combination of GRPO with verifiable rewards and long chain-of-thought generation produced the emergent reasoning behaviors that made DeepSeek-R1 a landmark result.

### 7.3 Theoretical Understanding

**Paper:** "Reinforcement Learning with Verifiable Rewards: GRPO's Effective Loss, Dynamics, and Success Amplification," arXiv 2025. ([arXiv:2503.06639](https://arxiv.org/abs/2503.06639))

Provides theoretical analysis of GRPO's loss landscape, training dynamics, and how it amplifies successful reasoning strategies. Shows that GRPO's group normalization creates an implicit curriculum where easier problems are upweighted early in training and harder problems receive more signal as the model improves.

**Paper:** "Demystifying Group Relative Policy Optimization: Its Policy Gradient is a U-Statistic," arXiv 2026. ([arXiv:2603.01162](https://arxiv.org/abs/2603.01162))

A 2026 theoretical contribution showing that GRPO's policy gradient estimator is a U-statistic, providing variance reduction guarantees and connecting GRPO to classical statistical estimation theory.

### 7.4 DAPO: Decoupled Clip and Dynamic Sampling Policy Optimization

**Paper:** Yu et al., "DAPO: An Open-Source LLM Reinforcement Learning System at Scale," arXiv 2025. ([arXiv:2503.14476](https://arxiv.org/abs/2503.14476))

DAPO identifies and addresses limitations of standard GRPO through four innovations:

1. **Clip-Higher:** Decouples the upper and lower clipping ranges in the PPO/GRPO objective. Standard GRPO uses a single epsilon (e.g., 0.2) for both; DAPO increases the upper range to 0.28, preventing *entropy collapse* (where the policy becomes too deterministic too quickly).
2. **Dynamic Sampling:** Adjusts the number of samples per prompt based on difficulty, improving efficiency.
3. **Token-Level Policy Gradient Loss:** Critical for long chain-of-thought RL where sequence lengths vary dramatically.
4. **Overlong Reward Shaping:** Reduces reward noise from excessively long outputs.

**Results:** DAPO achieves 50/100 on AIME 2024 using Qwen2.5-32B base, outperforming DeepSeek-R1's 47 with only 50% of the training steps. Fully open-sourced including code and data.

### 7.5 Scaf-GRPO

**Paper:** "Scaf-GRPO: Scaffolded Group Relative Policy Optimization for Enhancing LLM Reasoning," arXiv 2025. ([arXiv:2510.19807](https://arxiv.org/abs/2510.19807))

A progressive training framework that provides minimal guidance (scaffolding) only when the model's independent learning plateaus. Injects tiered in-prompt hints ranging from abstract concepts to concrete steps. Boosts Qwen2.5-Math-7B on AIME24 by 44.3% relative improvement over vanilla GRPO.

### 7.6 Training-Free GRPO

**Paper:** "Training-Free Group Relative Policy Optimization," arXiv 2025. ([arXiv:2510.08191](https://arxiv.org/abs/2510.08191))

Applies GRPO's group-relative ranking at inference time without any parameter updates. Using a frozen DeepSeek-V3.1-Terminus with merely 100 training samples yields performance superior to fully fine-tuning a 32B LLM, reducing cost from $800 to $8.

---

## 8. Online DPO Variants

Direct Preference Optimization (DPO; Rafailov et al., 2023) reformulates RLHF as a classification problem on preference pairs, eliminating the need for an explicit reward model. However, standard DPO is *offline*: it trains on a fixed dataset of preferences. Online and iterative DPO variants close the loop by generating synthetic preference data during training.

### 8.1 Iterative DPO

Multiple groups have shown that iterating DPO -- generating new on-policy responses, creating synthetic preference pairs, and retraining -- significantly outperforms single-round offline DPO. This is the approach used by Self-Rewarding Language Models (Section 3.2) and SPIN (Section 4.1).

In iterative reasoning DPO, models are trained with a variant of DPO including a negative log-likelihood loss for chosen responses, and the procedure iterates by generating new pairs and retraining. Reasoning performance improves over multiple iterations until saturation (typically 3--5 rounds).

### 8.2 Online DPO with AI Feedback

Several approaches generate on-policy completions and use either a reward model or an LLM judge to create synthetic preference pairs in real time:

- **OPTune** selectively regenerates only the lowest-rewarded responses and employs a weighted DPO objective prioritizing pairs with larger reward gaps, improving both generation and training efficiency.
- **Hybrid Preference Optimization (HPO)** integrates offline preference data with online exploration, achieving faster convergence than either alone. HPO theoretically establishes sample complexity bounds for policy optimization by relaxing concentrability conditions on offline data and introducing an optimistic regularizer for online feedback.

### 8.3 Notable DPO Variants (2024--2025)

| Variant | Innovation | Reference |
|---------|-----------|-----------|
| **TR-DPO** (Trust Region DPO) | Dynamically updates reference policy via soft/hard updates to prevent overoptimization | Gorbatovski et al., 2025 |
| **cDPO** (Contrastive DPO) | Token-level rewards with dynamic penalty weights on negative trajectories | Lin et al., 2024 |
| **M-DPO** (Multi-turn DPO) | MDP formulation for multi-turn reasoning with tool use | Xiong et al., 2025 |
| **BPO** (Balanced PO) | Addresses "Degraded Chosen Response" issue; +10--12% accuracy | 2025 |
| **ODPO** (DPO with Offset) | Adds margin offset to preference pairs | ACL Findings 2024 |

### 8.4 Comprehensive DPO Survey

**Paper:** "A Comprehensive Survey of Direct Preference Optimization: Datasets, Theories, Variants, and Applications," arXiv 2024. ([arXiv:2410.15595](https://arxiv.org/abs/2410.15595))

This survey catalogs over 50 DPO variants and provides a taxonomy of the space, covering dataset construction, theoretical foundations, algorithmic innovations, and application domains.

---

## 9. Rejection Sampling and Best-of-N Approaches

### 9.1 RAFT: Reward Ranked Fine-Tuning

**Paper:** Dong et al., "RAFT: Reward rAnked FineTuning for Generative Foundation Model Alignment," arXiv 2023/TMLR 2024. ([arXiv:2304.06767](https://arxiv.org/abs/2304.06767))

RAFT is the prototypical rejection-sampling-based alignment method:
1. Sample K responses from the current model for each prompt.
2. Score all responses with a reward model.
3. Fine-tune the model on the top-1 (or top-k) highest-reward responses.
4. Iterate.

**Advantages over PPO-based RLHF:** (a) SFT-like training is simpler and more stable. (b) Data generation and fine-tuning are decoupled, enabling efficient batching. (c) Fewer hyperparameters to tune. (d) Lower memory footprint (no value network, no on-policy gradient computation).

### 9.2 Best-of-N Sampling as an Inference-Time Baseline

Best-of-N (BoN) sampling generates N candidate responses and selects the one with the highest reward. While not a training method per se, BoN serves as a strong baseline for evaluating whether RL training provides benefit beyond simply sampling more at test time.

Recent work has shown that simple BoN with a good reward model can be surprisingly competitive with RL-trained models, especially when N is large. This has implications for the synthetic data pipeline: BoN-selected responses constitute high-quality synthetic data that can be used for subsequent SFT (a process sometimes called "distillation from inference-time compute").

### 9.3 RAFT as a Competitive Baseline to GRPO

**Paper:** "A Minimalist Approach to LLM Reasoning: from Rejection Sampling to Reinforce," arXiv 2025. ([arXiv:2504.11343](https://arxiv.org/abs/2504.11343))

This paper argues that RAFT (rejection sampling fine-tuning trained only on positively rewarded samples) matches or surpasses more complex RL approaches (GRPO, PPO) on math reasoning benchmarks. The authors propose **Reinforce-Rej**, which filters out both flawless and flawed prompts to improve training stability.

**Key insight:** GRPO's main advantage over simple rejection sampling arises from discarding prompts with entirely incorrect responses (where no learning signal exists), rather than from its reward normalization. Removing incorrect samples provides the largest gain in reward, highlighting their harmful impact on training.

---

## 10. Process and Outcome Reward Models

### 10.1 Outcome Reward Models (ORMs) vs. Process Reward Models (PRMs)

**Outcome Reward Models (ORMs)** provide a single scalar reward for the entire response. They are simple and align with RLVR (Section 5), but create sparse credit assignment: the model cannot localize which reasoning step was wrong.

**Process Reward Models (PRMs)** provide step-level (or even token-level) reward signals, enabling fine-grained credit assignment. PRMs have emerged as a central element in the toolkit for aligning and optimizing LLM reasoning.

### 10.2 Key PRM Papers

**Paper:** "The Lessons of Developing Process Reward Models in Mathematical Reasoning," arXiv 2025. ([arXiv:2501.07301](https://arxiv.org/abs/2501.07301))

Key finding: Monte Carlo (MC) estimation-based data synthesis for PRMs (the most common approach) typically yields inferior performance and generalization compared to LLM-as-a-judge and human annotation methods. The paper introduces a consensus filtering mechanism that integrates MC estimation with LLM-as-a-judge.

**Paper:** "Process Reward Models That Think," arXiv 2025. ([arXiv:2504.16828](https://arxiv.org/abs/2504.16828))

**Paper:** "R-PRM: Reasoning-Driven Process Reward Modeling," EMNLP 2025. ([arXiv:2503.21295](https://arxiv.org/abs/2503.21295))

### 10.3 Relevance to Synthetic Data

PRMs are critical for synthetic data quality: they enable filtering and ranking of intermediate reasoning steps in synthetically generated chains-of-thought. ReST-MCTS* (Section 6.7) uses process reward guidance to collect higher-quality synthetic reasoning traces. In "test-time scaling," PRMs score each candidate solution step-by-step, enabling better selection from synthetically generated candidates.

---

## 11. Notable 2025--2026 Papers on RL for Synthetic Data Generation

### 11.1 Open-Reasoner-Zero

**Paper:** "Open-Reasoner-Zero: An Open Source Approach to Scaling Up Reinforcement Learning on the Base Model," NeurIPS 2025. ([arXiv:2503.24290](https://arxiv.org/abs/2503.24290))

The first fully open-source implementation of large-scale reasoning-oriented RL training on a base model. Key findings:
- **Minimalist approach works:** Vanilla PPO with GAE (lambda=1, gamma=1), rule-based rewards, and *no* KL regularization is sufficient to scale both benchmark performance and response length.
- **Efficiency:** Achieves superior performance to DeepSeek-R1-Zero-Qwen-32B (on AIME2024, MATH500, GPQA Diamond) while requiring only 1/10 of the training steps.
- **Full release:** Source code, training data, and model weights are publicly available, enabling reproducible research.

### 11.2 SimpleRL

**Paper:** "SimpleRL: A Simple Framework for Training Reasoning LLMs with RL," 2025. ([github.com/hkust-nlp/simpleRL-reason](https://github.com/hkust-nlp/simpleRL-reason))

Demonstrates that simple RL training with only 8K examples achieves 10--20+ absolute points of accuracy improvement across diverse Qwen2.5 models (0.5B to 32B). Validates that RLVR scales down to small models and small data regimes.

### 11.3 QwQ-32B

**Paper:** Qwen Team, "QwQ-32B: Embracing the Power of Reinforcement Learning," 2025. ([Blog](https://qwenlm.github.io/blog/qwq-32b/))

A 32B-parameter model trained with outcome-based RL that achieves performance comparable to DeepSeek-R1 (671B parameters). Demonstrates the extreme efficiency of RL-generated synthetic reasoning data: a much smaller model can match a much larger one when trained with RL on verifiable tasks.

### 11.4 Beyond Model Collapse: Scaling Up with Synthesized Data Requires Reinforcement

**Paper:** ICLR 2025. Addresses the intersection of synthetic data generation and model collapse, arguing that RL-based filtering and reinforcement of synthetic data is necessary to avoid the degenerative effects of training on unfiltered model-generated data.

### 11.5 Synthetic Data Generation and Multi-Step Reinforcement Learning for Reasoning and Tool Use

**Paper:** OpenReview 2025. ([OpenReview](https://openreview.net/forum?id=oN9STRYQVa))

Proposes using multi-step RL to generate synthetic training data for reasoning tasks that involve external tool use, bridging the gap between pure reasoning and agentic capabilities.

### 11.6 Mitigating Reward Hacking in RLHF via Advantage Sign Robustness

**Paper:** arXiv 2026. ([arXiv:2604.02986](https://arxiv.org/abs/2604.02986))

A 2026 paper addressing the persistent problem of reward hacking in RLHF. Proposes robustness criteria for the sign of the advantage function to prevent the policy from exploiting reward model errors during synthetic data generation and training.

---

## 12. Model Collapse and Risks of Synthetic Data

### 12.1 The Model Collapse Problem

**Paper:** Shumailov et al., "AI models collapse when trained on recursively generated data," Nature 2024. ([Nature](https://www.nature.com/articles/s41586-024-07566-y))

Training generative models on their own outputs (or outputs of predecessors) can lead to *model collapse*: progressive loss of distributional diversity. The paper identifies two stages:
- **Early collapse:** Loss of tail information (minority data disappears).
- **Late collapse:** Loss of significant distributional mass, concept confusion, and variance reduction.

In LLMs, recursive training on synthetic text causes consistent decreases in lexical, syntactic, and semantic diversity.

### 12.2 Implications for RL-Based Synthetic Data

Model collapse is a fundamental risk for all self-training and RL-based methods described in this review. Mitigation strategies include:
- **Mixing real and synthetic data:** Maintaining a sufficient proportion of real data in the training mix.
- **Verification and filtering:** Using verifiable rewards (RLVR), reward models, or execution feedback to filter synthetic data, ensuring quality.
- **Diversity incentives:** Entropy bonuses in RL objectives (e.g., DAPO's Clip-Higher), or explicitly penalizing repetitive outputs.
- **Reinforcement as a corrective:** The ICLR 2025 paper "Beyond Model Collapse" argues that RL-based reinforcement of synthetic data is specifically what prevents collapse, as opposed to naive SFT on model outputs.

### 12.3 Reward Hacking and Overoptimization

**Paper:** "Scaling Laws for Reward Model Overoptimization in Direct Alignment Algorithms," NeurIPS 2024. ([arXiv:2406.02900](https://arxiv.org/abs/2406.02900))

When optimizing against a learned reward model, performance initially improves but eventually degrades as the policy exploits reward model errors (Goodhart's Law). The paper establishes scaling laws for this effect. Overoptimization exhibits a characteristic "hump-shaped" curve: gold reward rises, peaks, and falls while proxy reward increases monotonically.

RLVR (Section 5) partially sidesteps this issue by using *verifiable* rather than *learned* rewards, but is limited to domains where verification is possible (math, code, formal proofs). For open-ended tasks, reward overoptimization remains a major challenge.

---

## 13. Summary Table

| Paper / Method | Year | Method | Domain / Task | Key Findings |
|---|---|---|---|---|
| **InstructGPT** (Ouyang et al.) | 2022 | RLHF with PPO | Instruction following | 1.3B RLHF model preferred over 175B GPT-3; established 3-stage RLHF pipeline |
| **Constitutional AI** (Bai et al.) | 2022 | Critique-revision + AI preference labels | Safety / helpfulness | High-quality alignment with minimal human labels; AI-generated preferences effective |
| **STaR** (Zelikman et al.) | 2022 | Iterative rationale generation + filtering | Reasoning (arithmetic, QA) | Rationalization bootstraps reasoning; iterative improvement converges |
| **Self-Instruct** (Wang et al.) | 2023 | LLM-generated instruction data | Instruction following | 52K synthetic examples at <$500 approach ChatGPT quality (via Alpaca) |
| **ReST** (Gulcehre et al.) | 2023 | Offline RL with filtered self-generated data | Language modeling | More efficient than online RLHF; enables data reuse |
| **RAFT** (Dong et al.) | 2023 | Rejection sampling + SFT on top-k | Alignment | Simpler and more stable than PPO; competitive performance |
| **DPO** (Rafailov et al.) | 2023 | Direct preference optimization (offline) | Alignment | Removes need for explicit reward model; simpler than PPO |
| **RLAIF** (Lee et al.) | 2023 | RL from AI feedback | Summarization | AI feedback matches human feedback quality at lower cost |
| **SPIN** (Chen et al.) | 2024 | Self-play fine-tuning | General alignment | Outperforms DPO+GPT-4 data; provable convergence to target distribution |
| **Self-Rewarding LMs** (Yuan et al.) | 2024 | LLM-as-judge + iterative DPO | General alignment | Llama 2 70B surpasses Claude 2, Gemini Pro on AlpacaEval 2.0 |
| **DeepSeekMath / GRPO** (Shao et al.) | 2024 | Group relative policy optimization | Math reasoning | 51.7% on MATH; eliminates value network; memory efficient |
| **ReST-EM** (Singh et al.) | 2024 | EM-based self-training | Math (MATH) + code (APPS) | Model-generated data yields larger gains than human data |
| **V-STaR** (Hosseini et al.) | 2024 | STaR + DPO-trained verifier | Math reasoning | Uses both correct and incorrect solutions; improves test-time selection |
| **ReST-MCTS*** (Zhang et al.) | 2024 | Process reward + tree search self-training | Math reasoning | Step-level rewards without human annotation; higher quality traces |
| **Re-ReST** (Dou et al.) | 2024 | Reflection-reinforced self-training | Code agents | Reflector improves sample quality using execution feedback |
| **Meta-Rewarding LMs** (Wu et al.) | 2024 | LLM-as-meta-judge + iterative DPO | General alignment | Higher-order self-improvement via meta-judgment |
| **Model Collapse** (Shumailov et al.) | 2024 | Analysis of recursive self-training | Language modeling | Unfiltered synthetic data causes progressive diversity loss |
| **RM Overoptimization** (2024) | 2024 | Scaling laws for reward hacking | Alignment | Hump-shaped curve: gold reward degrades under overoptimization |
| **DPO Survey** (2024) | 2024 | Survey of 50+ DPO variants | Multiple | Comprehensive taxonomy of offline/online DPO methods |
| **DeepSeek-R1** (Guo et al.) | 2025 | RLVR with GRPO | Math, code, STEM | Pure RL yields emergent reasoning; SOTA on competition benchmarks |
| **Kimi k1.5** (Kimi Team) | 2025 | Long-context RL + partial rollouts | Multi-modal reasoning | 128K context RL; no MCTS/PRM needed; multi-modal |
| **DAPO** (Yu et al.) | 2025 | Decoupled clipping + dynamic sampling | Math reasoning | 50/100 AIME24 (beats R1); prevents entropy collapse; open-source |
| **Open-Reasoner-Zero** | 2025 | Vanilla PPO + rule-based rewards | Math reasoning | Matches R1-Zero quality at 1/10 training cost; fully open-source |
| **QwQ-32B** (Qwen Team) | 2025 | Outcome-based RL | Math, code, reasoning | 32B matches 671B DeepSeek-R1 performance |
| **SimpleRL** | 2025 | Simple RL with 8K examples | Math reasoning | 10--20 point gains across model sizes (0.5B--32B) |
| **Scaf-GRPO** | 2025 | Scaffolded GRPO with progressive hints | Math reasoning | 44.3% relative improvement over vanilla GRPO on AIME24 |
| **Training-Free GRPO** | 2025 | Inference-time GRPO (no training) | General tasks | Beats 32B fine-tuned model using 100 samples and $8 compute |
| **START** | 2025 | STaR + tool integration | Tool-augmented reasoning | Self-checking and self-debugging via external tools |
| **Reinforce-Rej** | 2025 | Rejection sampling + prompt filtering | Math reasoning | RAFT matches GRPO/PPO; removing bad samples is the main gain |
| **RLVR Theory** | 2025 | Theoretical analysis | Math, code | RLVR implicitly incentivizes correct intermediate reasoning |
| **SPPO** (Wu et al.) | 2025 | Self-play preference optimization | General alignment | Provable improvement over previous iteration in each self-play round |
| **PRM Lessons** | 2025 | Process reward model analysis | Math reasoning | MC-based PRM synthesis inferior to LLM-as-judge; consensus filtering helps |
| **ReST-RL** | 2025 | GRPO + test-time decoding | Code reasoning | Convergence of ReST self-training with modern RL techniques |
| **GRPO U-Statistic** | 2026 | Theoretical analysis | -- | GRPO gradient is a U-statistic; variance reduction guarantees |
| **Reward Hacking Robustness** | 2026 | Advantage sign robustness | Alignment | New robustness criteria to prevent reward exploitation |

---

## 14. Open Problems and Future Directions

### 14.1 Reward Specification for Open-Ended Tasks

RLVR has been transformative for math and code, where correctness is verifiable. However, most real-world LLM applications (creative writing, open-ended conversation, complex instruction following) lack verifiable reward signals. Key questions:
- How can we design verifiable proxies for open-ended quality?
- Can constitutional principles or rubric-based evaluation provide sufficiently reliable synthetic reward signals?
- How do we prevent reward hacking in domains where the reward model is necessarily imperfect?

### 14.2 Scaling Laws for RL Post-Training

While pre-training scaling laws (Chinchilla, etc.) are well-established, the scaling behavior of RL post-training is poorly understood:
- How does RL compute scale with model size, dataset size, and number of RL steps?
- Is there a "Chinchilla law" for GRPO or PPO training?
- How much RL compute is optimal relative to pre-training compute?

### 14.3 Sample Efficiency and Exploration

Current methods require generating many rollouts per prompt (GRPO uses groups of 8--64). Most of these are discarded. Improving sample efficiency through:
- Better exploration strategies (curiosity-driven exploration, novelty search)
- Curriculum learning and adaptive prompt difficulty (as in Scaf-GRPO)
- Partial rollout reuse (as in Kimi k1.5)

### 14.4 Multi-Turn and Agentic RL

Most current methods optimize single-turn generation. Extending RL-based self-training to multi-turn dialogues, tool use, and agentic workflows is an active frontier:
- M-DPO (multi-turn) and START (tool-augmented) are early steps.
- Credit assignment across turns is challenging.
- Environment design for multi-turn RL is an open problem.

### 14.5 Avoiding Model Collapse in Self-Training Loops

As models increasingly train on their own outputs, understanding and preventing model collapse is critical:
- What is the optimal ratio of real to synthetic data?
- Can RL-based filtering completely prevent collapse, or is real data always necessary?
- How do we detect early signs of collapse during training?

### 14.6 Unifying Policy and Value in a Single Model

Current RLHF/GRPO systems separate the policy (generation model) and the value/reward (reward model or verifier). Can these be unified? This is directly relevant to energy-based model approaches: a single EBM could assign lower energy to better outputs, serving as both generator (via Langevin sampling) and evaluator (via energy scores). This is an underexplored direction that connects to the motivation of this repository's research on EBMs for Lean 4 theorem proving.

### 14.7 Process Supervision Without Human Annotation

Training PRMs typically requires step-level labels, which are expensive to collect. Methods like ReST-MCTS* attempt to avoid this via tree search, but the quality gap relative to human-annotated PRMs remains. Developing reliable, fully synthetic process supervision is a key open problem.

### 14.8 Theoretical Foundations

Despite the empirical success of RLVR and GRPO, theoretical understanding lags behind:
- Why does RLVR incentivize correct intermediate reasoning (not just correct answers)?
- What are the convergence guarantees for iterative self-training methods?
- Under what conditions does self-play converge to the optimal policy vs. a suboptimal equilibrium?

Papers like RL-STaR (Section 6.3) and the GRPO dynamics analysis (Section 7.3) are early contributions, but much remains open.

### 14.9 RL for Theorem Proving

Directly relevant to this project: using RL with formal verification as the reward signal (does the proof compile in Lean 4?) for synthetic tactic generation. This is a natural fit for RLVR because the reward is perfectly verifiable. Key challenges include the extremely sparse reward signal (most tactic sequences fail), the combinatorial search space, and the need for long-horizon credit assignment across multi-step proofs.

---

## 15. References

1. Ouyang, L., et al. (2022). Training language models to follow instructions with human feedback. NeurIPS. [arXiv:2203.02155](https://arxiv.org/abs/2203.02155)
2. Bai, Y., et al. (2022). Constitutional AI: Harmlessness from AI Feedback. [arXiv:2212.08073](https://arxiv.org/abs/2212.08073)
3. Zelikman, E., et al. (2022). STaR: Bootstrapping Reasoning With Reasoning. NeurIPS. [arXiv:2203.14465](https://arxiv.org/abs/2203.14465)
4. Wang, Y., et al. (2023). Self-Instruct: Aligning Language Models with Self-Generated Instructions. ICLR 2024. [arXiv:2212.10560](https://arxiv.org/abs/2212.10560)
5. Gulcehre, C., et al. (2023). Reinforced Self-Training (ReST) for Language Modeling. [arXiv:2308.08998](https://arxiv.org/abs/2308.08998)
6. Dong, H., et al. (2023). RAFT: Reward rAnked FineTuning for Generative Foundation Model Alignment. [arXiv:2304.06767](https://arxiv.org/abs/2304.06767)
7. Rafailov, R., et al. (2023). Direct Preference Optimization: Your Language Model is Secretly a Reward Model. NeurIPS. [arXiv:2305.18290](https://arxiv.org/abs/2305.18290)
8. Lee, H., et al. (2023). RLAIF: Scaling Reinforcement Learning from Human Feedback with AI Feedback. [arXiv:2309.00267](https://arxiv.org/abs/2309.00267)
9. Chen, Z., et al. (2024). Self-Play Fine-Tuning Converts Weak Language Models to Strong Language Models. ICML. [arXiv:2401.01335](https://arxiv.org/abs/2401.01335)
10. Yuan, W., et al. (2024). Self-Rewarding Language Models. ICML. [arXiv:2401.10020](https://arxiv.org/abs/2401.10020)
11. Shao, Z., et al. (2024). DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models. [arXiv:2402.03300](https://arxiv.org/abs/2402.03300)
12. Singh, A., et al. (2024). Beyond Human Data: Scaling Self-Training for Problem-Solving with Language Models. TMLR. [arXiv:2312.06585](https://arxiv.org/abs/2312.06585)
13. Hosseini, A., et al. (2024). V-STaR: Training Verifiers for Self-Taught Reasoners. COLM. [arXiv:2402.06457](https://arxiv.org/abs/2402.06457)
14. Zhang, D., et al. (2024). ReST-MCTS*: LLM Self-Training via Process Reward Guided Tree Search. NeurIPS. [OpenReview](https://openreview.net/forum?id=8rcFOqEud5)
15. Dou, S., et al. (2024). Re-ReST: Reflection-Reinforced Self-Training for Language Agents. EMNLP. [arXiv:2406.01495](https://arxiv.org/abs/2406.01495)
16. Shumailov, I., et al. (2024). AI models collapse when trained on recursively generated data. Nature. [Nature](https://www.nature.com/articles/s41586-024-07566-y)
17. (2024). Scaling Laws for Reward Model Overoptimization in Direct Alignment Algorithms. NeurIPS. [arXiv:2406.02900](https://arxiv.org/abs/2406.02900)
18. Wu, T., et al. (2024). Meta-Rewarding Language Models: Self-Improving Alignment with LLM-as-a-Meta-Judge. [arXiv:2407.19594](https://arxiv.org/abs/2407.19594)
19. Luong, T., et al. (2024). RL-STaR: Theoretical Analysis of Reinforcement Learning Frameworks for Self-Taught Reasoner. [arXiv:2410.23912](https://arxiv.org/abs/2410.23912)
20. (2024). A Comprehensive Survey of Direct Preference Optimization. [arXiv:2410.15595](https://arxiv.org/abs/2410.15595)
21. Guo, D., et al. (2025). DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning. Nature. [arXiv:2501.12948](https://arxiv.org/abs/2501.12948)
22. Kimi Team (2025). Kimi k1.5: Scaling Reinforcement Learning with LLMs. [arXiv:2501.12599](https://arxiv.org/abs/2501.12599)
23. Yu, Q., et al. (2025). DAPO: An Open-Source LLM Reinforcement Learning System at Scale. [arXiv:2503.14476](https://arxiv.org/abs/2503.14476)
24. (2025). Open-Reasoner-Zero: An Open Source Approach to Scaling Up Reinforcement Learning on the Base Model. NeurIPS. [arXiv:2503.24290](https://arxiv.org/abs/2503.24290)
25. (2025). Reinforcement Learning with Verifiable Rewards: GRPO's Effective Loss, Dynamics, and Success Amplification. [arXiv:2503.06639](https://arxiv.org/abs/2503.06639)
26. (2025). START: Self-Taught Reasoner with Tools. [arXiv:2503.04625](https://arxiv.org/abs/2503.04625)
27. (2025). A Minimalist Approach to LLM Reasoning: from Rejection Sampling to Reinforce. [arXiv:2504.11343](https://arxiv.org/abs/2504.11343)
28. (2025). The Lessons of Developing Process Reward Models in Mathematical Reasoning. [arXiv:2501.07301](https://arxiv.org/abs/2501.07301)
29. (2025). Scaf-GRPO: Scaffolded Group Relative Policy Optimization for Enhancing LLM Reasoning. [arXiv:2510.19807](https://arxiv.org/abs/2510.19807)
30. (2025). Training-Free Group Relative Policy Optimization. [arXiv:2510.08191](https://arxiv.org/abs/2510.08191)
31. (2025). ReST-RL: Achieving Accurate Code Reasoning of LLMs with Optimized Self-Training and Decoding. [arXiv:2508.19576](https://arxiv.org/abs/2508.19576)
32. (2025). Reinforcement Learning with Verifiable Rewards Implicitly Incentivizes Correct Reasoning in Base LLMs. [arXiv:2506.14245](https://arxiv.org/abs/2506.14245)
33. Wu, Z., et al. (2025). Self-Play Preference Optimization for Language Model Alignment. ICLR. [OpenReview](https://openreview.net/forum?id=a3PmRgAB5T)
34. Qwen Team (2025). QwQ-32B: Embracing the Power of Reinforcement Learning. [Blog](https://qwenlm.github.io/blog/qwq-32b/)
35. Qwen Team (2024). Qwen2.5 Technical Report. [arXiv:2412.15115](https://arxiv.org/abs/2412.15115)
36. (2026). Demystifying Group Relative Policy Optimization: Its Policy Gradient is a U-Statistic. [arXiv:2603.01162](https://arxiv.org/abs/2603.01162)
37. (2026). Mitigating Reward Hacking in RLHF via Advantage Sign Robustness. [arXiv:2604.02986](https://arxiv.org/abs/2604.02986)
