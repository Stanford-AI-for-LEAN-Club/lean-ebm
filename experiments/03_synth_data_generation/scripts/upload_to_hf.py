#!/usr/bin/env python3
"""Upload the generated C/Python-to-Lean4 dataset to HuggingFace."""

import json
import glob
import os

def main():
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
    hf_token = open(os.path.expanduser("~/keys/master_hf_token.txt")).read().strip()

    # Collect all records
    all_records = []
    for jsonl_path in sorted(glob.glob(os.path.join(output_dir, "*.jsonl"))):
        batch_name = os.path.basename(jsonl_path).replace(".jsonl", "")
        with open(jsonl_path) as f:
            for line_num, line in enumerate(f, 1):
                try:
                    rec = json.loads(line.strip())
                    rec["batch"] = batch_name
                    all_records.append(rec)
                except json.JSONDecodeError as e:
                    print(f"WARNING: {jsonl_path}:{line_num} bad JSON: {e}")

    print(f"Collected {len(all_records)} records from {len(glob.glob(os.path.join(output_dir, '*.jsonl')))} files")

    # Write combined JSONL
    combined_path = os.path.join(output_dir, "combined_dataset.jsonl")
    with open(combined_path, "w") as f:
        for rec in all_records:
            f.write(json.dumps(rec) + "\n")
    print(f"Written combined dataset to {combined_path}")

    # Upload to HuggingFace
    try:
        from huggingface_hub import HfApi
    except ImportError:
        print("Installing huggingface_hub...")
        os.system("pip install huggingface_hub")
        from huggingface_hub import HfApi

    api = HfApi(token=hf_token)
    repo_id = "StanfordAILean/c-py-dataset"

    # Create repo if it doesn't exist
    try:
        api.create_repo(repo_id=repo_id, repo_type="dataset", exist_ok=True)
        print(f"Repository {repo_id} ready")
    except Exception as e:
        print(f"Note: {e}")

    # Upload combined JSONL (use create_pr=True if direct push fails with 403)
    try:
        api.upload_file(
            path_or_fileobj=combined_path,
            path_in_repo="data/train.jsonl",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Upload {len(all_records)} C/Python-to-Lean4 formalizations"
        )
        print(f"Uploaded {len(all_records)} records to {repo_id}")
    except Exception as e:
        print(f"Direct push failed ({e}), trying PR...")
        api.upload_file(
            path_or_fileobj=combined_path,
            path_in_repo="data/train.jsonl",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=f"Upload {len(all_records)} C/Python-to-Lean4 formalizations",
            create_pr=True
        )
        print(f"Created PR with {len(all_records)} records to {repo_id}")

    # Upload a README
    readme = f"""---
license: mit
task_categories:
  - text-generation
language:
  - en
tags:
  - lean4
  - formal-verification
  - c
  - python
  - theorem-proving
size_categories:
  - n<1K
---

# C/Python-to-Lean4 Formalization Dataset

Synthetic dataset of C and Python functions translated into Lean 4, with:
- Lean4 translations
- Test cases (C/Python + Lean)
- Theorem statements and proofs

## Statistics
- Total records: {len(all_records)}
- C functions: {sum(1 for r in all_records if r['language'] == 'C')}
- Python functions: {sum(1 for r in all_records if r['language'] == 'Python')}

## Schema
Each record contains:
- `language`: "C" or "Python"
- `source`: original source function
- `lean_translation`: Lean4 translation
- `tests`: test harness (C or Python)
- `lean_tests`: Lean4 #eval/#check tests
- `theorems`: list of theorem statements and proofs
- `deps_fully_translated`: list of fully translated dependencies
- `axiomatized_deps`: list of axiomatized dependencies
- `skip_reason`: null or reason for skipping
- `batch`: source batch name

## Categories
- Arithmetic (abs, max, min, factorial, fibonacci, etc.)
- Number theory (gcd, lcm, primality, modular exponentiation)
- Array operations (sum, product, max/min element, reverse, sort check)
- Search algorithms (linear, binary, first/last occurrence)
- Sorting (bubble, insertion, selection, merge)
- Bit manipulation (power-of-two, popcount, parity, bit reverse)
- String operations (length, compare, palindrome, case conversion)
- Mathematical functions (sqrt, binomial, collatz, digital root)

## Generation
Generated using Codex CLI and Gemini CLI agents translating hand-written C/Python functions.
"""

    try:
        api.upload_file(
            path_or_fileobj=readme.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Add dataset README"
        )
    except Exception:
        api.upload_file(
            path_or_fileobj=readme.encode(),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="dataset",
            commit_message="Add dataset README",
            create_pr=True
        )
    print("Uploaded README")
    print(f"\nDataset available at: https://huggingface.co/datasets/{repo_id}")


if __name__ == "__main__":
    main()
