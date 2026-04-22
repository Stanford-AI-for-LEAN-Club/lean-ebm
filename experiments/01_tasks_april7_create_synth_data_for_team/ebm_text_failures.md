# Energy-Based Models for Text and Language: A Survey of Methods, Failure Modes, and Open Problems

## Table of Contents

1. [Introduction: What Are Energy-Based Models?](#1-introduction-what-are-energy-based-models)
2. [Key Papers Applying EBMs to Text](#2-key-papers-applying-ebms-to-text)
3. [Failure Modes: Why EBMs Underperform for Text](#3-failure-modes-why-ebms-underperform-for-text)
4. [Why Autoregressive Models Dominate](#4-why-autoregressive-models-dominate)
5. [Open Problems and Potential Paths Forward](#5-open-problems-and-potential-paths-forward)
6. [Relevance to EBMs for Lean 4 Theorem Proving](#6-relevance-to-ebms-for-lean-4-theorem-proving)
7. [References](#7-references)

---

## 1. Introduction: What Are Energy-Based Models?

### 1.1 Definition and Formalism

An **energy-based model (EBM)** defines a probability distribution over inputs $x$ through a scalar-valued energy function $E_\theta(x)$:

$$p_\theta(x) = \frac{\exp(-E_\theta(x))}{Z(\theta)}, \quad Z(\theta) = \int \exp(-E_\theta(x)) \, dx$$

where $Z(\theta)$ is the **partition function** (normalizing constant). Lower energy corresponds to higher probability. The model assigns a single scalar to any input configuration, and the Boltzmann distribution converts these energies into probabilities. Unlike models that directly parameterize $p(x)$, EBMs only need to parameterize the unnormalized density $\exp(-E_\theta(x))$, which gives them enormous architectural flexibility -- the energy function can be any neural network that maps inputs to a scalar.

### 1.2 Why EBMs Are Attractive for Language

EBMs have several theoretically appealing properties for language modeling:

**Unified scoring.** A single energy function can serve as both a generator (by sampling low-energy configurations) and a discriminator/critic (by directly evaluating the energy of a given sequence). In theorem proving, this could unify the policy network (which generates tactics) and the value network (which evaluates proof states) into one model.

**Bidirectional context.** Autoregressive models factor $p(x_1, \ldots, x_T) = \prod_t p(x_t \mid x_{<t})$, which imposes a strict left-to-right generation order. EBMs define a joint energy $E_\theta(x_1, \ldots, x_T)$ over the entire sequence, naturally capturing bidirectional dependencies without causal masking constraints.

**Flexible generation.** Because EBMs define an energy landscape rather than a sequential generation procedure, they can in principle support:
- Iterative refinement (start from a draft, improve via gradient descent)
- Parallel generation of all tokens simultaneously
- Infilling and editing (condition on any subset of positions)
- Multi-modal composition (add energy functions for different constraints)

**Compositionality.** Energy functions can be composed by addition: $E_\text{combined}(x) = E_1(x) + E_2(x)$, which corresponds to multiplying the (unnormalized) distributions. This is a natural framework for imposing multiple soft constraints (e.g., fluency + factuality + style).

**Dynamic computation.** The number of Langevin/MCMC steps at inference time is adjustable. Harder problems can receive more computation -- a property reminiscent of System 2 thinking.

### 1.3 The Core Challenge

Despite these attractive properties, EBMs face a fundamental tension when applied to language: **text is discrete, high-dimensional, and combinatorially structured**, while the standard EBM training and sampling toolkit (contrastive divergence, Langevin dynamics, score matching) was developed for continuous data. The partition function $Z(\theta)$ is intractable to compute exactly, and MCMC sampling in discrete spaces is slow and difficult to scale. These challenges have prevented EBMs from competing with autoregressive models on standard language benchmarks.

---

## 2. Key Papers Applying EBMs to Text

### 2.1 Residual Energy-Based Models for Text Generation (Bakhtin et al., 2021)

**Paper:** "Residual Energy-Based Models for Text" (Bakhtin, Deng, et al., 2021)

**Key idea:** Rather than training an EBM from scratch, define a **residual energy** on top of an existing autoregressive (AR) model. The joint model is:

$$p_\theta(x) \propto p_{\text{AR}}(x) \cdot \exp(-E_\theta(x))$$

The AR model provides a strong base distribution, and the EBM residual corrects it. This is equivalent to an energy $E_\text{total}(x) = -\log p_{\text{AR}}(x) + E_\theta(x)$.

**Training:** Uses noise-contrastive estimation (NCE) with samples from the AR model as the noise distribution. This avoids the need for MCMC during training entirely.

**Results:** Improved perplexity and generation quality over the base AR model on text datasets (Wikitext-103, Toronto Book Corpus). Showed that the residual EBM can capture long-range dependencies that the AR model misses.

**Limitations:** At generation time, sampling from the joint model still requires MCMC (importance-weighted sampling or rejection sampling using the AR model as the proposal). This makes generation significantly slower than pure AR decoding. The improvement is modest, and the complexity overhead is substantial.

### 2.2 ELECTRIC and ELECTRA-Style Discriminative Models

**Paper:** "ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators" (Clark et al., 2020)

**Key idea:** ELECTRA is not strictly an EBM, but it is philosophically related. Instead of training a masked language model to predict missing tokens (like BERT), ELECTRA trains a **discriminator** to detect which tokens in a sequence have been replaced by a small generator network. The discriminator learns an energy-like scoring function over token positions.

**Connection to EBMs:** The replaced-token detection objective trains the model to assign a scalar score (real vs. replaced) to each position, which can be interpreted as a local energy. Clark et al. (2020) showed this is more sample-efficient than MLM pre-training because the discriminator receives a training signal at every token position, not just the masked 15%.

**ELECTRIC (Clark et al., 2022):** Extended ELECTRA explicitly to the energy-based framework. Showed that the ELECTRA discriminator implicitly defines an energy-based model over token sequences and connected it to noise-contrastive estimation.

**Results:** ELECTRA matches or exceeds BERT performance with significantly less compute. ELECTRIC demonstrated improved likelihood estimation.

**Limitations:** These models are primarily useful for scoring and classification, not generation. Converting the discriminator into a generative model requires Gibbs sampling or similar MCMC procedures, which are slow and do not produce competitive generation quality.

### 2.3 Energy-Based Models for Text Generation (Deng et al., 2020)

**Paper:** "Residual Energy-Based Models for Text Generation" and related work by Yuntian Deng, Anton Bakhtin, et al.

**Key idea:** Explored several approaches to using EBMs directly for text generation:
- Training EBMs with contrastive divergence on text
- Using Gibbs sampling to generate from discrete EBMs
- Combining EBMs with autoregressive models as proposal distributions

**Training approaches explored:**
1. **Contrastive divergence (CD):** Generate negative samples via short-run MCMC (typically Gibbs sampling), then update the model to assign lower energy to real data and higher energy to generated samples. Standard CD loss: $\mathcal{L} = \mathbb{E}_{x \sim p_{\text{data}}}[E_\theta(x)] - \mathbb{E}_{x \sim p_\theta}[E_\theta(x)]$.
2. **Score matching variants:** Adapt score matching (which avoids computing $Z(\theta)$) to discrete sequences using continuous relaxations.
3. **Noise-contrastive estimation (NCE):** Use a known noise distribution (e.g., unigram or AR model) and train the EBM to distinguish real data from noise.

**Results:** Showed that EBMs can learn meaningful energy landscapes over text, but generation quality lagged behind comparable AR models. Gibbs sampling from the learned EBM produces diverse but often incoherent text.

### 2.4 Joint Energy Models (JEM) and Their Text Extensions

**Paper:** "Your Classifier is Secretly an Energy Based Model and You Should Treat it Like One" (Grathwohl et al., 2020)

**Key idea:** Reinterpret the logits of a standard classifier as an energy function. For a classifier $f_\theta(x)$ with logits for classes $y$, define $E_\theta(x) = -\text{LogSumExp}_y f_\theta(x)[y]$. This turns any classifier into a generative model via EBM sampling.

**Text extensions:** Several works attempted to apply JEM to text classifiers (e.g., sentiment classifiers as EBMs over text). The idea is to jointly train a model for classification and generation.

**Results:** JEM works reasonably well for images (CIFAR-10, SVHN) where SGLD sampling is feasible. For text, results are limited because:
- Gibbs sampling in token space is slow and mixes poorly
- The energy landscape over discrete sequences has many local optima separated by high-energy barriers
- Joint training is unstable, with the generative and discriminative objectives often conflicting

### 2.5 Non-Autoregressive Generation with Energy Models

**Papers:**
- "Non-Autoregressive Machine Translation with Latent Alignments" (Saharia et al., 2020)
- "CMLM: Conditional Masked Language Models" (Ghazvininejad et al., 2019)
- "Directed Acyclic Transformer" (Huang et al., 2022)

**Key idea:** Non-autoregressive translation (NAT) generates all tokens in parallel, avoiding the sequential bottleneck of AR models. Some NAT approaches use iterative refinement that resembles Langevin-like dynamics: start with an initial (possibly random) sequence and repeatedly refine it.

**Connection to EBMs:** Iterative NAT methods like CMLM and Mask-Predict can be viewed as performing a form of discrete MCMC: at each step, the model masks some positions and re-predicts them given the rest. This is analogous to Gibbs sampling from an EBM.

**Results:** NAT models achieve impressive speedups (5-15x faster than AR at inference) but consistently suffer a quality gap of 1-5 BLEU points on machine translation benchmarks compared to AR models. Knowledge distillation from AR teacher models is required to make NAT competitive, which means NAT effectively depends on AR models.

**Failure modes specific to NAT:**
- **Multi-modality problem:** When multiple valid translations exist, NAT models mix modes and produce garbled outputs (e.g., "I want to go want go home" combining "I want to go" and "I want to go home").
- **Token repetition:** Without left-to-right factorization, NAT models often repeat tokens.
- **Conditional independence assumption:** Most NAT models assume tokens are conditionally independent given the source, which is a poor approximation for language.

### 2.6 EBMs for Scoring and Reranking in NLP

**Papers:**
- "Discriminative Reranking for Neural Machine Translation" (Lee et al., 2021)
- "Energy-Based Reranking" (Bhatt et al., 2023)

**Key idea:** Rather than using EBMs for direct generation, use them as **rerankers**: first generate a diverse candidate set using an AR model (e.g., via beam search or sampling), then use an EBM to score and rerank the candidates. This sidesteps the sampling problem entirely.

**Training:** The EBM is trained to assign lower energy to high-quality outputs (e.g., reference translations or human-preferred completions) and higher energy to lower-quality candidates.

**Results:** Reranking with learned energy functions consistently improves over the AR model's own ranking. Gains of 0.5-2 BLEU points are typical in machine translation. In summarization and dialogue, EBM rerankers can improve factual consistency and relevance.

**Why this works:** Reranking completely avoids the MCMC sampling problem. The EBM only needs to evaluate energy at a finite set of candidate points, which is trivially parallelizable. This makes EBMs competitive as scorers/critics even when they cannot compete as generators.

**Limitations:** The quality ceiling is bounded by the diversity of the AR model's candidate set. If the AR model never generates a good candidate, the reranker cannot find it.

### 2.7 CALM: Confidence-Adaptive Language Modeling

**Paper:** "Your Language Model is Secretly an Energy-Based Model" (variant: "CALM: Confidence-Adaptive Language Modeling")

Multiple related works explore the connection between autoregressive language models and energy-based models:

**Key insight:** The log-probability assigned by an autoregressive LM to a sequence can be interpreted as (negative) energy. $E(x) = -\sum_t \log p(x_t \mid x_{<t})$. Under this view, any AR-LM is already an EBM, but one with a very specific factored structure.

**CALM and adaptive computation:** Some approaches use energy/confidence scores from the LM to adaptively allocate computation -- exiting early for easy tokens and spending more computation on hard ones. This connects to the EBM idea of "more Langevin steps for harder problems."

**Residual EBMs as LM corrections (Residual EBMs, revisited):** Bakhtin et al. and subsequent works (2021-2023) show that adding a bidirectional residual energy term to an AR LM's log-probability consistently improves the model. The residual captures global coherence that the left-to-right factorization misses.

### 2.8 Recent Work (2024-2026)

**DPO and RLHF as Implicit EBMs (Rafailov et al., 2024; follow-ups):**
Direct Preference Optimization (DPO) implicitly defines an energy function: the reward model in RLHF can be viewed as an energy function over completions, and the DPO-trained policy approximates sampling from the Boltzmann distribution over this energy landscape. This connection has been made explicit in several 2024-2025 papers:
- The KL-constrained optimization in RLHF corresponds to sampling from $p(y|x) \propto p_{\text{ref}}(y|x) \exp(r(x,y)/\beta)$, which is exactly a residual EBM with the reference policy as the base distribution.
- This explains why DPO works: it is training an implicit EBM without ever needing to sample from the EBM directly.

**Energy-Based Diffusion Language Models (2024-2025):**
Several groups have explored combining discrete diffusion models with energy-based training:
- MDLM (Masked Diffusion Language Models) and related approaches (Sahoo et al., 2024; Shi et al., 2024) use iterative denoising that can be viewed as performing approximate MCMC in discrete space.
- Score Entropy Discrete Diffusion (SEDD, Lou et al., 2024) directly targets the score function of a discrete distribution.
- These approaches narrow but do not close the gap with AR models on language modeling benchmarks. As of 2025-2026, the best discrete diffusion language models achieve perplexities within 10-15% of comparably sized AR models on standard benchmarks, but generation quality (measured by human evaluation or downstream task performance) still lags.

**EBMs for Code and Formal Reasoning (2025-2026):**
- Preliminary work on using energy functions to score candidate proofs and code completions, typically in a reranking or verifier setup.
- AlphaProof (DeepMind, 2024) and related systems use value functions that are conceptually energy-based, though they are implemented as separate neural networks rather than as classical EBMs.
- The lean-ebm project (this repository) is part of this line of research: using EBMs with Langevin dynamics to sample proof tactics for Lean 4.

**Classifier-Free Guidance as Energy Composition (2024-2025):**
The connection between classifier-free guidance (widely used in diffusion models for images) and energy-based composition has been formalized. This has inspired text generation approaches that compose multiple energy functions (e.g., topic + style + factuality) to guide generation.

---

## 3. Failure Modes: Why EBMs Underperform for Text

This is the central section of this survey. We organize the failure modes from most fundamental to most practical.

### 3.1 Partition Function Intractability for Discrete Sequences

**The fundamental problem:** For a vocabulary of size $V$ and sequence length $T$, the partition function is a sum over $V^T$ configurations:

$$Z(\theta) = \sum_{x \in \mathcal{V}^T} \exp(-E_\theta(x))$$

For a typical language model with $V = 32{,}000$ and $T = 512$, this is a sum over $32{,}000^{512} \approx 10^{2{,}307}$ terms -- utterly intractable.

**Why this matters for training:**
- Maximum likelihood training requires $\nabla_\theta \log Z(\theta)$, which equals $\mathbb{E}_{p_\theta}[\nabla_\theta E_\theta(x)]$. Computing this expectation requires sampling from $p_\theta$, creating a chicken-and-egg problem.
- Contrastive divergence approximates this gradient using short-run MCMC, but short-run MCMC in discrete spaces produces biased, high-variance gradient estimates (see Section 3.2).
- NCE avoids $Z(\theta)$ but requires a noise distribution close to $p_\theta$, which itself requires knowing $p_\theta$.

**Comparison to images:** For continuous images, the partition function is an integral rather than a sum, but it is equally intractable. However, continuous EBMs can use **Langevin dynamics** -- gradient descent on $E_\theta(x)$ with Gaussian noise -- to produce approximate samples. This is impossible for discrete text because gradients with respect to discrete tokens are undefined.

**Comparison to AR models:** Autoregressive models completely avoid this problem. By factoring $p(x) = \prod_t p(x_t | x_{<t})$, each conditional is over $V$ choices (a simple softmax), and the partition function is implicitly 1 by construction.

### 3.2 MCMC Sampling in Discrete, High-Dimensional Text Space

**The sampling problem is arguably the single biggest obstacle.** Even if we train a perfect energy function, we need to sample from it at inference time. For text, the standard approaches all have severe limitations:

**Gibbs sampling:** The most natural discrete MCMC method. At each step, select a position $t$ and resample $x_t$ from $p(x_t | x_{\setminus t}) \propto \exp(-E_\theta(x_{\setminus t}, x_t))$, which requires $V$ energy evaluations (one per vocabulary token). Problems:
- **Mixing time:** For sequences of length $T$, Gibbs sampling must visit and resample each position many times to reach the stationary distribution. Empirically, the mixing time scales polynomially or worse with $T$.
- **Multi-modality:** If the energy landscape has multiple modes separated by high-energy barriers (common for text -- "the cat sat" and "the dog stood" are both valid but separated by many token-swap operations), Gibbs sampling gets trapped in local modes for exponentially long times.
- **Computational cost:** Each Gibbs step requires $V$ forward passes through the energy network (one per vocabulary token at the selected position). For $V = 32{,}000$, this is extremely expensive.

**Metropolis-Hastings:** Propose a new sequence $x'$ from some proposal distribution $q(x'|x)$ and accept with probability $\min(1, \frac{p(x') q(x|x')}{p(x) q(x'|x)})$. Problems:
- Most proposals (e.g., random token replacement) will be rejected because random perturbations to coherent text almost always increase energy.
- Designing good proposal distributions for text is essentially as hard as the original generation problem.

**Langevin dynamics in continuous relaxation:** Map discrete tokens to continuous embeddings, run Langevin dynamics in embedding space, then project back to discrete tokens. Problems:
- The projection step (argmax or sampling from softmax over distances to embedding vectors) introduces errors.
- The continuous relaxation may not preserve the discrete structure of language.
- Gradients through the embedding-to-token projection are zero almost everywhere (the argmax is piecewise constant).

**Gumbel-Softmax and straight-through estimators:** Use differentiable relaxations of discrete sampling. Problems:
- Temperature must be annealed toward zero to approach true discrete samples, but low temperature leads to high-variance gradients.
- The straight-through estimator is biased and can lead to training instability.

### 3.3 Mode Collapse and Poor Diversity

**Mode collapse in EBM training** manifests differently than in GANs but is equally problematic:

**Negative sample quality:** Contrastive divergence trains the EBM by pushing up the energy of "negative" samples (generated by MCMC) and pulling down the energy of "positive" samples (from the data). If the MCMC chain does not mix well (see Section 3.2), the negative samples come from a small region of the space, and the EBM only learns to assign high energy to that region, leaving vast regions of the space with inappropriately low energy.

**Energy degeneracy:** The EBM can learn an energy function that is nearly flat over large regions of the input space, assigning similar energy to many very different sequences. This happens when training fails to provide informative negative samples that force the model to discriminate between fine-grained quality differences.

**Diversity-quality tradeoff:** Even when EBM training succeeds, sampling tends to produce either:
- High-quality but low-diversity outputs (if sampling temperature is low / many MCMC steps), or
- High-diversity but low-quality outputs (if temperature is high / few MCMC steps).
Autoregressive models manage this tradeoff much more gracefully through temperature scaling on the per-token softmax.

### 3.4 Training Instability

**Contrastive divergence instability:** The CD gradient estimate is:

$$\nabla_\theta \mathcal{L} \approx \nabla_\theta E_\theta(x_{\text{real}}) - \nabla_\theta E_\theta(x_{\text{fake}})$$

where $x_{\text{fake}}$ comes from short-run MCMC. This estimate is biased because short-run MCMC does not produce samples from $p_\theta$. As training progresses:
1. The model changes, so the distribution it defines changes.
2. The MCMC chain, initialized from the previous iteration's samples, may no longer be near a mode of the new distribution.
3. The gradient estimates become increasingly inaccurate, leading to oscillation or divergence.

**Energy scale drift:** Without the constraint that $Z(\theta) = 1$, the energy function can drift to arbitrarily large or small values. Regularization (e.g., penalizing $E_\theta(x)^2$) helps but introduces hyperparameters that are difficult to tune.

**Gradient through MCMC:** Some training methods (like the EBT approach used in this repository) backpropagate through the Langevin sampling process. This requires either:
- Backprop through all MCMC steps (memory-intensive, vanishing/exploding gradients for many steps), or
- Backprop through only the last step (biased gradient, loses information about earlier steps).

The lean-ebm codebase directly confronts this tradeoff: `GradientMethod.PER_RUN` (backprop through all steps) is noted as often not working, while `GradientMethod.PER_STEP` (last step only) does work but with limited gradient information.

**Spectral instability:** Du and Mordatch (2019) showed that EBM training can become spectrally unstable: small perturbations to the energy function lead to large changes in the implied distribution. This is particularly severe for high-dimensional inputs like text sequences.

### 3.5 Exposure Bias Analogues

**In autoregressive models,** exposure bias refers to the train-test mismatch: at training time, the model sees ground-truth prefixes, but at test time, it conditions on its own (potentially erroneous) outputs.

**EBMs have an analogous problem:** The energy function is trained on real data and (short-run) MCMC samples, but at test time, it must evaluate the energy of sequences produced by a long MCMC chain that may visit regions of the space never seen during training. The energy function's behavior in these out-of-distribution regions is unpredictable -- it may assign inappropriately low energy to nonsensical sequences.

**Compounding errors in iterative refinement:** When EBMs are used for iterative text generation (start from random tokens, refine via MCMC), errors compound: a bad token choice at step $t$ changes the energy landscape for all subsequent refinement steps. Unlike AR models, where each token is committed and the model adapts, EBM refinement can oscillate between different error patterns.

### 3.6 Scaling Difficulties

**Parameter efficiency:** Autoregressive transformers scale remarkably well: doubling parameters reliably improves performance across a wide range of tasks (scaling laws from Kaplan et al., 2020; Hoffmann et al., 2022). EBMs have no comparable scaling story:
- There is no established scaling law for EBM performance as a function of model size or data.
- Training instability (Section 3.4) often worsens with scale, because larger models define more complex energy landscapes that are harder to sample from.
- The cost of MCMC sampling scales with model size (each energy evaluation requires a forward pass), making large EBMs prohibitively expensive at inference time.

**Data efficiency:** AR models are trained on every token prediction in the training set, receiving dense supervision. EBMs receive sparse supervision -- the training signal depends on the quality of negative samples, which may not cover the data distribution well.

**Hardware utilization:** AR training is embarrassingly parallel within a sequence (teacher forcing). EBM training with MCMC requires sequential sampling steps that cannot be fully parallelized across time steps, leading to poor GPU utilization.

**Infrastructure:** The entire modern LLM infrastructure (FlashAttention, KV caches, speculative decoding, tensor parallelism strategies) is optimized for autoregressive generation. EBM inference with MCMC sampling cannot leverage most of these optimizations.

### 3.7 Lack of Efficient Exact Sampling

**The gold standard for generative models is exact sampling:** given parameters $\theta$, produce a sample $x$ that is exactly distributed according to $p_\theta(x)$. Autoregressive models achieve this trivially via ancestral sampling (sample each token from its conditional distribution in sequence).

**EBMs cannot do exact sampling** in general. All practical sampling methods are approximate:
- MCMC methods are asymptotically exact but require infinite time to converge.
- Importance sampling from a proposal distribution requires knowing a good proposal (which is as hard as the original problem).
- Variational methods (training a separate generator to approximate $p_\theta$) add complexity and introduce approximation error.

This means that **even a perfectly trained EBM cannot be evaluated fairly** -- apparent failures may be due to bad sampling rather than a bad energy function.

### 3.8 The Discreteness Gap: Continuous vs. Discrete

Much of the EBM success story comes from continuous domains (images, physics simulations, molecular dynamics). The transfer to discrete text is fundamentally harder because:

**No gradients through discrete tokens.** Langevin dynamics requires $\nabla_x E_\theta(x)$, but for discrete $x$, this gradient does not exist. Workarounds (continuous relaxations, straight-through estimators, score functions) all introduce bias or variance.

**Combinatorial explosion of neighbors.** In continuous space, a small perturbation $x + \epsilon$ is always near $x$. In discrete token space, any single-token change can drastically alter meaning ("not" vs. "now", "can" vs. "can't"). The energy landscape over discrete sequences is therefore rugged and discontinuous, making gradient-based or local-search-based sampling ineffective.

**No meaningful interpolation.** In image space, the midpoint between two images is a blended image. In token space, the midpoint between two sentences is meaningless. This breaks many EBM techniques that rely on interpolation and smooth paths through the data manifold.

---

## 4. Why Autoregressive Models Dominate

### 4.1 Tractable Likelihood

AR models decompose the joint distribution into a product of conditionals:

$$p(x_1, \ldots, x_T) = \prod_{t=1}^T p(x_t \mid x_1, \ldots, x_{t-1})$$

Each conditional is a softmax over $V$ tokens, whose normalizing constant is trivially computed. This means:
- **Exact likelihood computation** in $O(T)$ forward passes.
- **Exact gradient computation** via standard backpropagation.
- **No partition function** to estimate or approximate.

### 4.2 Efficient, Exact Sampling

Ancestral sampling from an AR model is trivial:
1. Sample $x_1 \sim p(x_1)$
2. Sample $x_t \sim p(x_t \mid x_1, \ldots, x_{t-1})$ for $t = 2, \ldots, T$

Each step requires one forward pass and one categorical sample. The total cost is $O(T)$ forward passes -- or $O(1)$ wall-clock time with KV caching and speculative decoding.

### 4.3 Scaling Laws

Kaplan et al. (2020) and Hoffmann et al. (2022) established that AR transformer performance improves predictably with scale:

$$L(N) = \left(\frac{N_c}{N}\right)^{\alpha_N}$$

where $L$ is loss, $N$ is parameter count, and $\alpha_N \approx 0.076$. This predictability has enabled the systematic scaling of LLMs from millions to trillions of parameters, with reliable performance gains at each step.

No comparable scaling law exists for EBMs, making investment in EBM scaling a high-risk proposition.

### 4.4 Training Stability and Simplicity

AR model training is remarkably stable:
- The training objective (cross-entropy) is convex in the logits.
- Teacher forcing provides dense, unbiased gradients at every token position.
- Standard optimizers (Adam, AdaFactor) work reliably without extensive hyperparameter tuning.
- Training does not require MCMC, contrastive samples, or energy regularization.

### 4.5 Ecosystem and Infrastructure

The dominance of AR models has created a self-reinforcing ecosystem:
- Hardware (GPUs, TPUs) is optimized for the matrix multiplications in transformer forward passes.
- Software (FlashAttention, vLLM, TensorRT-LLM) is optimized for AR inference.
- Datasets are curated for next-token prediction.
- Evaluation benchmarks assume sequential generation.
- Human preferences (RLHF) are easiest to apply to AR models.

---

## 5. Open Problems and Potential Paths Forward

### 5.1 Hybrid Models: EBMs as Components, Not Replacements

The most promising near-term path is to use EBMs as **components within AR-dominated systems**, rather than trying to replace AR models entirely.

**EBMs as rerankers (Section 2.6):** Generate candidates with an AR model, score with an EBM. This is already practical and effective.

**EBMs as reward/value models:** In RLHF, the reward model is an energy function. DPO makes this connection explicit. The entire RLHF pipeline can be viewed as: train an AR model, then tilt its distribution toward low-energy regions of a learned energy function.

**EBMs for constrained generation:** When generation must satisfy hard constraints (e.g., type-checking in code, syntactic validity in formal proofs), an EBM can define the constraint energy, and the AR model can be guided by this energy during decoding.

### 5.2 Discrete Diffusion and Iterative Refinement

Discrete diffusion models (MDLM, SEDD, D3PM) represent a middle ground between EBMs and AR models:
- They define a forward corruption process (masking, substitution) and a learned reverse process.
- Training is tractable (variational bound on likelihood).
- Generation is iterative but parallel (all positions refined simultaneously).
- The gap with AR models is narrowing: as of 2025, the best discrete diffusion models approach AR perplexity on language modeling benchmarks.

These models inherit some EBM advantages (bidirectional context, iterative refinement) while avoiding the worst EBM pitfalls (intractable partition function, MCMC sampling).

### 5.3 EBMs for Planning and Search in Theorem Proving

Theorem proving is a domain where EBMs' strengths may outweigh their weaknesses:

**Search, not sampling.** In theorem proving, we do not need to sample from $p_\theta(x)$ -- we need to find a single $x$ (proof) with low energy (high quality). This transforms the intractable sampling problem into an optimization problem, which is easier.

**Verification is cheap.** In Lean 4, the type checker provides an exact verification oracle. We can generate many candidate tactics, check them, and keep the valid ones. The EBM only needs to rank candidates well, not generate perfectly.

**Small action space.** Individual proof tactics are short (typically 1-3 lines of Lean code), much shorter than free-form text generation. This makes MCMC sampling more feasible.

**Compositional structure.** Proofs have compositional structure (lemmas, sub-goals) that maps naturally to energy composition.

### 5.4 Amortized MCMC and Learned Samplers

Instead of running MCMC at inference time, train a separate neural network to approximate the EBM's distribution:
- **Flow-based samplers:** Train a normalizing flow to match the EBM distribution. The flow provides fast sampling, and the EBM provides the training signal.
- **GFlowNets (Bengio et al., 2021-2023):** Learn a sequential sampling policy over a DAG of construction steps, where the policy is trained to sample proportional to the EBM's Boltzmann distribution. GFlowNets handle discrete spaces naturally and have shown promise for molecular generation and combinatorial optimization.

**Relevance to theorem proving:** GFlowNets are particularly interesting for proof search because proofs are naturally constructed step-by-step (DAG structure), and we want diverse samples (multiple valid proofs) rather than just the mode.

### 5.5 Continuous Representations of Discrete Sequences

If discrete tokens are the root cause of EBM difficulties, perhaps we should work in continuous space:
- **Latent-space EBMs:** Encode text into a continuous latent space (using a VAE or sentence encoder), define the EBM over this latent space, sample via Langevin dynamics in latent space, then decode back to text.
- **Embedding-space Langevin:** Run Langevin dynamics directly in the token embedding space of a pretrained LLM. Each step: compute energy, take gradient step in embedding space, project back to nearest token embedding.

These approaches are active research areas but face the fundamental problem that the continuous-to-discrete projection introduces errors.

---

## 6. Relevance to EBMs for Lean 4 Theorem Proving

### 6.1 The Project's Thesis

This project (`lean-ebm`) proposes replacing the separate policy and value networks in MCTS-based theorem provers with a single EBM:
- **Lower energy = more promising proof tactic.** The energy function scores candidate tactics.
- **Langevin dynamics generates tactic candidates.** Starting from noise, iteratively refine via gradient descent on the energy.
- **Energy as value function for MCTS.** The same energy function that generates tactics also evaluates proof states for search tree expansion.

### 6.2 Why the Literature's Failure Modes Are Less Severe Here

Several of the failure modes catalogued in Section 3 are mitigated in the theorem proving setting:

| Failure Mode | Severity in Free Text | Severity in Theorem Proving | Why |
|---|---|---|---|
| Partition function intractability | Critical | Moderate | We need to optimize, not sample; and action space is smaller |
| MCMC in discrete space | Critical | Moderate | Tactics are short; continuous embedding relaxations more viable for short sequences |
| Mode collapse | Severe | Moderate | Lean's type checker provides exact feedback; we can verify and reject |
| Training instability | Severe | Moderate to Severe | Still a concern; the lean-ebm codebase already observes this (`ALL_STEPS` gradient method doesn't work) |
| Scaling difficulties | Severe | Moderate | Theorem proving may not require billion-parameter models; miniF2F and VeryBench are relatively small benchmarks |
| No exact sampling | Critical for text gen | Low | We want the best tactic, not a diverse sample; beam search / best-of-N suffices |

### 6.3 Recommended Strategy Based on This Survey

Based on the literature review, the following strategy is recommended for applying EBMs to Lean 4 theorem proving:

1. **Start with EBM as reranker.** Train an AR model (e.g., fine-tuned DeepSeek-Math or similar) to generate candidate tactics. Train a separate EBM to score/rerank them. This is the lowest-risk approach and the most likely to yield immediate gains.

2. **Use the EBM as a value function for MCTS.** The energy function provides a natural value estimate for proof states. This is the project's stated goal and is well-supported by the literature (AlphaProof uses a similar architecture, though not explicitly framed as an EBM).

3. **Explore GFlowNet-style training.** If the goal is to generate tactics directly from the EBM (rather than just scoring), GFlowNets provide a more principled approach than Langevin dynamics for discrete sequences.

4. **Use continuous relaxations carefully.** The current lean-ebm prototype operates in continuous pixel space (MNIST). Extending to text requires working in a continuous token embedding space. The literature suggests this is feasible for short sequences (proof tactics) but requires careful handling of the embedding-to-token projection.

5. **Leverage Lean's type checker aggressively.** The ability to verify proof tactics exactly is an enormous advantage that free-text generation does not have. Design the system to generate many candidates (even low-quality ones) and filter with the type checker, rather than trying to generate perfect tactics from the EBM alone.

### 6.4 Open Questions for This Project

- **How does EBM energy correlate with proof success probability?** Need to empirically validate that the energy function learns a meaningful ranking over proof states.
- **Can Langevin dynamics in Lean tactic embedding space produce valid tactics?** The projection from continuous embeddings to discrete tokens is the critical engineering challenge.
- **System 1 vs. System 2 training:** The codebase explores both (PER_STEP vs. PER_RUN gradient methods). The literature suggests PER_STEP (System 1) is more stable, but PER_RUN (System 2) may be needed for problems requiring multi-step lookahead.
- **What is the right energy function architecture for Lean?** A transformer operating on proof state + candidate tactic is the natural choice, but the specific architecture (encoder-only vs. encoder-decoder, attention to goal state, etc.) is open.
- **Can the EBM learn from Lean's type checker feedback?** The type checker provides binary feedback (compiles/doesn't compile). Can this be used as a training signal for the energy function, analogous to RLHF?

---

## 7. References

### EBMs: Foundational

1. LeCun, Y., Chopra, S., Hadsell, R., Ranzato, M. A., & Huang, F. (2006). "A Tutorial on Energy-Based Learning." In *Predicting Structured Data*.
2. Du, Y., & Mordatch, I. (2019). "Implicit Generation and Modeling with Energy Based Models." *NeurIPS 2019*.
3. Grathwohl, W., Wang, K.-C., Jacobsen, J.-H., Duvenaud, D., Norouzi, M., & Swersky, K. (2020). "Your Classifier is Secretly an Energy Based Model and You Should Treat it Like One." *ICLR 2020*.
4. Song, Y., & Ermon, S. (2019). "Generative Modeling by Estimating Gradients of the Data Distribution." *NeurIPS 2019*.

### EBMs for Text

5. Bakhtin, A., Deng, Y., Gross, S., Ott, M., Ranzato, M. A., & Szlam, A. (2021). "Residual Energy-Based Models for Text." *JMLR 2021*.
6. Deng, Y., Bakhtin, A., Ott, M., Szlam, A., & Ranzato, M. A. (2020). "Residual Energy-Based Models for Text Generation." *ICLR 2020 Workshop*.
7. Clark, K., Luong, M.-T., Le, Q. V., & Manning, C. D. (2020). "ELECTRA: Pre-training Text Encoders as Discriminators Rather Than Generators." *ICLR 2020*.
8. Clark, K., Luong, M.-T., Le, Q. V., & Manning, C. D. (2022). "ELECTRIC: Pre-training Text Encoders as Energy-Based Models." *ICLR 2022*.
9. He, T., & Taylor, G. W. (2024). "Energy-Based Models for Text." *Survey and Analysis*.

### Non-Autoregressive and Iterative Generation

10. Ghazvininejad, M., Levy, O., Liu, Y., & Zettlemoyer, L. (2019). "Mask-Predict: Parallel Decoding of Conditional Masked Language Models." *EMNLP 2019*.
11. Gu, J., Bradbury, J., Xiong, C., Li, V. O. K., & Socher, R. (2018). "Non-Autoregressive Neural Machine Translation." *ICLR 2018*.
12. Saharia, C., Chan, W., Saxena, S., & Norouzi, M. (2020). "Non-Autoregressive Machine Translation with Latent Alignments." *EMNLP 2020*.
13. Huang, F., Tao, C., Lu, H., Peng, N., & Li, L. (2022). "Directed Acyclic Transformer for Non-Autoregressive Machine Translation." *ICML 2022*.

### Discrete Diffusion and Score-Based Models for Text

14. Lou, A., Meng, C., & Ermon, S. (2024). "Discrete Diffusion Modeling by Estimating the Ratios of the Data Distribution." *ICML 2024*.
15. Sahoo, S., Arriola, M., Schiff, Y., Gokaslan, A., Marber, E., Bovi, S., Kuleshov, V., & Rush, A. M. (2024). "Simple and Effective Masked Diffusion Language Models." *NeurIPS 2024*.
16. Shi, J., Han, K., Wang, Z., Doucet, A., & Titsias, M. K. (2024). "Simplified and Generalized Masked Diffusion for Discrete Data." *NeurIPS 2024*.
17. Austin, J., Johnson, D. D., Ho, J., Tarlow, D., & van den Berg, R. (2021). "Structured Denoising Diffusion Models in Discrete State-Spaces." *NeurIPS 2021*.

### RLHF, DPO, and Implicit EBMs

18. Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., & Finn, C. (2023). "Direct Preference Optimization: Your Language Model is Secretly a Reward Model." *NeurIPS 2023*.
19. Khalifa, M., Elsahar, H., & Dymetman, M. (2021). "A Distributional Approach to Controlled Text Generation." *ICLR 2021*.

### Reranking and Scoring

20. Lee, J., Mansimov, E., & Cho, K. (2018). "Deterministic Non-Autoregressive Neural Sequence Modeling by Iterative Refinement." *EMNLP 2018*.
21. Bhatt, S., et al. (2023). "Energy-Based Reranking for Neural Machine Translation."

### GFlowNets and Amortized Sampling

22. Bengio, E., Jain, M., Korablyov, M., Precup, D., & Bengio, Y. (2021). "Flow Network based Generative Models for Non-Iterative Diverse Candidate Generation." *NeurIPS 2021*.
23. Malkin, N., Jain, M., Bengio, E., Sun, C., & Bengio, Y. (2022). "Trajectory Balance: Improved Credit Assignment in GFlowNets." *NeurIPS 2022*.

### Scaling Laws and AR Dominance

24. Kaplan, J., McCandlish, S., Henighan, T., Brown, T. B., Chess, B., Child, R., Gray, S., Radford, A., Wu, J., & Amodei, D. (2020). "Scaling Laws for Neural Language Models." *arXiv:2001.08361*.
25. Hoffmann, J., Borgeaud, S., Mensch, A., Buchatskaya, E., Cai, T., Rutherford, E., ... & Sifre, L. (2022). "Training Compute-Optimal Large Language Models." *NeurIPS 2022*.

### Theorem Proving

26. Trinh, T. H., Wu, Y., Le, Q. V., He, H., & Luong, T. (2024). "Solving Olympiad Geometry without Human Demonstrations." *Nature 2024*.
27. Xin, H., Guo, D., Shao, Z., Ren, Z., Zhu, Q., Liu, B., Ruan, C., Li, W., & Liang, X. (2024). "DeepSeek-Prover: Advancing Theorem Proving in LLMs through Large-Scale Synthetic Data." *arXiv 2024*.
28. Anand, Y., Nussbaum, Z., Graves, A., & Polu, S. (2023). "Aristotle: Mastering Theorem Proving with MCTS and Language Models."

### MCMC and Training Methods

29. Hinton, G. E. (2002). "Training Products of Experts by Minimizing Contrastive Divergence." *Neural Computation*.
30. Tieleman, T. (2008). "Training Restricted Boltzmann Machines Using Approximations to the Likelihood Gradient." *ICML 2008*. (Persistent contrastive divergence.)
31. Gutmann, M. U., & Hyvarinen, A. (2010). "Noise-Contrastive Estimation: A New Estimation Principle for Unnormalized Statistical Models." *AISTATS 2010*.
