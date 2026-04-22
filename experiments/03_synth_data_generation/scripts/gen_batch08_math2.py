import json
from pathlib import Path


def get_c_source(name):
    sources = {
        "integer_sqrt": """unsigned int integer_sqrt(unsigned int n) {
    if (n == 0) return 0;
    unsigned int x = n;
    unsigned int y = (x + 1) / 2;
    while (y < x) {
        x = y;
        y = (x + n / x) / 2;
    }
    return x;
}""",
        "is_perfect_square": """int is_perfect_square(unsigned int n) {
    unsigned int s = integer_sqrt(n);
    return s * s == n;
}""",
        "binomial": """unsigned int binomial(unsigned int n, unsigned int k) {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n - k) k = n - k;
    unsigned int result = 1;
    for (unsigned int i = 0; i < k; i++) {
        result = result * (n - i) / (i + 1);
    }
    return result;
}""",
        "is_even": """int is_even(int n) {
    return n % 2 == 0;
}""",
        "is_odd": """int is_odd(int n) {
    return n % 2 != 0;
}""",
        "triangular_number": """unsigned int triangular_number(unsigned int n) {
    return n * (n + 1) / 2;
}""",
        "collatz_steps": """int collatz_steps(unsigned int n) {
    int steps = 0;
    while (n != 1 && n != 0) {
        if (n % 2 == 0) {
            n = n / 2;
        } else {
            n = 3 * n + 1;
        }
        steps++;
    }
    return steps;
}""",
        "digital_root": """unsigned int digital_root(unsigned int n) {
    if (n == 0) return 0;
    return 1 + (n - 1) % 9;
}""",
    }
    return sources[name]


def get_py_source(name):
    sources = {
        "integer_sqrt": """def integer_sqrt(n: int) -> int:
    if n == 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x""",
        "is_perfect_square": """def is_perfect_square(n: int) -> bool:
    s = integer_sqrt(n)
    return s * s == n""",
        "binomial": """def binomial(n: int, k: int) -> int:
    if k > n:
        return 0
    if k == 0 or k == n:
        return 1
    if k > n - k:
        k = n - k
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result""",
        "is_even": """def is_even(n: int) -> bool:
    return n % 2 == 0""",
        "is_odd": """def is_odd(n: int) -> bool:
    return n % 2 != 0""",
        "triangular_number": """def triangular_number(n: int) -> int:
    return n * (n + 1) // 2""",
        "collatz_steps": """def collatz_steps(n: int) -> int:
    steps = 0
    while n != 1 and n != 0:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps""",
        "digital_root": """def digital_root(n: int) -> int:
    if n == 0:
        return 0
    return 1 + (n - 1) % 9""",
    }
    return sources[name]


def get_lean_translation(name, lang):
    del lang
    translations = {
        "integer_sqrt": """partial def integer_sqrt (n : Nat) : Nat :=
  if n = 0 then
    0
  else
    let rec loop (x : Nat) : Nat :=
      if (x + 1) * (x + 1) ≤ n then
        loop (x + 1)
      else
        x
    loop 0""",
        "is_perfect_square": """partial def integer_sqrt (n : Nat) : Nat :=
  if n = 0 then
    0
  else
    let rec loop (x : Nat) : Nat :=
      if (x + 1) * (x + 1) ≤ n then
        loop (x + 1)
      else
        x
    loop 0

def is_perfect_square (n : Nat) : Bool :=
  let s := integer_sqrt n
  s * s == n""",
        "binomial": """partial def binomial (n k : Nat) : Nat :=
  if k > n then
    0
  else if k = 0 || k = n then
    1
  else
    let k' := if k > n - k then n - k else k
    let rec loop (i result : Nat) : Nat :=
      if i < k' then
        loop (i + 1) (result * (n - i) / (i + 1))
      else
        result
    loop 0 1""",
        "is_even": """def is_even (n : Int) : Bool :=
  n % 2 == 0""",
        "is_odd": """def is_odd (n : Int) : Bool :=
  n % 2 != 0""",
        "triangular_number": """def triangular_number (n : Nat) : Nat :=
  n * (n + 1) / 2""",
        "collatz_steps": """partial def collatz_steps (n : Nat) : Nat :=
  if n = 0 ∨ n = 1 then
    0
  else if n % 2 = 0 then
    1 + collatz_steps (n / 2)
  else
    1 + collatz_steps (3 * n + 1)""",
        "digital_root": """def digital_root (n : Nat) : Nat :=
  if n = 0 then
    0
  else
    1 + (n - 1) % 9""",
    }
    return translations[name]


def get_c_tests(name):
    source = get_c_source(name)
    if name == "integer_sqrt":
        program = source
        main = """int main() {
    assert(integer_sqrt(0) == 0);
    assert(integer_sqrt(1) == 1);
    assert(integer_sqrt(15) == 3);
    assert(integer_sqrt(16) == 4);
    assert(integer_sqrt(17) == 4);
    return 0;
}"""
    elif name == "is_perfect_square":
        program = f"{get_c_source('integer_sqrt')}\n\n{source}"
        main = """int main() {
    assert(is_perfect_square(0) == 1);
    assert(is_perfect_square(1) == 1);
    assert(is_perfect_square(49) == 1);
    assert(is_perfect_square(50) == 0);
    return 0;
}"""
    elif name == "binomial":
        program = source
        main = """int main() {
    assert(binomial(5, 2) == 10);
    assert(binomial(6, 0) == 1);
    assert(binomial(6, 6) == 1);
    assert(binomial(4, 5) == 0);
    return 0;
}"""
    elif name == "is_even":
        program = source
        main = """int main() {
    assert(is_even(4) == 1);
    assert(is_even(-2) == 1);
    assert(is_even(5) == 0);
    return 0;
}"""
    elif name == "is_odd":
        program = source
        main = """int main() {
    assert(is_odd(5) == 1);
    assert(is_odd(-3) == 1);
    assert(is_odd(4) == 0);
    return 0;
}"""
    elif name == "triangular_number":
        program = source
        main = """int main() {
    assert(triangular_number(0) == 0);
    assert(triangular_number(1) == 1);
    assert(triangular_number(5) == 15);
    assert(triangular_number(10) == 55);
    return 0;
}"""
    elif name == "collatz_steps":
        program = source
        main = """int main() {
    assert(collatz_steps(0) == 0);
    assert(collatz_steps(1) == 0);
    assert(collatz_steps(2) == 1);
    assert(collatz_steps(3) == 7);
    assert(collatz_steps(6) == 8);
    return 0;
}"""
    elif name == "digital_root":
        program = source
        main = """int main() {
    assert(digital_root(0) == 0);
    assert(digital_root(9) == 9);
    assert(digital_root(38) == 2);
    assert(digital_root(9999) == 9);
    return 0;
}"""
    else:
        raise KeyError(name)
    return f"#include <assert.h>\n\n{program}\n\n{main}"


def get_py_tests(name):
    source = get_py_source(name)
    if name == "integer_sqrt":
        program = source
        tests = """assert integer_sqrt(0) == 0
assert integer_sqrt(1) == 1
assert integer_sqrt(15) == 3
assert integer_sqrt(16) == 4
assert integer_sqrt(17) == 4"""
    elif name == "is_perfect_square":
        program = f"{get_py_source('integer_sqrt')}\n\n{source}"
        tests = """assert is_perfect_square(0) is True
assert is_perfect_square(1) is True
assert is_perfect_square(49) is True
assert is_perfect_square(50) is False"""
    elif name == "binomial":
        program = source
        tests = """assert binomial(5, 2) == 10
assert binomial(6, 0) == 1
assert binomial(6, 6) == 1
assert binomial(4, 5) == 0"""
    elif name == "is_even":
        program = source
        tests = """assert is_even(4) is True
assert is_even(-2) is True
assert is_even(5) is False"""
    elif name == "is_odd":
        program = source
        tests = """assert is_odd(5) is True
assert is_odd(-3) is True
assert is_odd(4) is False"""
    elif name == "triangular_number":
        program = source
        tests = """assert triangular_number(0) == 0
assert triangular_number(1) == 1
assert triangular_number(5) == 15
assert triangular_number(10) == 55"""
    elif name == "collatz_steps":
        program = source
        tests = """assert collatz_steps(0) == 0
assert collatz_steps(1) == 0
assert collatz_steps(2) == 1
assert collatz_steps(3) == 7
assert collatz_steps(6) == 8"""
    elif name == "digital_root":
        program = source
        tests = """assert digital_root(0) == 0
assert digital_root(9) == 9
assert digital_root(38) == 2
assert digital_root(9999) == 9"""
    else:
        raise KeyError(name)
    return f"{program}\n\n{tests}"


def get_lean_tests(name, lang):
    del lang
    tests = {
        "integer_sqrt": """#eval integer_sqrt 0
#eval integer_sqrt 1
#eval integer_sqrt 15
#eval integer_sqrt 16
#eval integer_sqrt 17""",
        "is_perfect_square": """#eval is_perfect_square 0
#eval is_perfect_square 1
#eval is_perfect_square 49
#eval is_perfect_square 50""",
        "binomial": """#eval binomial 5 2
#eval binomial 6 0
#eval binomial 6 6
#eval binomial 4 5""",
        "is_even": """#eval is_even 4
#eval is_even (-2)
#eval is_even 5""",
        "is_odd": """#eval is_odd 5
#eval is_odd (-3)
#eval is_odd 4""",
        "triangular_number": """#eval triangular_number 0
#eval triangular_number 1
#eval triangular_number 5
#eval triangular_number 10""",
        "collatz_steps": """#eval collatz_steps 0
#eval collatz_steps 1
#eval collatz_steps 2
#eval collatz_steps 3
#eval collatz_steps 6""",
        "digital_root": """#eval digital_root 0
#eval digital_root 9
#eval digital_root 38
#eval digital_root 9999""",
    }
    return tests[name]


def theorem(name, statement, proof, proof_incomplete):
    return {
        "name": name,
        "statement": statement,
        "proof": proof,
        "proof_incomplete": proof_incomplete,
    }


def get_theorems(name, lang):
    del lang
    if name == "integer_sqrt":
        return [
            theorem(
                "integer_sqrt_square_le",
                "theorem integer_sqrt_square_le (n : Nat) : integer_sqrt n * integer_sqrt n ≤ n",
                "by sorry",
                True,
            ),
            theorem(
                "integer_sqrt_lt_next_square",
                "theorem integer_sqrt_lt_next_square (n : Nat) : n < (integer_sqrt n + 1) * (integer_sqrt n + 1)",
                "by sorry",
                True,
            ),
            theorem(
                "integer_sqrt_exact_square",
                "theorem integer_sqrt_exact_square (m : Nat) : integer_sqrt (m * m) = m",
                "by sorry",
                True,
            ),
            theorem(
                "integer_sqrt_monotone",
                "theorem integer_sqrt_monotone {a b : Nat} (h : a ≤ b) : integer_sqrt a ≤ integer_sqrt b",
                "by sorry",
                True,
            ),
        ]
    if name == "is_perfect_square":
        return [
            theorem(
                "is_perfect_square_spec",
                "theorem is_perfect_square_spec (n : Nat) : is_perfect_square n = (((integer_sqrt n) * (integer_sqrt n)) == n)",
                "by rfl",
                False,
            ),
            theorem(
                "is_perfect_square_square",
                "theorem is_perfect_square_square (m : Nat) : is_perfect_square (m * m) = true",
                "by sorry",
                True,
            ),
            theorem(
                "is_perfect_square_eq_true_iff",
                "theorem is_perfect_square_eq_true_iff (n : Nat) : is_perfect_square n = true ↔ ∃ m : Nat, m * m = n",
                "by sorry",
                True,
            ),
        ]
    if name == "binomial":
        return [
            theorem(
                "binomial_zero_right",
                "theorem binomial_zero_right (n : Nat) : binomial n 0 = 1",
                "by simp [binomial]",
                False,
            ),
            theorem(
                "binomial_eq_zero_of_lt",
                "theorem binomial_eq_zero_of_lt (n k : Nat) (h : n < k) : binomial n k = 0",
                "by sorry",
                True,
            ),
            theorem(
                "binomial_self",
                "theorem binomial_self (n : Nat) : binomial n n = 1",
                "by simpa [binomial]",
                False,
            ),
            theorem(
                "binomial_symm",
                "theorem binomial_symm (n k : Nat) (h : k ≤ n) : binomial n k = binomial n (n - k)",
                "by sorry",
                True,
            ),
        ]
    if name == "is_even":
        return [
            theorem(
                "is_even_add_two",
                "theorem is_even_add_two (n : Int) : is_even (n + 2) = is_even n",
                "by sorry",
                True,
            ),
            theorem(
                "is_even_neg",
                "theorem is_even_neg (n : Int) : is_even (-n) = is_even n",
                "by sorry",
                True,
            ),
            theorem(
                "is_even_eq_not_is_odd",
                "theorem is_even_eq_not_is_odd (n : Int) : is_even n = !(is_odd n)",
                "by sorry",
                True,
            ),
        ]
    if name == "is_odd":
        return [
            theorem(
                "is_odd_add_two",
                "theorem is_odd_add_two (n : Int) : is_odd (n + 2) = is_odd n",
                "by sorry",
                True,
            ),
            theorem(
                "is_odd_neg",
                "theorem is_odd_neg (n : Int) : is_odd (-n) = is_odd n",
                "by sorry",
                True,
            ),
            theorem(
                "is_odd_eq_not_is_even",
                "theorem is_odd_eq_not_is_even (n : Int) : is_odd n = !(is_even n)",
                "by sorry",
                True,
            ),
        ]
    if name == "triangular_number":
        return [
            theorem(
                "triangular_number_succ",
                "theorem triangular_number_succ (n : Nat) : triangular_number (n + 1) = triangular_number n + (n + 1)",
                "by sorry",
                True,
            ),
            theorem(
                "two_mul_triangular_number",
                "theorem two_mul_triangular_number (n : Nat) : 2 * triangular_number n = n * (n + 1)",
                "by sorry",
                True,
            ),
            theorem(
                "triangular_number_monotone",
                "theorem triangular_number_monotone {a b : Nat} (h : a ≤ b) : triangular_number a ≤ triangular_number b",
                "by sorry",
                True,
            ),
        ]
    if name == "collatz_steps":
        return [
            theorem(
                "collatz_steps_eq_zero_iff",
                "theorem collatz_steps_eq_zero_iff (n : Nat) : collatz_steps n = 0 ↔ n = 0 ∨ n = 1",
                "by sorry",
                True,
            ),
            theorem(
                "collatz_steps_even_step",
                "theorem collatz_steps_even_step (n : Nat) (h0 : n ≠ 0) (h1 : n ≠ 1) (he : n % 2 = 0) : collatz_steps n = 1 + collatz_steps (n / 2)",
                "by sorry",
                True,
            ),
            theorem(
                "collatz_steps_odd_step",
                "theorem collatz_steps_odd_step (n : Nat) (h0 : n ≠ 0) (h1 : n ≠ 1) (ho : n % 2 = 1) : collatz_steps n = 1 + collatz_steps (3 * n + 1)",
                "by sorry",
                True,
            ),
        ]
    if name == "digital_root":
        return [
            theorem(
                "digital_root_eq_zero_iff",
                "theorem digital_root_eq_zero_iff (n : Nat) : digital_root n = 0 ↔ n = 0",
                "by sorry",
                True,
            ),
            theorem(
                "digital_root_range",
                "theorem digital_root_range (n : Nat) (h : n ≠ 0) : 1 ≤ digital_root n ∧ digital_root n ≤ 9",
                "by sorry",
                True,
            ),
            theorem(
                "digital_root_eq_one_add_mod",
                "theorem digital_root_eq_one_add_mod (n : Nat) (h : n ≠ 0) : digital_root n = 1 + (n - 1) % 9",
                "by simp [digital_root, h]",
                False,
            ),
            theorem(
                "digital_root_nine_multiple",
                "theorem digital_root_nine_multiple (k : Nat) (h : k ≠ 0) : digital_root (9 * k) = 9",
                "by sorry",
                True,
            ),
        ]
    raise KeyError(name)


def get_deps_fully_translated(name):
    deps = {
        "integer_sqrt": [],
        "is_perfect_square": ["integer_sqrt"],
        "binomial": [],
        "is_even": [],
        "is_odd": [],
        "triangular_number": [],
        "collatz_steps": [],
        "digital_root": [],
    }
    return deps[name]


FUNCTIONS = [
    "integer_sqrt",
    "is_perfect_square",
    "binomial",
    "is_even",
    "is_odd",
    "triangular_number",
    "collatz_steps",
    "digital_root",
]


def main():
    output_path = Path(
        "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch08_math2.jsonl"
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        for lang in ("C", "Python"):
            for name in FUNCTIONS:
                record = {
                    "language": lang,
                    "source": get_c_source(name) if lang == "C" else get_py_source(name),
                    "lean_translation": get_lean_translation(name, lang),
                    "tests": get_c_tests(name) if lang == "C" else get_py_tests(name),
                    "lean_tests": get_lean_tests(name, lang),
                    "theorems": get_theorems(name, lang),
                    "deps_fully_translated": get_deps_fully_translated(name),
                    "axiomatized_deps": [],
                    "skip_reason": None,
                }
                handle.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
