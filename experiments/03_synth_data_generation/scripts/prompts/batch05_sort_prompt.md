# Task: Generate C/Python-to-Lean4 Formalization Dataset

You are generating a synthetic dataset of C and Python functions translated into Lean 4, with test cases, theorem statements, and proofs. Work in the directory: `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation`

## Your Batch

Process BOTH the C file and Python file for this batch:
- C source: `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/c_src/batch05_sort.c`
- Python source: `/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/py_src/batch05_sort.py`

Read both files. For EACH function in each file, generate a JSON record following the schema below.

## Output Schema

For each function, output a JSON record with these exact keys:
- "language": "Python" or "C" (string)
- "source": original source function (string)
- "lean_translation": Lean4 translation (string)
- "tests": C or Python test harness as a complete compilable .c/.py file (string)
- "lean_tests": Lean4 #eval / #check test cases (string)
- "theorems": list of { "name": string, "statement": string, "proof": string }
- "deps_fully_translated": list of callee names that were axiomatized (empty list if none)
- "axiomatized_deps": list of { "name": string, "lean_axiom": string } (empty list if none)
- "skip_reason": null | string (if skipped, why)

Write the output as a JSONL file (one JSON object per line) to:
`/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch05_sort.jsonl`

## Type Conversion Rules

### Integers
- int, long, short -> use UInt32/UInt64/UInt16 (wrapping semantics) for bit-exact behavior
- unsigned variants -> same UInt types (already unsigned in Lean)
- size_t -> USize
- char used as integer -> UInt8
- Bitwise ops (&, |, ^, ~, <<, >>) -> use Lean's corresponding UInt ops, NOT Nat/Int
- For Python integers that can be arbitrarily large, use Nat or Int as appropriate

### Booleans
- bool / _Bool -> Bool
- C int used as boolean (0/1) -> Bool with explicit conversion

### Arrays and Lists
- C array with pointer+length -> Array T with side condition h : arr.size = n
- Python list -> Array T or List T
- Out-of-bounds access -> add precondition h : i < n to every theorem

### Strings
- C char* -> Array UInt8 (for byte buffers) or String
- Python str -> String

### Structs
- C struct -> Lean structure with identical field names
- In-place mutation -> pure function returning new value

## Lean Translation Guidelines

1. All functions must be total (proven to terminate) or marked `partial`
2. Use `def` for non-recursive functions, `def` with termination proof for recursive ones
3. Model C arrays as `Array` with explicit bounds
4. Model C mutation as pure functions returning new values
5. Use `do` notation for sequential operations where needed
6. Keep the translation as close to the original algorithm as possible

## Test Case Requirements

Generate test cases covering:
- 0, 1, -1 for every integer argument
- Boundary values (UInt32.max = 4294967295, etc.)
- Empty array (size = 0), single-element array, two-element array
- Arrays where all elements are equal
- For string functions: empty string, single char, palindromes

### C Test Harness Format
```c
#include <stdio.h>
#include <assert.h>

// paste the function here

int main() {
    assert(function_name(args) == expected);
    // ... more test cases
    printf("All tests passed!\n");
    return 0;
}
```

### Python Test Harness Format
```python
# paste the function here

assert function_name(args) == expected
# ... more test cases
print("All tests passed!")
```

### Lean Test Format
```lean
-- paste the translation here

#eval function_name args  -- expected: result
#check @function_name     -- type check
```

## Theorem Requirements

For each function, generate theorems about these properties (as applicable):
1. **Correctness/specification**: What the function computes (e.g., factorial n = n!)
2. **Edge cases**: Behavior at boundaries (e.g., factorial 0 = 1)
3. **Relationship lemmas**: Connections between functions (e.g., gcd a b = gcd b a)
4. **Monotonicity/ordering**: If applicable
5. **Idempotence**: If applicable (e.g., sort (sort arr) = sort arr)
6. **Involution**: If applicable (e.g., reverse (reverse arr) = arr)

Write proofs using Lean 4 tactics (simp, omega, decide, induction, etc.). If a proof is too hard, use `sorry` and note it.

## Validation Steps (DO THESE!)

For each function:
1. Write the Lean translation to a temp .lean file and run `lean` on it to check compilation
2. Write the C/Python test harness and run it with `gcc -o test test.c && ./test` or `python3 test.py`
3. Write the Lean tests and check they evaluate correctly
4. Write the theorems+proofs and check they compile

If something fails, fix it (up to 3 retries). If still broken, set skip_reason.

The lean binary is at: `/Users/brandomiranda/.elan/bin/lean`
gcc is at: `/usr/bin/gcc`
python3 is available.

## IMPORTANT

- Process EVERY function in both files (C and Python versions)
- Each C function produces one JSON record with language="C"
- Each Python function produces one JSON record with language="Python"
- Validate as many as you can - prioritize quantity AND quality
- Write all output to the JSONL file specified above
- End every response with **TLDR:**
