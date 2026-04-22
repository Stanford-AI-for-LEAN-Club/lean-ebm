# IMPORTANT: Do NOT read CLAUDE.md or agents-config. Start immediately.

# Task: Write a Python script that generates JSONL for C/Python-to-Lean4 translations

Look at the existing example script at `GEN_SCRIPT_EXAMPLE` — it shows the exact pattern to follow.

Read the C source file at `C_FILE_PLACEHOLDER` and the Python source file at `PY_FILE_PLACEHOLDER`.

Write a Python script at `SCRIPT_OUTPUT` that:
1. Contains ALL functions' translations inline (like the example)
2. When run, outputs a JSONL file at `JSONL_OUTPUT`

For each function in the C and Python files:
- Translate to Lean4 (use UInt32 for C unsigned int, Nat/Int for Python int)
- Write C/Python test harness strings with assert statements
- Write Lean #eval tests
- Write 1-2 theorems (use native_decide, rfl, simp, omega, or sorry for proofs)
- Include all required JSON keys: language, source, lean_translation, tests, lean_tests, theorems, deps_fully_translated, axiomatized_deps, skip_reason

After writing the script, run it with `python3 SCRIPT_OUTPUT` to generate the JSONL.

Validate at least 2 Lean translations by writing them to temp files and running `lean` on them.
lean is at: `/Users/brandomiranda/.elan/bin/lean`
