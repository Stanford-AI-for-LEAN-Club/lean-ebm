import json
import os

def generate_jsonl():
    functions = [
        "gcd", "lcm", "power", "is_prime", "mod_exp", "sum_digits", "count_digits"
    ]

    # C Source Codes
    c_sources = {
        "gcd": """unsigned int gcd(unsigned int a, unsigned int b) {
    while (b != 0) {
        unsigned int t = b;
        b = a % b;
        a = t;
    }
    return a;
}""",
        "lcm": """unsigned int lcm(unsigned int a, unsigned int b) {
    if (a == 0 || b == 0) return 0;
    return (a / gcd(a, b)) * b;
}""",
        "power": """unsigned int power(unsigned int base, unsigned int exp) {
    unsigned int result = 1;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result *= base;
        }
        base *= base;
        exp /= 2;
    }
    return result;
}""",
        "is_prime": """int is_prime(unsigned int n) {
    if (n < 2) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;
    for (unsigned int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}""",
        "mod_exp": """unsigned int mod_exp(unsigned int base, unsigned int exp, unsigned int mod) {
    if (mod == 0) return 0;
    unsigned int result = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        exp /= 2;
        base = (base * base) % mod;
    }
    return result;
}""",
        "sum_digits": """unsigned int sum_digits(unsigned int n) {
    unsigned int s = 0;
    while (n > 0) {
        s += n % 10;
        n /= 10;
    }
    return s;
}""",
        "count_digits": """unsigned int count_digits(unsigned int n) {
    if (n == 0) return 1;
    unsigned int c = 0;
    while (n > 0) {
        c++;
        n /= 10;
    }
    return c;
}"""
    }

    # Python Source Codes
    py_sources = {
        "gcd": """def gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a""",
        "lcm": """def lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return (a // gcd(a, b)) * b""",
        "power": """def power(base: int, exp: int) -> int:
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result *= base
        base *= base
        exp //= 2
    return result""",
        "is_prime": """def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True""",
        "mod_exp": """def mod_exp(base: int, exp: int, mod: int) -> int:
    if mod == 0:
        return 0
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    return result""",
        "sum_digits": """def sum_digits(n: int) -> int:
    s = 0
    while n > 0:
        s += n % 10
        n //= 10
    return s""",
        "count_digits": """def count_digits(n: int) -> int:
    if n == 0:
        return 1
    c = 0
    while n > 0:
        c += 1
        n //= 10
    return c"""
    }

    # Lean4 Translations (using Nat for provability as requested)
    lean_translations = {
        "gcd": """def gcd (a b : Nat) : Nat :=
  if h : b = 0 then a else
  gcd b (a % b)
termination_by b
decreasing_by
  simp [h]
  apply Nat.mod_lt
  exact Nat.pos_of_ne_zero h""",
        "lcm": """def gcd (a b : Nat) : Nat :=
  if h : b = 0 then a else
  gcd b (a % b)
termination_by b
decreasing_by
  simp [h]
  apply Nat.mod_lt
  exact Nat.pos_of_ne_zero h

def lcm (a b : Nat) : Nat :=
  if a = 0 || b = 0 then 0
  else (a / gcd a b) * b""",
        "power": """def power (base exp : Nat) : Nat :=
  if h : exp = 0 then 1
  else 
    let res := power (base * base) (exp / 2)
    if exp % 2 = 1 then base * res else res
termination_by exp
decreasing_by
  simp [h]
  apply Nat.div_lt_self
  · apply Nat.pos_of_ne_zero h
  · decide""",
        "is_prime": """def is_prime (n : Nat) : Bool :=
  if n < 2 then false
  else if n = 2 then true
  else if n % 2 = 0 then false
  else 
    let rec loop (i : Nat) : Bool :=
      if h : i * i > n then true
      else if n % i = 0 then false
      else loop (i + 2)
    termination_by n - i
    decreasing_by sorry
    loop 3""",
        "mod_exp": """def mod_exp (base exp mod : Nat) : Nat :=
  if mod = 0 then 0
  else if h : exp = 0 then 1 % mod
  else 
    let res := mod_exp ((base * base) % mod) (exp / 2) mod
    if exp % 2 = 1 then (base % mod * res) % mod else res
termination_by exp
decreasing_by
  simp [h]
  apply Nat.div_lt_self
  · apply Nat.pos_of_ne_zero h
  · decide""",
        "sum_digits": """def sum_digits (n : Nat) : Nat :=
  if h : n = 0 then 0
  else (n % 10) + sum_digits (n / 10)
termination_by n
decreasing_by
  simp [h]
  apply Nat.div_lt_self
  · apply Nat.pos_of_ne_zero h
  · decide""",
        "count_digits": """def count_digits (n : Nat) : Nat :=
  if h : n < 10 then 1
  else 1 + count_digits (n / 10)
termination_by n
decreasing_by
  simp at h
  apply Nat.div_lt_self
  · apply Nat.lt_of_succ_le
    apply Nat.le_trans (by show 10 <= n; exact h) (Nat.le_refl n)
  · decide"""
    }

    # C/Python Tests
    c_tests = {
        "gcd": """#include <assert.h>
{source}
int main() {{
    assert(gcd(48, 18) == 6);
    assert(gcd(101, 103) == 1);
    assert(gcd(0, 5) == 5);
    assert(gcd(5, 0) == 5);
    return 0;
}}""",
        "lcm": """#include <assert.h>
unsigned int gcd(unsigned int a, unsigned int b) {{
    while (b != 0) {{
        unsigned int t = b;
        b = a % b;
        a = t;
    }}
    return a;
}}
{source}
int main() {{
    assert(lcm(12, 18) == 36);
    assert(lcm(0, 5) == 0);
    assert(lcm(7, 3) == 21);
    return 0;
}}""",
        "power": """#include <assert.h>
{source}
int main() {{
    assert(power(2, 10) == 1024);
    assert(power(3, 4) == 81);
    assert(power(5, 0) == 1);
    return 0;
}}""",
        "is_prime": """#include <assert.h>
{source}
int main() {{
    assert(is_prime(2) == 1);
    assert(is_prime(7) == 1);
    assert(is_prime(10) == 0);
    assert(is_prime(1) == 0);
    assert(is_prime(0) == 0);
    assert(is_prime(25) == 0);
    return 0;
}}""",
        "mod_exp": """#include <assert.h>
{source}
int main() {{
    assert(mod_exp(2, 10, 1000) == 24);
    assert(mod_exp(5, 3, 13) == 8);
    assert(mod_exp(10, 0, 7) == 1);
    return 0;
}}""",
        "sum_digits": """#include <assert.h>
{source}
int main() {{
    assert(sum_digits(123) == 6);
    assert(sum_digits(0) == 0);
    assert(sum_digits(999) == 27);
    return 0;
}}""",
        "count_digits": """#include <assert.h>
{source}
int main() {{
    assert(count_digits(123) == 3);
    assert(count_digits(0) == 1);
    assert(count_digits(1000) == 4);
    return 0;
}}"""
    }

    py_tests = {
        "gcd": """{source}
assert gcd(48, 18) == 6
assert gcd(101, 103) == 1
assert gcd(0, 5) == 5
assert gcd(5, 0) == 5""",
        "lcm": """{source}
# Assuming gcd is available if needed
def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a
{source}
assert lcm(12, 18) == 36
assert lcm(0, 5) == 0
assert lcm(7, 3) == 21""",
        "power": """{source}
assert power(2, 10) == 1024
assert power(3, 4) == 81
assert power(5, 0) == 1""",
        "is_prime": """{source}
assert is_prime(2) == True
assert is_prime(7) == True
assert is_prime(10) == False
assert is_prime(1) == False
assert is_prime(0) == False
assert is_prime(25) == False""",
        "mod_exp": """{source}
assert mod_exp(2, 10, 1000) == 24
assert mod_exp(5, 3, 13) == 8
assert mod_exp(10, 0, 7) == 1""",
        "sum_digits": """{source}
assert sum_digits(123) == 6
assert sum_digits(0) == 0
assert sum_digits(999) == 27""",
        "count_digits": """{source}
assert count_digits(123) == 3
assert count_digits(0) == 1
assert count_digits(1000) == 4"""
    }

    lean_tests = {
        "gcd": """#eval gcd 48 18
#eval gcd 101 103
#eval gcd 0 5
#eval gcd 5 0""",
        "lcm": """#eval lcm 12 18
#eval lcm 0 5
#eval lcm 7 3""",
        "power": """#eval power 2 10
#eval power 3 4
#eval power 5 0""",
        "is_prime": """#eval is_prime 2
#eval is_prime 7
#eval is_prime 10
#eval is_prime 1
#eval is_prime 0
#eval is_prime 25""",
        "mod_exp": """#eval mod_exp 2 10 1000
#eval mod_exp 5 3 13
#eval mod_exp 10 0 7""",
        "sum_digits": """#eval sum_digits 123
#eval sum_digits 0
#eval sum_digits 999""",
        "count_digits": """#eval count_digits 123
#eval count_digits 0
#eval count_digits 1000"""
    }

    theorems = {
        "gcd": [
            {"name": "gcd_eq_nat_gcd", "statement": "theorem gcd_eq_nat_gcd (a b : Nat) : gcd a b = Nat.gcd a b", "proof": "by sorry", "proof_incomplete": True},
            {"name": "gcd_comm", "statement": "theorem gcd_comm (a b : Nat) : gcd a b = gcd b a", "proof": "by sorry", "proof_incomplete": True},
            {"name": "gcd_divides_left", "statement": "theorem gcd_divides_left (a b : Nat) : gcd a b ∣ a", "proof": "by sorry", "proof_incomplete": True}
        ],
        "lcm": [
            {"name": "lcm_eq_nat_lcm", "statement": "theorem lcm_eq_nat_lcm (a b : Nat) : lcm a b = Nat.lcm a b", "proof": "by sorry", "proof_incomplete": True},
            {"name": "lcm_comm", "statement": "theorem lcm_comm (a b : Nat) : lcm a b = lcm b a", "proof": "by sorry", "proof_incomplete": True},
            {"name": "lcm_is_multiple_left", "statement": "theorem lcm_is_multiple_left (a b : Nat) : a ∣ lcm a b", "proof": "by sorry", "proof_incomplete": True}
        ],
        "power": [
            {"name": "power_eq_pow", "statement": "theorem power_eq_pow (base exp : Nat) : power base exp = base ^ exp", "proof": "by sorry", "proof_incomplete": True},
            {"name": "power_zero", "statement": "theorem power_zero (base : Nat) : power base 0 = 1", "proof": "by rfl", "proof_incomplete": False},
            {"name": "power_one", "statement": "theorem power_one (base : Nat) : power base 1 = base", "proof": "by sorry", "proof_incomplete": True}
        ],
        "is_prime": [
            {"name": "is_prime_eq_nat_prime", "statement": "theorem is_prime_eq_nat_prime (n : Nat) : is_prime n = Nat.isPrime n", "proof": "by sorry", "proof_incomplete": True},
            {"name": "is_prime_two", "statement": "theorem is_prime_two : is_prime 2 = true", "proof": "by rfl", "proof_incomplete": False},
            {"name": "is_prime_gt_one", "statement": "theorem is_prime_gt_one (n : Nat) : is_prime n = true → n > 1", "proof": "by sorry", "proof_incomplete": True}
        ],
        "mod_exp": [
            {"name": "mod_exp_eq_pow_mod", "statement": "theorem mod_exp_eq_pow_mod (base exp mod : Nat) : mod > 0 → mod_exp base exp mod = (base ^ exp) % mod", "proof": "by sorry", "proof_incomplete": True},
            {"name": "mod_exp_lt_mod", "statement": "theorem mod_exp_lt_mod (base exp mod : Nat) : mod > 0 → mod_exp base exp mod < mod", "proof": "by sorry", "proof_incomplete": True}
        ],
        "sum_digits": [
            {"name": "sum_digits_le", "statement": "theorem sum_digits_le (n : Nat) : sum_digits n <= n", "proof": "by sorry", "proof_incomplete": True},
            {"name": "sum_digits_zero", "statement": "theorem sum_digits_zero : sum_digits 0 = 0", "proof": "by rfl", "proof_incomplete": False},
            {"name": "sum_digits_mod_9", "statement": "theorem sum_digits_mod_9 (n : Nat) : sum_digits n % 9 = n % 9", "proof": "by sorry", "proof_incomplete": True}
        ],
        "count_digits": [
            {"name": "count_digits_pos", "statement": "theorem count_digits_pos (n : Nat) : count_digits n >= 1", "proof": "by sorry", "proof_incomplete": True},
            {"name": "count_digits_eq_one_iff", "statement": "theorem count_digits_eq_one_iff (n : Nat) : count_digits n = 1 <-> n < 10", "proof": "by sorry", "proof_incomplete": True}
        ]
    }

    output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch02_gcd_math.jsonl"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w") as f:
        for lang in ["C", "Python"]:
            for name in functions:
                source = c_sources[name] if lang == "C" else py_sources[name]
                tests = c_tests[name].format(source=source) if lang == "C" else py_tests[name].format(source=source)
                
                record = {
                    "language": lang,
                    "source": source,
                    "lean_translation": lean_translations[name],
                    "tests": tests,
                    "lean_tests": lean_tests[name],
                    "theorems": theorems[name],
                    "deps_fully_translated": [],
                    "axiomatized_deps": [],
                    "skip_reason": None
                }
                f.write(json.dumps(record) + "\n")

if __name__ == "__main__":
    generate_jsonl()
