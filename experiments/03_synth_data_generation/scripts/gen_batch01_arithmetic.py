#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

# Paths
ROOT = Path("/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation")
OUTPUT_PATH = ROOT / "output" / "batch01_arithmetic.jsonl"
LEAN_BIN = "/Users/brandomiranda/.elan/bin/lean"

def get_records():
    records = []
    
    # 1. abs_val (C)
    records.append({
        "language": "C",
        "source": "int abs_val(int x) {\n    if (x < 0) return -x;\n    return x;\n}",
        "lean_translation": "def abs_val (x : Int) : Int :=\n  if x < 0 then -x else x",
        "tests": "#include <stdio.h>\n#include <assert.h>\n\nint abs_val(int x) {\n    if (x < 0) return -x;\n    return x;\n}\n\nint main() {\n    assert(abs_val(-5) == 5);\n    assert(abs_val(0) == 0);\n    assert(abs_val(5) == 5);\n    printf(\"All tests passed!\\n\");\n    return 0;\n}",
        "lean_tests": "#eval abs_val (-5)\n#eval abs_val 0\n#eval abs_val 5",
        "theorems": [
            {"name": "abs_val_nonneg", "statement": "∀ (x : Int), 0 ≤ abs_val x", "proof": "by\n  unfold abs_val\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "abs_val_pos", "statement": "∀ (x : Int), x ≥ 0 → abs_val x = x", "proof": "by\n  intro h\n  unfold abs_val\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "abs_val_neg", "statement": "∀ (x : Int), x < 0 → abs_val x = -x", "proof": "by\n  intro h\n  unfold abs_val\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 2. max_of_two (C)
    records.append({
        "language": "C",
        "source": "int max_of_two(int a, int b) {\n    if (a >= b) return a;\n    return b;\n}",
        "lean_translation": "def max_of_two (a b : Int) : Int :=\n  if a ≥ b then a else b",
        "tests": "#include <stdio.h>\n#include <assert.h>\n\nint max_of_two(int a, int b) {\n    if (a >= b) return a;\n    return b;\n}\n\nint main() {\n    assert(max_of_two(1, 2) == 2);\n    assert(max_of_two(2, 1) == 2);\n    assert(max_of_two(1, 1) == 1);\n    printf(\"All tests passed!\\n\");\n    return 0;\n}",
        "lean_tests": "#eval max_of_two 1 2\n#eval max_of_two 2 1\n#eval max_of_two 1 1",
        "theorems": [
            {"name": "max_of_two_ge_left", "statement": "∀ (a b : Int), max_of_two a b ≥ a", "proof": "by\n  unfold max_of_two\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "max_of_two_ge_right", "statement": "∀ (a b : Int), max_of_two a b ≥ b", "proof": "by\n  unfold max_of_two\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "max_of_two_comm", "statement": "∀ (a b : Int), max_of_two a b = max_of_two b a", "proof": "by\n  unfold max_of_two\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 3. min_of_two (C)
    records.append({
        "language": "C",
        "source": "int min_of_two(int a, int b) {\n    if (a <= b) return a;\n    return b;\n}",
        "lean_translation": "def min_of_two (a b : Int) : Int :=\n  if a ≤ b then a else b",
        "tests": "#include <stdio.h>\n#include <assert.h>\n\nint min_of_two(int a, int b) {\n    if (a <= b) return a;\n    return b;\n}\n\nint main() {\n    assert(min_of_two(1, 2) == 1);\n    assert(min_of_two(2, 1) == 1);\n    assert(min_of_two(1, 1) == 1);\n    printf(\"All tests passed!\\n\");\n    return 0;\n}",
        "lean_tests": "#eval min_of_two 1 2\n#eval min_of_two 2 1\n#eval min_of_two 1 1",
        "theorems": [
            {"name": "min_of_two_le_left", "statement": "∀ (a b : Int), min_of_two a b ≤ a", "proof": "by\n  unfold min_of_two\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "min_of_two_le_right", "statement": "∀ (a b : Int), min_of_two a b ≤ b", "proof": "by\n  unfold min_of_two\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "min_of_two_comm", "statement": "∀ (a b : Int), min_of_two a b = min_of_two b a", "proof": "by\n  unfold min_of_two\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 4. clamp (C)
    records.append({
        "language": "C",
        "source": "int clamp(int x, int lo, int hi) {\n    if (x < lo) return lo;\n    if (x > hi) return hi;\n    return x;\n}",
        "lean_translation": "def clamp (x lo hi : Int) : Int :=\n  if x < lo then lo else if x > hi then hi else x",
        "tests": "#include <stdio.h>\n#include <assert.h>\n\nint clamp(int x, int lo, int hi) {\n    if (x < lo) return lo;\n    if (x > hi) return hi;\n    return x;\n}\n\nint main() {\n    assert(clamp(5, 1, 10) == 5);\n    assert(clamp(0, 1, 10) == 1);\n    assert(clamp(15, 1, 10) == 10);\n    printf(\"All tests passed!\\n\");\n    return 0;\n}",
        "lean_tests": "#eval clamp 5 1 10\n#eval clamp 0 1 10\n#eval clamp 15 1 10",
        "theorems": [
            {"name": "clamp_bounds", "statement": "∀ (x lo hi : Int), lo ≤ hi → lo ≤ clamp x lo hi ∧ clamp x lo hi ≤ hi", "proof": "by\n  intro h\n  unfold clamp\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "clamp_idempotent", "statement": "∀ (x lo hi : Int), clamp (clamp x lo hi) lo hi = clamp x lo hi", "proof": "by\n  unfold clamp\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 5. factorial (C)
    records.append({
        "language": "C",
        "source": "unsigned int factorial(unsigned int n) {\n    unsigned int result = 1;\n    for (unsigned int i = 2; i <= n; i++) {\n        result *= i;\n    }\n    return result;\n}",
        "lean_translation": "def factorial (n : Nat) : Nat :=\n  match n with\n  | 0 => 1\n  | n + 1 => (n + 1) * factorial n",
        "tests": "#include <stdio.h>\n#include <assert.h>\n\nunsigned int factorial(unsigned int n) {\n    unsigned int result = 1;\n    for (unsigned int i = 2; i <= n; i++) {\n        result *= i;\n    }\n    return result;\n}\n\nint main() {\n    assert(factorial(0) == 1);\n    assert(factorial(1) == 1);\n    assert(factorial(5) == 120);\n    printf(\"All tests passed!\\n\");\n    return 0;\n}",
        "lean_tests": "#eval factorial 0\n#eval factorial 1\n#eval factorial 5",
        "theorems": [
            {"name": "factorial_zero", "statement": "factorial 0 = 1", "proof": "by rfl", "proof_incomplete": False},
            {"name": "factorial_pos", "statement": "∀ (n : Nat), factorial n > 0", "proof": "by\n  intro n\n  induction n with\n  | zero => simp [factorial]\n  | succ n ih => simp [factorial]; sorry", "proof_incomplete": True},
            {"name": "factorial_step", "statement": "∀ (n : Nat), factorial (n + 1) = (n + 1) * factorial n", "proof": "by intro n; rfl", "proof_incomplete": False}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 6. fibonacci (C)
    records.append({
        "language": "C",
        "source": "unsigned int fibonacci(unsigned int n) {\n    if (n <= 1) return n;\n    unsigned int a = 0, b = 1;\n    for (unsigned int i = 2; i <= n; i++) {\n        unsigned int tmp = a + b;\n        a = b;\n        b = tmp;\n    }\n    return b;\n}",
        "lean_translation": "def fibonacci (n : Nat) : Nat :=\n  match n with\n  | 0 => 0\n  | 1 => 1\n  | n + 2 => fibonacci (n + 1) + fibonacci n",
        "tests": "#include <stdio.h>\n#include <assert.h>\n\nunsigned int fibonacci(unsigned int n) {\n    if (n <= 1) return n;\n    unsigned int a = 0, b = 1;\n    for (unsigned int i = 2; i <= n; i++) {\n        unsigned int tmp = a + b;\n        a = b;\n        b = tmp;\n    }\n    return b;\n}\n\nint main() {\n    assert(fibonacci(0) == 0);\n    assert(fibonacci(1) == 1);\n    assert(fibonacci(2) == 1);\n    assert(fibonacci(10) == 55);\n    printf(\"All tests passed!\\n\");\n    return 0;\n}",
        "lean_tests": "#eval fibonacci 0\n#eval fibonacci 1\n#eval fibonacci 10",
        "theorems": [
            {"name": "fibonacci_zero", "statement": "fibonacci 0 = 0", "proof": "by rfl", "proof_incomplete": False},
            {"name": "fibonacci_one", "statement": "fibonacci 1 = 1", "proof": "by rfl", "proof_incomplete": False},
            {"name": "fibonacci_recurrence", "statement": "∀ (n : Nat), fibonacci (n + 2) = fibonacci (n + 1) + fibonacci n", "proof": "by intro n; rfl", "proof_incomplete": False}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 7. sign (C)
    records.append({
        "language": "C",
        "source": "int sign(int x) {\n    if (x > 0) return 1;\n    if (x < 0) return -1;\n    return 0;\n}",
        "lean_translation": "def sign (x : Int) : Int :=\n  if x > 0 then 1 else if x < 0 then -1 else 0",
        "tests": "#include <stdio.h>\n#include <assert.h>\n\nint sign(int x) {\n    if (x > 0) return 1;\n    if (x < 0) return -1;\n    return 0;\n}\n\nint main() {\n    assert(sign(5) == 1);\n    assert(sign(-5) == -1);\n    assert(sign(0) == 0);\n    printf(\"All tests passed!\\n\");\n    return 0;\n}",
        "lean_tests": "#eval sign 5\n#eval sign (-5)\n#eval sign 0",
        "theorems": [
            {"name": "sign_pos", "statement": "∀ (x : Int), x > 0 → sign x = 1", "proof": "by\n  intro h\n  unfold sign\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "sign_neg", "statement": "∀ (x : Int), x < 0 → sign x = -1", "proof": "by\n  intro h\n  unfold sign\n  split_ifs <;> sorry", "proof_incomplete": True},
            {"name": "sign_zero", "statement": "sign 0 = 0", "proof": "by rfl", "proof_incomplete": False}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # Python Functions
    
    # 8. abs_val (Python)
    records.append({
        "language": "Python",
        "source": "def abs_val(x: int) -> int:\n    if x < 0:\n        return -x\n    return x",
        "lean_translation": "def abs_val_py (x : Int) : Int :=\n  if x < 0 then -x else x",
        "tests": "def abs_val(x: int) -> int:\n    if x < 0:\n        return -x\n    return x\n\nassert abs_val(-5) == 5\nassert abs_val(0) == 0\nassert abs_val(5) == 5\nprint(\"All tests passed!\")",
        "lean_tests": "#eval abs_val_py (-5)\n#eval abs_val_py 0\n#eval abs_val_py 5",
        "theorems": [
            {"name": "abs_val_py_nonneg", "statement": "∀ (x : Int), 0 ≤ abs_val_py x", "proof": "by\n  unfold abs_val_py\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 9. max_of_two (Python)
    records.append({
        "language": "Python",
        "source": "def max_of_two(a: int, b: int) -> int:\n    if a >= b:\n        return a\n    return b",
        "lean_translation": "def max_of_two_py (a b : Int) : Int :=\n  if a ≥ b then a else b",
        "tests": "def max_of_two(a, b):\n    if a >= b: return a\n    return b\n\nassert max_of_two(1, 2) == 2\nassert max_of_two(2, 1) == 2\nprint(\"All tests passed!\")",
        "lean_tests": "#eval max_of_two_py 1 2\n#eval max_of_two_py 2 1",
        "theorems": [
            {"name": "max_of_two_py_ge", "statement": "∀ (a b : Int), max_of_two_py a b ≥ a ∧ max_of_two_py a b ≥ b", "proof": "by\n  unfold max_of_two_py\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 10. min_of_two (Python)
    records.append({
        "language": "Python",
        "source": "def min_of_two(a: int, b: int) -> int:\n    if a <= b:\n        return a\n    return b",
        "lean_translation": "def min_of_two_py (a b : Int) : Int :=\n  if a ≤ b then a else b",
        "tests": "def min_of_two(a, b):\n    if a <= b: return a\n    return b\n\nassert min_of_two(1, 2) == 1\nassert min_of_two(2, 1) == 1\nprint(\"All tests passed!\")",
        "lean_tests": "#eval min_of_two_py 1 2\n#eval min_of_two_py 2 1",
        "theorems": [
            {"name": "min_of_two_py_le", "statement": "∀ (a b : Int), min_of_two_py a b ≤ a ∧ min_of_two_py a b ≤ b", "proof": "by\n  unfold min_of_two_py\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 11. clamp (Python)
    records.append({
        "language": "Python",
        "source": "def clamp(x: int, lo: int, hi: int) -> int:\n    if x < lo:\n        return lo\n    if x > hi:\n        return hi\n    return x",
        "lean_translation": "def clamp_py (x lo hi : Int) : Int :=\n  if x < lo then lo else if x > hi then hi else x",
        "tests": "def clamp(x, lo, hi):\n    if x < lo: return lo\n    if x > hi: return hi\n    return x\n\nassert clamp(5, 1, 10) == 5\nassert clamp(0, 1, 10) == 1\nassert clamp(15, 1, 10) == 10\nprint(\"All tests passed!\")",
        "lean_tests": "#eval clamp_py 5 1 10\n#eval clamp_py 0 1 10\n#eval clamp_py 15 1 10",
        "theorems": [
            {"name": "clamp_py_bounds", "statement": "∀ (x lo hi : Int), lo ≤ hi → lo ≤ clamp_py x lo hi ∧ clamp_py x lo hi ≤ hi", "proof": "by\n  intro h\n  unfold clamp_py\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 12. factorial (Python)
    records.append({
        "language": "Python",
        "source": "def factorial(n: int) -> int:\n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    return result",
        "lean_translation": "def factorial_py (n : Int) : Int :=\n  if n < 2 then 1\n  else Nat.factorial n.toNat",
        "tests": "def factorial(n):\n    res = 1\n    for i in range(2, n + 1): res *= i\n    return res\n\nassert factorial(0) == 1\nassert factorial(5) == 120\nassert factorial(-1) == 1\nprint(\"All tests passed!\")",
        "lean_tests": "#eval factorial_py 0\n#eval factorial_py 5\n#eval factorial_py (-1)",
        "theorems": [
            {"name": "factorial_py_pos", "statement": "∀ (n : Int), factorial_py n > 0", "proof": "by\n  unfold factorial_py\n  split_ifs\n  · sorry\n  · sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 13. fibonacci (Python)
    records.append({
        "language": "Python",
        "source": "def fibonacci(n: int) -> int:\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
        "lean_translation": "def fibonacci_py (n : Int) : Int :=\n  if n ≤ 1 then n\n  else \n    let rec loop (remaining : Nat) (a b : Int) : Int :=\n      match remaining with\n      | 0 => b\n      | k + 1 => loop k b (a + b)\n    loop (n.toNat - 1) 0 1",
        "tests": "def fibonacci(n):\n    if n <= 1: return n\n    a, b = 0, 1\n    for _ in range(2, n + 1): a, b = b, a + b\n    return b\n\nassert fibonacci(0) == 0\nassert fibonacci(1) == 1\nassert fibonacci(10) == 55\nprint(\"All tests passed!\")",
        "lean_tests": "#eval fibonacci_py 0\n#eval fibonacci_py 1\n#eval fibonacci_py 10",
        "theorems": [
            {"name": "fibonacci_py_zero", "statement": "fibonacci_py 0 = 0", "proof": "by rfl", "proof_incomplete": False},
            {"name": "fibonacci_py_one", "statement": "fibonacci_py 1 = 1", "proof": "by rfl", "proof_incomplete": False}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    # 14. sign (Python)
    records.append({
        "language": "Python",
        "source": "def sign(x: int) -> int:\n    if x > 0:\n        return 1\n    if x < 0:\n        return -1\n    return 0",
        "lean_translation": "def sign_py (x : Int) : Int :=\n  if x > 0 then 1 else if x < 0 then -1 else 0",
        "tests": "def sign(x):\n    if x > 0: return 1\n    if x < 0: return -1\n    return 0\n\nassert sign(5) == 1\nassert sign(-5) == -1\nassert sign(0) == 0\nprint(\"All tests passed!\")",
        "lean_tests": "#eval sign_py 5\n#eval sign_py (-5)\n#eval sign_py 0",
        "theorems": [
            {"name": "sign_py_cases", "statement": "∀ (x : Int), sign_py x = 1 ∨ sign_py x = -1 ∨ sign_py x = 0", "proof": "by\n  unfold sign_py\n  split_ifs <;> sorry", "proof_incomplete": True}
        ],
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None
    })

    return records

def main():
    records = get_records()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    print(f"Generated {len(records)} records in {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
