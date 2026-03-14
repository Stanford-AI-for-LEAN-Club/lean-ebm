

---- previous slides

Energy Based Models 
for Lean
By William Peng, Holger Molin, Eshaan Barkataki, Matt Chen 

The bitter lesson
“The bitter lesson is based on the historical observations that 
1) AI researchers have often tried to build knowledge into their agents, 
2) this always helps in the short term, and is personally satisfying to the researcher, but 
3) in the long run it plateaus and even inhibits further progress, and 
4) breakthrough progress eventually arrives by an opposing approach based on scaling computation by search and learning.”
Richard Sutton

The bitter lesson
“The bitter lesson is based on the historical observations that 
1) AI researchers have often tried to build knowledge into their agents, 
2) this always helps in the short term, and is personally satisfying to the researcher, but 
3) in the long run it plateaus and even inhibits further progress, and 
4) breakthrough progress eventually arrives by an opposing approach based on scaling computation by search and learning.”
Richard Sutton

The bitter lesson
“The bitter lesson is based on the historical observations that 
1) AI researchers have often tried to build knowledge into their agents, 
2) this always helps in the short term, and is personally satisfying to the researcher, but 
3) in the long run it plateaus and even inhibits further progress, and 
4) breakthrough progress eventually arrives by an opposing approach based on scaling computation by search and learning.”
Richard Sutton

The bitter lesson
“The bitter lesson is based on the historical observations that 
1) AI researchers have often tried to build knowledge into their agents, 
2) this always helps in the short term, and is personally satisfying to the researcher, but 
3) in the long run it plateaus and even inhibits further progress, and 
4) breakthrough progress eventually arrives by an opposing approach based on scaling computation by search and learning.”
Richard Sutton

The bitter lesson
“The bitter lesson is based on the historical observations that 
1) AI researchers have often tried to build knowledge into their agents, 
2) this always helps in the short term, and is personally satisfying to the researcher, but 
3) in the long run it plateaus and even inhibits further progress, and 
4) breakthrough progress eventually arrives by an opposing approach based on scaling computation by search and learning.”
Richard Sutton

Formal verification as a search problem

Search problem – continued
We can use the energy function as a “verification tool”
Lower energy → promising candidate
Higher energy → less promising proof

Current SOTA
Current theorem-proving systems (Aristotle, DeepSeek Prover) rely on two heads:
Policy: an fine-tuned LLM that generates tactics, used in sampling for MCTS
Value: another LLM that outputs the probability of success, used to prune branches
Our idea:
Unify the policy and value into a single model (an EBM).

What are EBMs?

How do we predict? Gradient Descent
Start with initial noise (every token has an equal probability of being chosen)
Get our energy using our model
Calculate the gradient of our energy (we want to lower this) w.r.t our input (initial noise)
Change our initial noise using the gradients

EBMs Versus other Generative Models
Transformers/RNNs: seq → distribution over tokens
Diffusion: seq + noised distribution→ denoised distribution
EBT: seq + potential distribution→ energy scalar
This scalar measures how good the potential output.

Benefits of Energy Based Models vs. Alternatives
Model Uncertainty
Higher energy → more uncertain about the answer
Dynamic Allocation of Computation
As humans, for a hard problem → think longer. Easier problem → think shorter. 
EBMs mimic this: more forward passes → better generalization 
Trained on Verifying Predictions
Verifying Predictions is easier to train than Generating Predictions

How to solve math as search problem with EMB
Use EBM + Langevian to sample chunks of tactics
Use energy score as the value to guide MCTS searches



Implications and Risks:
Implications
Training needs to be predicting next chunk
How to separate training data into chunks
Need a continuous representation of tactics
Risks
Local minima problem
“Cliff” problem


The bitter lesson, continued

Methods
We’ll take an existing pretrained, math-finetuned model (e.g. DeepSeek Math-7B), finetune a projection head, and implement inference logic.

Open Questions
Fine-tuning vs. training from scratch
Fine-tuning: embeddings?
Agentic system (like Aristotle)?

Next steps	
Make a CS id: CSID | Stanford Computer Science
Divide pipeline work- benchmarks, training, architecture, etc.
Why do we believe in this? 
How can we test that? 
How can we convince a skeptic that this is true?
How do we train the ebm in a stable way?
Contrastive - negative samples?
What does the structure of Lean change about model training
Data generation?
Benchmarks: miniF2F, Veribench
Lean training data
Interfacing with Lean (v4.26): stanford-centaur/PyPantograph: A Machine-to-Machine Interaction System for Lean 4.
brando90/snap-cluster-setup

Code Verification
Scalable Oversight of Code
tests/theorems → automate writing theorems
Data quality
train (post/pre/cont) train a model for all Lean
doremi, dodge
agentic data
Replacing pre-training with “all training”
EBM
