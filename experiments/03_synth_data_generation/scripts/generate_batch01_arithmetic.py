#!/usr/bin/env python3
# TLDR: Generates validated JSONL records for batch01 arithmetic C/Python functions and writes the batch output file.

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path("/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation")
C_PATH = ROOT / "c_src" / "batch01_arithmetic.c"
PY_PATH = ROOT / "py_src" / "batch01_arithmetic.py"
OUTPUT_PATH = ROOT / "output" / "batch01_arithmetic.jsonl"
TEMP_DIR = ROOT / "temp_validation" / "batch01_arithmetic"
LEAN_BIN = Path("/Users/brandomiranda/.elan/bin/lean")
GCC_BIN = Path("/usr/bin/gcc")
PYTHON_BIN = "python3"
FUNCTION_ORDER = ["abs_val", "max_of_two", "min_of_two", "clamp", "factorial", "fibonacci", "sign"]


@dataclass
class ValidationResult:
    ok: bool
    detail: str


def theorem(name: str, statement: str, proof: str = "by\n  native_decide") -> dict[str, str]:
    return {"name": name, "statement": statement, "proof": proof}


def extract_c_functions(path: Path) -> dict[str, str]:
    text = path.read_text()
    pattern = re.compile(
        r"(?ms)^[A-Za-z_][A-Za-z0-9_\s\*]*?\b([A-Za-z_][A-Za-z0-9_]*)\s*\([^;]*?\)\s*\{.*?^}\n?"
    )
    functions: dict[str, str] = {}
    for match in pattern.finditer(text):
        functions[match.group(1)] = match.group(0).rstrip()
    return functions


def extract_python_functions(path: Path) -> dict[str, str]:
    lines = path.read_text().splitlines()
    functions: dict[str, str] = {}
    current_name: str | None = None
    current_lines: list[str] = []

    for line in lines:
        if line.startswith("def "):
            if current_name is not None:
                functions[current_name] = "\n".join(current_lines).rstrip()
            current_name = line.split("def ", 1)[1].split("(", 1)[0]
            current_lines = [line]
            continue
        if current_name is not None:
            if line.startswith("    ") or line == "":
                current_lines.append(line)

    if current_name is not None:
        functions[current_name] = "\n".join(current_lines).rstrip()
    return functions


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def validate_lean(record: dict[str, Any], stem: str, expected_eval_lines: list[str]) -> ValidationResult:
    theorem_block = "\n\n".join(
        f"theorem {thm['name']} : {thm['statement']} :=\n{thm['proof']}" for thm in record["theorems"]
    )
    lean_body = "\n\n".join(
        [
            record["lean_translation"].strip(),
            record["lean_tests"].strip(),
            theorem_block.strip(),
        ]
    ).strip() + "\n"
    lean_path = TEMP_DIR / f"{stem}.lean"
    write_text(lean_path, lean_body)
    proc = subprocess.run([str(LEAN_BIN), str(lean_path)], text=True, capture_output=True, cwd=ROOT)
    if proc.returncode != 0:
        return ValidationResult(False, f"lean failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}".strip())
    actual_lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    eval_lines = actual_lines[: len(expected_eval_lines)]
    if eval_lines != expected_eval_lines:
        return ValidationResult(
            False,
            f"lean #eval mismatch for {stem}: expected {expected_eval_lines}, got {eval_lines}",
        )
    return ValidationResult(True, proc.stdout.strip())


def validate_c(record: dict[str, Any], stem: str) -> ValidationResult:
    c_path = TEMP_DIR / f"{stem}.c"
    bin_path = TEMP_DIR / stem
    write_text(c_path, record["tests"])
    compile_proc = subprocess.run(
        [str(GCC_BIN), "-std=c11", "-Wall", "-Wextra", "-O2", "-o", str(bin_path), str(c_path)],
        text=True,
        capture_output=True,
        cwd=ROOT,
    )
    if compile_proc.returncode != 0:
        return ValidationResult(
            False,
            f"gcc failed:\nSTDOUT:\n{compile_proc.stdout}\nSTDERR:\n{compile_proc.stderr}".strip(),
        )
    run_proc = subprocess.run([str(bin_path)], text=True, capture_output=True, cwd=ROOT)
    if run_proc.returncode != 0:
        return ValidationResult(
            False,
            f"c test run failed:\nSTDOUT:\n{run_proc.stdout}\nSTDERR:\n{run_proc.stderr}".strip(),
        )
    return ValidationResult(True, run_proc.stdout.strip())


def validate_python(record: dict[str, Any], stem: str) -> ValidationResult:
    py_path = TEMP_DIR / f"{stem}.py"
    write_text(py_path, record["tests"])
    proc = subprocess.run([PYTHON_BIN, str(py_path)], text=True, capture_output=True, cwd=ROOT)
    if proc.returncode != 0:
        return ValidationResult(
            False,
            f"python test run failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}".strip(),
        )
    return ValidationResult(True, proc.stdout.strip())


def c_specs() -> dict[str, dict[str, Any]]:
    return {
        "abs_val": {
            "lean_translation": """def abs_val (x : Int32) : Int32 :=
  if x < 0 then 0 - x else x""",
            "tests": """#include <stdio.h>
#include <assert.h>
#include <limits.h>

int abs_val(int x) {
    if (x < 0) return -x;
    return x;
}

int main() {
    assert(abs_val(-1) == 1);
    assert(abs_val(0) == 0);
    assert(abs_val(1) == 1);
    assert(abs_val(INT_MAX) == INT_MAX);
    assert(abs_val(INT_MIN + 1) == INT_MAX);
    printf("All tests passed!\\n");
    return 0;
}""",
            "lean_tests": """#eval abs_val (-1) -- expected: 1
#eval abs_val 0 -- expected: 0
#eval abs_val 1 -- expected: 1
#eval abs_val (Int32.ofInt 2147483647) -- expected: 2147483647
#check @abs_val""",
            "lean_expected": ["1", "0", "1", "2147483647"],
            "theorems": [
                theorem("abs_val_neg_one", "abs_val (-1) = (1 : Int32)"),
                theorem("abs_val_zero", "abs_val 0 = (0 : Int32)"),
                theorem(
                    "abs_val_int_max",
                    "abs_val (Int32.ofInt 2147483647) = Int32.ofInt 2147483647",
                ),
            ],
        },
        "max_of_two": {
            "lean_translation": """def max_of_two (a b : Int32) : Int32 :=
  if a >= b then a else b""",
            "tests": """#include <stdio.h>
#include <assert.h>
#include <limits.h>

int max_of_two(int a, int b) {
    if (a >= b) return a;
    return b;
}

int main() {
    assert(max_of_two(0, 0) == 0);
    assert(max_of_two(1, -1) == 1);
    assert(max_of_two(-1, 1) == 1);
    assert(max_of_two(INT_MAX, INT_MIN) == INT_MAX);
    assert(max_of_two(INT_MIN, INT_MIN) == INT_MIN);
    printf("All tests passed!\\n");
    return 0;
}""",
            "lean_tests": """#eval max_of_two 0 0 -- expected: 0
#eval max_of_two 1 (-1) -- expected: 1
#eval max_of_two (-1) 1 -- expected: 1
#eval max_of_two (Int32.ofInt 2147483647) (Int32.ofInt (-2147483648)) -- expected: 2147483647
#check @max_of_two""",
            "lean_expected": ["0", "1", "1", "2147483647"],
            "theorems": [
                theorem("max_of_two_equal", "max_of_two 7 7 = (7 : Int32)"),
                theorem("max_of_two_mixed_signs", "max_of_two (-1) 3 = (3 : Int32)"),
                theorem(
                    "max_of_two_boundary",
                    "max_of_two (Int32.ofInt 2147483647) (Int32.ofInt (-2147483648)) = Int32.ofInt 2147483647",
                ),
            ],
        },
        "min_of_two": {
            "lean_translation": """def min_of_two (a b : Int32) : Int32 :=
  if a <= b then a else b""",
            "tests": """#include <stdio.h>
#include <assert.h>
#include <limits.h>

int min_of_two(int a, int b) {
    if (a <= b) return a;
    return b;
}

int main() {
    assert(min_of_two(0, 0) == 0);
    assert(min_of_two(1, -1) == -1);
    assert(min_of_two(-1, 1) == -1);
    assert(min_of_two(INT_MAX, INT_MIN) == INT_MIN);
    assert(min_of_two(INT_MAX, INT_MAX) == INT_MAX);
    printf("All tests passed!\\n");
    return 0;
}""",
            "lean_tests": """#eval min_of_two 0 0 -- expected: 0
#eval min_of_two 1 (-1) -- expected: -1
#eval min_of_two (-1) 1 -- expected: -1
#eval min_of_two (Int32.ofInt 2147483647) (Int32.ofInt (-2147483648)) -- expected: -2147483648
#check @min_of_two""",
            "lean_expected": ["0", "-1", "-1", "-2147483648"],
            "theorems": [
                theorem("min_of_two_equal", "min_of_two 7 7 = (7 : Int32)"),
                theorem("min_of_two_mixed_signs", "min_of_two (-1) 3 = (-1 : Int32)"),
                theorem(
                    "min_of_two_boundary",
                    "min_of_two (Int32.ofInt 2147483647) (Int32.ofInt (-2147483648)) = Int32.ofInt (-2147483648)",
                ),
            ],
        },
        "clamp": {
            "lean_translation": """def clamp (x lo hi : Int32) : Int32 :=
  if x < lo then lo else if x > hi then hi else x""",
            "tests": """#include <stdio.h>
#include <assert.h>
#include <limits.h>

int clamp(int x, int lo, int hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

int main() {
    assert(clamp(-5, -1, 1) == -1);
    assert(clamp(0, -1, 1) == 0);
    assert(clamp(5, -1, 1) == 1);
    assert(clamp(INT_MAX, -1, 1) == 1);
    assert(clamp(INT_MIN, -1, 1) == -1);
    printf("All tests passed!\\n");
    return 0;
}""",
            "lean_tests": """#eval clamp (-5) (-1) 1 -- expected: -1
#eval clamp 0 (-1) 1 -- expected: 0
#eval clamp 5 (-1) 1 -- expected: 1
#eval clamp (Int32.ofInt 2147483647) (-1) 1 -- expected: 1
#check @clamp""",
            "lean_expected": ["-1", "0", "1", "1"],
            "theorems": [
                theorem("clamp_below_example", "clamp (-5) (-1) 1 = (-1 : Int32)"),
                theorem("clamp_inside_example", "clamp 0 (-1) 1 = (0 : Int32)"),
                theorem("clamp_above_example", "clamp 5 (-1) 1 = (1 : Int32)"),
                theorem("clamp_idempotent_example", "clamp (clamp 5 (-1) 1) (-1) 1 = clamp 5 (-1) 1"),
            ],
        },
        "factorial": {
            "lean_translation": """def factorial (n : UInt32) : UInt32 :=
  let nums := (List.range (n.toNat + 1)).drop 2
  nums.foldl (fun acc i => acc * UInt32.ofNat i) (1 : UInt32)""",
            "tests": """#include <stdio.h>
#include <assert.h>

unsigned int factorial(unsigned int n) {
    unsigned int result = 1;
    for (unsigned int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

int main() {
    assert(factorial(0u) == 1u);
    assert(factorial(1u) == 1u);
    assert(factorial(5u) == 120u);
    assert(factorial(10u) == 3628800u);
    assert(factorial(13u) == 1932053504u);
    printf("All tests passed!\\n");
    return 0;
}""",
            "lean_tests": """#eval factorial 0 -- expected: 1
#eval factorial 1 -- expected: 1
#eval factorial 5 -- expected: 120
#eval factorial 13 -- expected: 1932053504
#check @factorial""",
            "lean_expected": ["1", "1", "120", "1932053504"],
            "theorems": [
                theorem("factorial_zero", "factorial 0 = (1 : UInt32)"),
                theorem("factorial_one", "factorial 1 = (1 : UInt32)"),
                theorem("factorial_five", "factorial 5 = (120 : UInt32)"),
                theorem("factorial_overflow_13", "factorial 13 = (1932053504 : UInt32)"),
            ],
        },
        "fibonacci": {
            "lean_translation": """def fibonacci (n : UInt32) : UInt32 :=
  if n <= 1 then n
  else
    let rec loop (remaining : Nat) (a b : UInt32) : UInt32 :=
      match remaining with
      | 0 => b
      | k + 1 => loop k b (a + b)
    loop (n.toNat - 1) 0 1""",
            "tests": """#include <stdio.h>
#include <assert.h>

unsigned int fibonacci(unsigned int n) {
    if (n <= 1) return n;
    unsigned int a = 0, b = 1;
    for (unsigned int i = 2; i <= n; i++) {
        unsigned int tmp = a + b;
        a = b;
        b = tmp;
    }
    return b;
}

int main() {
    assert(fibonacci(0u) == 0u);
    assert(fibonacci(1u) == 1u);
    assert(fibonacci(2u) == 1u);
    assert(fibonacci(10u) == 55u);
    assert(fibonacci(48u) == 512559680u);
    printf("All tests passed!\\n");
    return 0;
}""",
            "lean_tests": """#eval fibonacci 0 -- expected: 0
#eval fibonacci 1 -- expected: 1
#eval fibonacci 10 -- expected: 55
#eval fibonacci 48 -- expected: 512559680
#check @fibonacci""",
            "lean_expected": ["0", "1", "55", "512559680"],
            "theorems": [
                theorem("fibonacci_zero", "fibonacci 0 = (0 : UInt32)"),
                theorem("fibonacci_one", "fibonacci 1 = (1 : UInt32)"),
                theorem("fibonacci_ten", "fibonacci 10 = (55 : UInt32)"),
                theorem("fibonacci_48", "fibonacci 48 = (512559680 : UInt32)"),
            ],
        },
        "sign": {
            "lean_translation": """def sign (x : Int32) : Int32 :=
  if x > 0 then 1 else if x < 0 then -1 else 0""",
            "tests": """#include <stdio.h>
#include <assert.h>
#include <limits.h>

int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;
}

int main() {
    assert(sign(-1) == -1);
    assert(sign(0) == 0);
    assert(sign(1) == 1);
    assert(sign(INT_MAX) == 1);
    assert(sign(INT_MIN) == -1);
    printf("All tests passed!\\n");
    return 0;
}""",
            "lean_tests": """#eval sign (-1) -- expected: -1
#eval sign 0 -- expected: 0
#eval sign 1 -- expected: 1
#eval sign (Int32.ofInt (-2147483648)) -- expected: -1
#check @sign""",
            "lean_expected": ["-1", "0", "1", "-1"],
            "theorems": [
                theorem("sign_neg_one", "sign (-1) = (-1 : Int32)"),
                theorem("sign_zero", "sign 0 = (0 : Int32)"),
                theorem("sign_pos_one", "sign 1 = (1 : Int32)"),
                theorem("sign_int_min", "sign (Int32.ofInt (-2147483648)) = (-1 : Int32)"),
            ],
        },
    }


def python_specs() -> dict[str, dict[str, Any]]:
    return {
        "abs_val": {
            "lean_translation": """def abs_val (x : Int) : Int :=
  if x < 0 then -x else x""",
            "tests": """def abs_val(x: int) -> int:
    if x < 0:
        return -x
    return x


assert abs_val(-1) == 1
assert abs_val(0) == 0
assert abs_val(1) == 1
assert abs_val(-(10**18)) == 10**18
assert abs_val(10**18) == 10**18
print("All tests passed!")""",
            "lean_tests": """#eval abs_val (-1) -- expected: 1
#eval abs_val 0 -- expected: 0
#eval abs_val 1 -- expected: 1
#eval abs_val (-1000000000000000000) -- expected: 1000000000000000000
#check @abs_val""",
            "lean_expected": ["1", "0", "1", "1000000000000000000"],
            "theorems": [
                theorem("abs_val_neg_one", "abs_val (-1) = (1 : Int)"),
                theorem("abs_val_zero", "abs_val 0 = (0 : Int)"),
                theorem("abs_val_big", "abs_val (-1000000000000000000) = (1000000000000000000 : Int)"),
            ],
        },
        "max_of_two": {
            "lean_translation": """def max_of_two (a b : Int) : Int :=
  if a >= b then a else b""",
            "tests": """def max_of_two(a: int, b: int) -> int:
    if a >= b:
        return a
    return b


assert max_of_two(0, 0) == 0
assert max_of_two(1, -1) == 1
assert max_of_two(-1, 1) == 1
assert max_of_two(-(10**18), 10**18) == 10**18
assert max_of_two(10**18, 10**18) == 10**18
print("All tests passed!")""",
            "lean_tests": """#eval max_of_two 0 0 -- expected: 0
#eval max_of_two 1 (-1) -- expected: 1
#eval max_of_two (-1) 1 -- expected: 1
#eval max_of_two (-1000000000000000000) 1000000000000000000 -- expected: 1000000000000000000
#check @max_of_two""",
            "lean_expected": ["0", "1", "1", "1000000000000000000"],
            "theorems": [
                theorem("max_of_two_equal", "max_of_two 7 7 = (7 : Int)"),
                theorem("max_of_two_mixed_signs", "max_of_two (-1) 3 = (3 : Int)"),
                theorem(
                    "max_of_two_big",
                    "max_of_two (-1000000000000000000) 1000000000000000000 = (1000000000000000000 : Int)",
                ),
            ],
        },
        "min_of_two": {
            "lean_translation": """def min_of_two (a b : Int) : Int :=
  if a <= b then a else b""",
            "tests": """def min_of_two(a: int, b: int) -> int:
    if a <= b:
        return a
    return b


assert min_of_two(0, 0) == 0
assert min_of_two(1, -1) == -1
assert min_of_two(-1, 1) == -1
assert min_of_two(-(10**18), 10**18) == -(10**18)
assert min_of_two(10**18, 10**18) == 10**18
print("All tests passed!")""",
            "lean_tests": """#eval min_of_two 0 0 -- expected: 0
#eval min_of_two 1 (-1) -- expected: -1
#eval min_of_two (-1) 1 -- expected: -1
#eval min_of_two (-1000000000000000000) 1000000000000000000 -- expected: -1000000000000000000
#check @min_of_two""",
            "lean_expected": ["0", "-1", "-1", "-1000000000000000000"],
            "theorems": [
                theorem("min_of_two_equal", "min_of_two 7 7 = (7 : Int)"),
                theorem("min_of_two_mixed_signs", "min_of_two (-1) 3 = (-1 : Int)"),
                theorem(
                    "min_of_two_big",
                    "min_of_two (-1000000000000000000) 1000000000000000000 = (-1000000000000000000 : Int)",
                ),
            ],
        },
        "clamp": {
            "lean_translation": """def clamp (x lo hi : Int) : Int :=
  if x < lo then lo else if x > hi then hi else x""",
            "tests": """def clamp(x: int, lo: int, hi: int) -> int:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


assert clamp(-5, -1, 1) == -1
assert clamp(0, -1, 1) == 0
assert clamp(5, -1, 1) == 1
assert clamp(10**18, -1, 1) == 1
assert clamp(-(10**18), -1, 1) == -1
print("All tests passed!")""",
            "lean_tests": """#eval clamp (-5) (-1) 1 -- expected: -1
#eval clamp 0 (-1) 1 -- expected: 0
#eval clamp 5 (-1) 1 -- expected: 1
#eval clamp 1000000000000000000 (-1) 1 -- expected: 1
#check @clamp""",
            "lean_expected": ["-1", "0", "1", "1"],
            "theorems": [
                theorem("clamp_below_example", "clamp (-5) (-1) 1 = (-1 : Int)"),
                theorem("clamp_inside_example", "clamp 0 (-1) 1 = (0 : Int)"),
                theorem("clamp_above_example", "clamp 5 (-1) 1 = (1 : Int)"),
                theorem("clamp_idempotent_example", "clamp (clamp 5 (-1) 1) (-1) 1 = clamp 5 (-1) 1"),
            ],
        },
        "factorial": {
            "lean_translation": """def factorial (n : Int) : Int :=
  let upper := Int.toNat (n + 1)
  let nums := (List.range upper).drop 2
  nums.foldl (fun acc i => acc * Int.ofNat i) (1 : Int)""",
            "tests": """def factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


assert factorial(-1) == 1
assert factorial(0) == 1
assert factorial(1) == 1
assert factorial(5) == 120
assert factorial(10) == 3628800
print("All tests passed!")""",
            "lean_tests": """#eval factorial (-1) -- expected: 1
#eval factorial 0 -- expected: 1
#eval factorial 5 -- expected: 120
#eval factorial 10 -- expected: 3628800
#check @factorial""",
            "lean_expected": ["1", "1", "120", "3628800"],
            "theorems": [
                theorem("factorial_neg_one", "factorial (-1) = (1 : Int)"),
                theorem("factorial_zero", "factorial 0 = (1 : Int)"),
                theorem("factorial_five", "factorial 5 = (120 : Int)"),
                theorem("factorial_ten", "factorial 10 = (3628800 : Int)"),
            ],
        },
        "fibonacci": {
            "lean_translation": """def fibonacci (n : Int) : Int :=
  if n <= 1 then n
  else
    let rec loop (remaining : Nat) (a b : Int) : Int :=
      match remaining with
      | 0 => b
      | k + 1 => loop k b (a + b)
    loop (Int.toNat (n - 1)) 0 1""",
            "tests": """def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


assert fibonacci(-1) == -1
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(10) == 55
assert fibonacci(20) == 6765
print("All tests passed!")""",
            "lean_tests": """#eval fibonacci (-1) -- expected: -1
#eval fibonacci 0 -- expected: 0
#eval fibonacci 10 -- expected: 55
#eval fibonacci 20 -- expected: 6765
#check @fibonacci""",
            "lean_expected": ["-1", "0", "55", "6765"],
            "theorems": [
                theorem("fibonacci_neg_one", "fibonacci (-1) = (-1 : Int)"),
                theorem("fibonacci_zero", "fibonacci 0 = (0 : Int)"),
                theorem("fibonacci_ten", "fibonacci 10 = (55 : Int)"),
                theorem("fibonacci_twenty", "fibonacci 20 = (6765 : Int)"),
            ],
        },
        "sign": {
            "lean_translation": """def sign (x : Int) : Int :=
  if x > 0 then 1 else if x < 0 then -1 else 0""",
            "tests": """def sign(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


assert sign(-1) == -1
assert sign(0) == 0
assert sign(1) == 1
assert sign(-(10**18)) == -1
assert sign(10**18) == 1
print("All tests passed!")""",
            "lean_tests": """#eval sign (-1) -- expected: -1
#eval sign 0 -- expected: 0
#eval sign 1 -- expected: 1
#eval sign (-1000000000000000000) -- expected: -1
#check @sign""",
            "lean_expected": ["-1", "0", "1", "-1"],
            "theorems": [
                theorem("sign_neg_one", "sign (-1) = (-1 : Int)"),
                theorem("sign_zero", "sign 0 = (0 : Int)"),
                theorem("sign_pos_one", "sign 1 = (1 : Int)"),
                theorem("sign_big_negative", "sign (-1000000000000000000) = (-1 : Int)"),
            ],
        },
    }


def build_records() -> list[dict[str, Any]]:
    c_functions = extract_c_functions(C_PATH)
    py_functions = extract_python_functions(PY_PATH)
    c_spec_map = c_specs()
    py_spec_map = python_specs()
    records: list[dict[str, Any]] = []

    for name in FUNCTION_ORDER:
        spec = c_spec_map[name]
        records.append(
            {
                "language": "C",
                "source": c_functions[name],
                "lean_translation": spec["lean_translation"],
                "tests": spec["tests"],
                "lean_tests": spec["lean_tests"],
                "theorems": spec["theorems"],
                "deps_fully_translated": [],
                "axiomatized_deps": [],
                "skip_reason": None,
                "_lean_expected": spec["lean_expected"],
            }
        )

    for name in FUNCTION_ORDER:
        spec = py_spec_map[name]
        records.append(
            {
                "language": "Python",
                "source": py_functions[name],
                "lean_translation": spec["lean_translation"],
                "tests": spec["tests"],
                "lean_tests": spec["lean_tests"],
                "theorems": spec["theorems"],
                "deps_fully_translated": [],
                "axiomatized_deps": [],
                "skip_reason": None,
                "_lean_expected": spec["lean_expected"],
            }
        )
    return records


def validate_records(records: list[dict[str, Any]]) -> None:
    for record in records:
        fn_name = record["source"].split("(")[0].split()[-1].split(":")[0]
        stem = f"{record['language'].lower()}_{fn_name}"
        if record["language"] == "C":
            c_result = validate_c(record, stem)
            if not c_result.ok:
                record["skip_reason"] = c_result.detail
                continue
        else:
            py_result = validate_python(record, stem)
            if not py_result.ok:
                record["skip_reason"] = py_result.detail
                continue

        lean_result = validate_lean(record, stem, record["_lean_expected"])
        if not lean_result.ok:
            record["skip_reason"] = lean_result.detail


def write_jsonl(records: list[dict[str, Any]]) -> None:
    output_records = []
    for record in records:
        clean_record = {k: v for k, v in record.items() if not k.startswith("_")}
        output_records.append(clean_record)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w") as f:
        for record in output_records:
            f.write(json.dumps(record) + "\n")


def main() -> None:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    records = build_records()
    validate_records(records)
    write_jsonl(records)
    failures = [r for r in records if r["skip_reason"] is not None]
    print(f"Wrote {len(records)} records to {OUTPUT_PATH}")
    if failures:
        print(f"{len(failures)} records failed validation")
        for failure in failures:
            print(f"- {failure['language']} {failure['source'].split('(')[0].split()[-1]}: {failure['skip_reason']}")
    else:
        print("All records validated successfully")


if __name__ == "__main__":
    main()
