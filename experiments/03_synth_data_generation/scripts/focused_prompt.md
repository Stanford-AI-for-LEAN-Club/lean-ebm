# IMPORTANT: Do NOT read CLAUDE.md, agents-config, or any project config files. All instructions are here. Start working IMMEDIATELY.

# Task: Translate C/Python functions to Lean4 and output JSONL

You have C and Python source files. For EACH function, generate a JSON record and write them all to a JSONL file.

## Source Files to Process
- C: `C_FILE_PLACEHOLDER`
- Python: `PY_FILE_PLACEHOLDER`

## Output: `OUTPUT_PLACEHOLDER`

Read both files. For EACH function, write one JSON line with these keys:
```json
{
  "language": "C" or "Python",
  "source": "original function code",
  "lean_translation": "Lean4 translation",
  "tests": "complete test file (C or Python)",
  "lean_tests": "Lean4 #eval/#check tests",
  "theorems": [{"name": "...", "statement": "...", "proof": "..."}],
  "deps_fully_translated": [],
  "axiomatized_deps": [],
  "skip_reason": null
}
```

## Type Mapping (C -> Lean4)
- unsigned int -> UInt32 (wrapping)
- int -> Int32 or Int (for pure math use Int)
- int* + length -> Array Int
- char* -> Array UInt8 or String
- bool/int-as-bool -> Bool
- void mutation -> pure function returning new value

## Type Mapping (Python -> Lean4)
- int -> Nat or Int (as appropriate)
- list[int] -> Array Int or List Int
- str -> String
- bool -> Bool

## Translation Rules
- Use `partial def` if termination is hard to prove, `def` otherwise
- Model C arrays as `Array` with bounds
- Model mutation as pure functions returning new values
- Stay close to original algorithm

## For Each Function:
1. Write Lean translation
2. Write C/Python test harness with asserts (test 0, 1, boundary values)
3. Write Lean #eval tests
4. Write 1-2 theorems with proofs (use sorry if proof is hard)
5. Validate: run `lean temp.lean`, `gcc -o t t.c && ./t`, `python3 t.py`
6. If validation fails, fix up to 3 times, then set skip_reason

Lean binary: `/Users/brandomiranda/.elan/bin/lean`
gcc: `/usr/bin/gcc`
python3 is available.

## CRITICAL
- Process EVERY function in BOTH files
- Write ALL output to the JSONL file above (one JSON per line)
- Do NOT read CLAUDE.md or any config files
- Start immediately with reading the source files
