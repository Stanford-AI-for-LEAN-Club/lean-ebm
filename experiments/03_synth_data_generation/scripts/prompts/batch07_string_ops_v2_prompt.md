# IMPORTANT: Do NOT read CLAUDE.md or agents-config. Start immediately.

# Task: Write a Python script that generates JSONL for C/Python-to-Lean4 translations

Look at the existing example script at `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/scripts/gen_script_prompt_v2.md` — it shows the exact pattern to follow for structuring the Python script.

Read the C source file at `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/c_src/batch07_string_ops.c` and the Python source file at `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/py_src/batch07_string_ops.py`.

Write a Python script at `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/scripts/gen_batch07_string_ops.py` that:
1. Contains ALL functions' translations inline (like the example)
2. When run, outputs a JSONL file at `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch07_string_ops.jsonl`

For each function in the C and Python files:
- Translate to Lean4 (use UInt32 for C unsigned int, Nat/Int for Python int)
- Write C/Python test harness strings with assert statements
- Write Lean #eval tests
- Write substantive, universally quantified theorems (see CRITICAL section below)
- Include all required JSON keys: language, source, lean_translation, tests, lean_tests, theorems, deps_fully_translated, axiomatized_deps, skip_reason

## Type Mapping (C -> Lean4)
- unsigned int -> UInt32 (wrapping)
- int -> Int32 or Int (for pure math, prefer Int for provability)
- int* + length -> Array Int
- char* -> Array UInt8 or String
- bool/int-as-bool -> Bool
- void mutation -> pure function returning new value

## Type Mapping (Python -> Lean4)
- int -> Nat or Int (as appropriate)
- list[int] -> List Nat or List Int
- str -> String
- bool -> Bool

NOTE: For theorem provability, prefer using Nat/Int over UInt32 when the function is pure math. UInt32 wrapping semantics make proofs extremely hard. Use Nat for unsigned, Int for signed.

## CRITICAL: Theorem Requirements

Theorems must be **substantive** and **universally quantified**. They should collectively form a correctness specification — a reviewer should be able to reconstruct the function's behavior from the theorems alone.

### REJECT these (BAD):
```lean
-- BAD: point evaluation disguised as a theorem
theorem abs_val_neg_one : abs_val (-1) = 1 := by native_decide
-- BAD: trivially true for ANY implementation
theorem factorial_type_check : ∀ n : Nat, factorial n >= 0 := by omega
```

### REQUIRE these (GOOD):
```lean
-- GOOD: universally quantified property that characterizes behavior
theorem abs_val_nonneg (x : Int) : 0 ≤ abs_val x := by
  simp [abs_val]; split_ifs <;> omega

-- GOOD: algebraic law
theorem gcd_comm (a b : Nat) : gcd a b = gcd b a := by sorry

-- GOOD: agreement with stdlib
theorem max_of_two_eq_max (a b : Nat) : max_of_two a b = max a b := by
  simp [max_of_two]; split_ifs <;> omega

-- GOOD: output invariant
theorem reverse_length (arr : List α) : (reverse_array arr).length = arr.length := by sorry

-- GOOD: involution
theorem reverse_involution (arr : List α) : reverse_array (reverse_array arr) = arr := by sorry

-- GOOD: idempotence
theorem sort_idempotent (arr : List Nat) : bubble_sort (bubble_sort arr) = bubble_sort arr := by sorry
```

### Each function MUST have 2-4 theorems covering:
1. **Algebraic laws** (commutativity, associativity, idempotence, involution)
2. **Agreement with Lean stdlib** (e.g., `my_gcd a b = Nat.gcd a b`)
3. **Output invariants** (range, length preservation, sortedness, non-negativity)
4. **Case characterization** (e.g., `binary_search returns i → arr[i] = target`)

### Proof strategy:
- Try `simp`, `omega`, `decide`, `induction` first
- If a proof is genuinely hard, keep the CORRECT universally quantified statement and use `sorry`
- NEVER downgrade a correct statement to a trivial point-check to avoid `sorry`
- Add `"proof_incomplete": true` to the theorem dict when using `sorry`

## After writing the script, run it with `python3 /Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/scripts/gen_batch07_string_ops.py` to generate the JSONL.

Validate at least 2 Lean translations by writing them to temp files and running `lean` on them.
lean is at: `/Users/brandomiranda/.elan/bin/lean`
gcc is at: `/usr/bin/gcc`
python3 is available.

## Output Schema
Each JSON record must have:
```json
{
  "language": "C" or "Python",
  "source": "original function code",
  "lean_translation": "Lean4 translation",
  "tests": "complete test file (C or Python)",
  "lean_tests": "Lean4 #eval/#check tests",
  "theorems": [{"name": "thm_name", "statement": "theorem ...", "proof": "by ...", "proof_incomplete": false}],
  "deps_fully_translated": [],
  "axiomatized_deps": [],
  "skip_reason": null
}
```
