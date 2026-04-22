Create and checkout a new git branch called `leban-tasks`. Then complete all of the following tasks in order:

1. Create `literature_review_rl.md` — a literature review on synthetic data generation for post-training LLMs using reinforcement learning. Focus on papers from 2024-2026. Include a summary table with columns: paper name, method, dataset, key findings.

2. Create `literature_review_contrastive.md` — a literature review on synthetic data generation for post-training using contrastive learning approaches. Compare to RL-based methods where relevant.

3. Create `ebm_text_failures.md` — a survey of energy-based models (EBMs) applied to text/language tasks. Focus on why they fail or underperform vs autoregressive LLMs. Cover key papers, failure modes, and open problems.

4. Create `gen_lean_prompt.py` — a Python CLI script that takes a C or Python source file path as an argument, reads it, and outputs a structured prompt to stdout instructing an LLM to translate the code into semantics-preserving, compilable Lean 4. The prompt should instruct the model to preserve control flow, handle types explicitly, and produce code that works with Mathlib4.

5. Create `verybench_c_plan.md` — a plan for extending VeryBench to support C programs. Identify which modules need changes, what new parsers or translators are needed, and draft key adapter functions as pseudocode.

Commit each task separately with a descriptive commit message. Do not merge into main.