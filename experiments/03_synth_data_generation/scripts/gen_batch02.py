"""Generate JSONL for batch02_gcd_math: gcd, lcm, power, is_prime, mod_exp, sum_digits, count_digits."""
import json, os

FUNCTIONS = ["gcd", "lcm", "power", "is_prime", "mod_exp", "sum_digits", "count_digits"]

C_SOURCES = {
    "gcd": "unsigned int gcd(unsigned int a, unsigned int b) {\n    while (b != 0) {\n        unsigned int t = b;\n        b = a % b;\n        a = t;\n    }\n    return a;\n}",
    "lcm": "unsigned int lcm(unsigned int a, unsigned int b) {\n    if (a == 0 || b == 0) return 0;\n    return (a / gcd(a, b)) * b;\n}",
    "power": "unsigned int power(unsigned int base, unsigned int exp) {\n    unsigned int result = 1;\n    while (exp > 0) {\n        if (exp % 2 == 1) result *= base;\n        base *= base;\n        exp /= 2;\n    }\n    return result;\n}",
    "is_prime": "int is_prime(unsigned int n) {\n    if (n < 2) return 0;\n    if (n == 2) return 1;\n    if (n % 2 == 0) return 0;\n    for (unsigned int i = 3; i * i <= n; i += 2) {\n        if (n % i == 0) return 0;\n    }\n    return 1;\n}",
    "mod_exp": "unsigned int mod_exp(unsigned int base, unsigned int exp, unsigned int mod) {\n    if (mod == 0) return 0;\n    unsigned int result = 1;\n    base = base % mod;\n    while (exp > 0) {\n        if (exp % 2 == 1) result = (result * base) % mod;\n        exp /= 2;\n        base = (base * base) % mod;\n    }\n    return result;\n}",
    "sum_digits": "unsigned int sum_digits(unsigned int n) {\n    unsigned int s = 0;\n    while (n > 0) {\n        s += n % 10;\n        n /= 10;\n    }\n    return s;\n}",
    "count_digits": "unsigned int count_digits(unsigned int n) {\n    if (n == 0) return 1;\n    unsigned int c = 0;\n    while (n > 0) { c++; n /= 10; }\n    return c;\n}",
}

PY_SOURCES = {
    "gcd": "def gcd(a: int, b: int) -> int:\n    while b != 0:\n        a, b = b, a % b\n    return a",
    "lcm": "def lcm(a: int, b: int) -> int:\n    if a == 0 or b == 0:\n        return 0\n    return (a // gcd(a, b)) * b",
    "power": "def power(base: int, exp: int) -> int:\n    result = 1\n    while exp > 0:\n        if exp % 2 == 1:\n            result *= base\n        base *= base\n        exp //= 2\n    return result",
    "is_prime": "def is_prime(n: int) -> bool:\n    if n < 2: return False\n    if n == 2: return True\n    if n % 2 == 0: return False\n    i = 3\n    while i * i <= n:\n        if n % i == 0: return False\n        i += 2\n    return True",
    "mod_exp": "def mod_exp(base: int, exp: int, mod: int) -> int:\n    if mod == 0: return 0\n    result = 1\n    base = base % mod\n    while exp > 0:\n        if exp % 2 == 1: result = (result * base) % mod\n        exp //= 2\n        base = (base * base) % mod\n    return result",
    "sum_digits": "def sum_digits(n: int) -> int:\n    s = 0\n    while n > 0:\n        s += n % 10\n        n //= 10\n    return s",
    "count_digits": "def count_digits(n: int) -> int:\n    if n == 0: return 1\n    c = 0\n    while n > 0:\n        c += 1\n        n //= 10\n    return c",
}

LEAN_TRANSLATIONS = {
    "gcd": {
        "C": "def gcd (a b : Nat) : Nat :=\n  if h : b = 0 then a else gcd b (a % b)\ntermination_by b\ndecreasing_by exact Nat.mod_lt a (Nat.pos_of_ne_zero h)",
        "Python": "def gcd (a b : Nat) : Nat :=\n  if h : b = 0 then a else gcd b (a % b)\ntermination_by b\ndecreasing_by exact Nat.mod_lt a (Nat.pos_of_ne_zero h)",
    },
    "lcm": {
        "C": "def lcm (a b : Nat) : Nat :=\n  if a = 0 || b = 0 then 0 else (a / Nat.gcd a b) * b",
        "Python": "def lcm (a b : Nat) : Nat :=\n  if a = 0 || b = 0 then 0 else (a / Nat.gcd a b) * b",
    },
    "power": {
        "C": "def power (base exp : Nat) : Nat :=\n  match exp with\n  | 0 => 1\n  | e + 1 => base * power base e",
        "Python": "def power (base exp : Nat) : Nat :=\n  match exp with\n  | 0 => 1\n  | e + 1 => base * power base e",
    },
    "is_prime": {
        "C": "def is_prime (n : Nat) : Bool :=\n  if n < 2 then false\n  else if n = 2 then true\n  else if n % 2 = 0 then false\n  else Id.run do\n    let mut i := 3\n    while i * i <= n do\n      if n % i = 0 then return false\n      i := i + 2\n    return true",
        "Python": "def is_prime (n : Nat) : Bool :=\n  if n < 2 then false\n  else if n = 2 then true\n  else if n % 2 = 0 then false\n  else Id.run do\n    let mut i := 3\n    while i * i <= n do\n      if n % i = 0 then return false\n      i := i + 2\n    return true",
    },
    "mod_exp": {
        "C": "def mod_exp (base exp mod : Nat) : Nat :=\n  if mod = 0 then 0 else (base ^ exp) % mod",
        "Python": "def mod_exp (base exp mod : Nat) : Nat :=\n  if mod = 0 then 0 else (base ^ exp) % mod",
    },
    "sum_digits": {
        "C": "def sum_digits (n : Nat) : Nat :=\n  if h : n = 0 then 0 else n % 10 + sum_digits (n / 10)\ntermination_by n\ndecreasing_by exact Nat.div_lt_self (Nat.pos_of_ne_zero h) (by omega)",
        "Python": "def sum_digits (n : Nat) : Nat :=\n  if h : n = 0 then 0 else n % 10 + sum_digits (n / 10)\ntermination_by n\ndecreasing_by exact Nat.div_lt_self (Nat.pos_of_ne_zero h) (by omega)",
    },
    "count_digits": {
        "C": "def count_digits (n : Nat) : Nat :=\n  if n = 0 then 1\n  else\n    let rec loop (val count : Nat) : Nat :=\n      if val = 0 then count else loop (val / 10) (count + 1)\n    loop n 0\ntermination_by n",
        "Python": "def count_digits (n : Nat) : Nat :=\n  if n = 0 then 1\n  else\n    let rec loop (val count : Nat) : Nat :=\n      if val = 0 then count else loop (val / 10) (count + 1)\n    loop n 0\ntermination_by n",
    },
}

C_TESTS = {
    "gcd": '#include <assert.h>\nunsigned int gcd(unsigned int a, unsigned int b) { while (b != 0) { unsigned int t = b; b = a % b; a = t; } return a; }\nint main() { assert(gcd(48, 18) == 6); assert(gcd(101, 103) == 1); assert(gcd(0, 5) == 5); assert(gcd(7, 0) == 7); return 0; }',
    "lcm": '#include <assert.h>\nunsigned int gcd(unsigned int a, unsigned int b) { while (b != 0) { unsigned int t = b; b = a % b; a = t; } return a; }\nunsigned int lcm(unsigned int a, unsigned int b) { if (a == 0 || b == 0) return 0; return (a / gcd(a, b)) * b; }\nint main() { assert(lcm(12, 18) == 36); assert(lcm(0, 5) == 0); assert(lcm(7, 1) == 7); return 0; }',
    "power": '#include <assert.h>\nunsigned int power(unsigned int base, unsigned int exp) { unsigned int result = 1; while (exp > 0) { if (exp % 2 == 1) result *= base; base *= base; exp /= 2; } return result; }\nint main() { assert(power(2, 10) == 1024); assert(power(3, 4) == 81); assert(power(5, 0) == 1); assert(power(1, 100) == 1); return 0; }',
    "is_prime": '#include <assert.h>\nint is_prime(unsigned int n) { if (n < 2) return 0; if (n == 2) return 1; if (n % 2 == 0) return 0; for (unsigned int i = 3; i * i <= n; i += 2) { if (n % i == 0) return 0; } return 1; }\nint main() { assert(is_prime(2) == 1); assert(is_prime(7) == 1); assert(is_prime(10) == 0); assert(is_prime(1) == 0); assert(is_prime(0) == 0); return 0; }',
    "mod_exp": '#include <assert.h>\nunsigned int mod_exp(unsigned int base, unsigned int exp, unsigned int mod) { if (mod == 0) return 0; unsigned int result = 1; base = base % mod; while (exp > 0) { if (exp % 2 == 1) result = (result * base) % mod; exp /= 2; base = (base * base) % mod; } return result; }\nint main() { assert(mod_exp(2, 10, 1000) == 24); assert(mod_exp(5, 3, 13) == 8); assert(mod_exp(7, 0, 5) == 1); return 0; }',
    "sum_digits": '#include <assert.h>\nunsigned int sum_digits(unsigned int n) { unsigned int s = 0; while (n > 0) { s += n % 10; n /= 10; } return s; }\nint main() { assert(sum_digits(123) == 6); assert(sum_digits(0) == 0); assert(sum_digits(9999) == 36); return 0; }',
    "count_digits": '#include <assert.h>\nunsigned int count_digits(unsigned int n) { if (n == 0) return 1; unsigned int c = 0; while (n > 0) { c++; n /= 10; } return c; }\nint main() { assert(count_digits(123) == 3); assert(count_digits(0) == 1); assert(count_digits(9) == 1); assert(count_digits(10) == 2); return 0; }',
}

PY_TESTS = {
    "gcd": "def gcd(a, b):\n    while b != 0: a, b = b, a % b\n    return a\nassert gcd(48, 18) == 6\nassert gcd(101, 103) == 1\nassert gcd(0, 5) == 5\nassert gcd(7, 0) == 7",
    "lcm": "def gcd(a, b):\n    while b != 0: a, b = b, a % b\n    return a\ndef lcm(a, b):\n    if a == 0 or b == 0: return 0\n    return (a // gcd(a, b)) * b\nassert lcm(12, 18) == 36\nassert lcm(0, 5) == 0\nassert lcm(7, 1) == 7",
    "power": "def power(base, exp):\n    result = 1\n    while exp > 0:\n        if exp % 2 == 1: result *= base\n        base *= base\n        exp //= 2\n    return result\nassert power(2, 10) == 1024\nassert power(3, 4) == 81\nassert power(5, 0) == 1",
    "is_prime": "def is_prime(n):\n    if n < 2: return False\n    if n == 2: return True\n    if n % 2 == 0: return False\n    i = 3\n    while i * i <= n:\n        if n % i == 0: return False\n        i += 2\n    return True\nassert is_prime(2)\nassert is_prime(7)\nassert not is_prime(10)\nassert not is_prime(1)",
    "mod_exp": "def mod_exp(base, exp, mod):\n    if mod == 0: return 0\n    result = 1\n    base = base % mod\n    while exp > 0:\n        if exp % 2 == 1: result = (result * base) % mod\n        exp //= 2\n        base = (base * base) % mod\n    return result\nassert mod_exp(2, 10, 1000) == 24\nassert mod_exp(5, 3, 13) == 8",
    "sum_digits": "def sum_digits(n):\n    s = 0\n    while n > 0: s += n % 10; n //= 10\n    return s\nassert sum_digits(123) == 6\nassert sum_digits(0) == 0\nassert sum_digits(9999) == 36",
    "count_digits": "def count_digits(n):\n    if n == 0: return 1\n    c = 0\n    while n > 0: c += 1; n //= 10\n    return c\nassert count_digits(123) == 3\nassert count_digits(0) == 1\nassert count_digits(9) == 1",
}

LEAN_TESTS = {
    "gcd": "#eval gcd 48 18  -- 6\n#eval gcd 101 103  -- 1\n#eval gcd 0 5  -- 5",
    "lcm": "#eval lcm 12 18  -- 36\n#eval lcm 0 5  -- 0",
    "power": "#eval power 2 10  -- 1024\n#eval power 3 4  -- 81\n#eval power 5 0  -- 1",
    "is_prime": "#eval is_prime 2  -- true\n#eval is_prime 7  -- true\n#eval is_prime 10  -- false",
    "mod_exp": "#eval mod_exp 2 10 1000  -- 24\n#eval mod_exp 5 3 13  -- 8",
    "sum_digits": "#eval sum_digits 123  -- 6\n#eval sum_digits 0  -- 0",
    "count_digits": "#eval count_digits 123  -- 3\n#eval count_digits 0  -- 1",
}

THEOREMS = {
    "gcd": [
        {"name": "gcd_comm", "statement": "theorem gcd_comm (a b : Nat) : gcd a b = gcd b a", "proof": "by sorry", "proof_incomplete": True},
        {"name": "gcd_zero_right", "statement": "theorem gcd_zero_right (a : Nat) : gcd a 0 = a", "proof": "by unfold gcd; simp", "proof_incomplete": False},
        {"name": "gcd_self", "statement": "theorem gcd_self (a : Nat) : gcd a a = a", "proof": "by sorry", "proof_incomplete": True},
        {"name": "gcd_dvd_left", "statement": "theorem gcd_dvd_left (a b : Nat) : gcd a b ∣ a", "proof": "by sorry", "proof_incomplete": True},
    ],
    "lcm": [
        {"name": "lcm_comm", "statement": "theorem lcm_comm (a b : Nat) : lcm a b = lcm b a", "proof": "by sorry", "proof_incomplete": True},
        {"name": "lcm_zero_left", "statement": "theorem lcm_zero_left (b : Nat) : lcm 0 b = 0", "proof": "by simp [lcm]", "proof_incomplete": False},
        {"name": "lcm_dvd_left", "statement": "theorem lcm_dvd_left (a b : Nat) : a ∣ lcm a b", "proof": "by sorry", "proof_incomplete": True},
    ],
    "power": [
        {"name": "power_zero_exp", "statement": "theorem power_zero_exp (b : Nat) : power b 0 = 1", "proof": "by simp [power]", "proof_incomplete": False},
        {"name": "power_one_exp", "statement": "theorem power_one_exp (b : Nat) : power b 1 = b", "proof": "by simp [power]", "proof_incomplete": False},
        {"name": "power_eq_pow", "statement": "theorem power_eq_pow (b e : Nat) : power b e = b ^ e", "proof": "by sorry", "proof_incomplete": True},
    ],
    "is_prime": [
        {"name": "is_prime_implies_gt_one", "statement": "theorem is_prime_implies_gt_one (n : Nat) : is_prime n = true → n > 1", "proof": "by sorry", "proof_incomplete": True},
        {"name": "not_is_prime_zero", "statement": "theorem not_is_prime_zero : is_prime 0 = false", "proof": "by simp [is_prime]", "proof_incomplete": False},
        {"name": "not_is_prime_one", "statement": "theorem not_is_prime_one : is_prime 1 = false", "proof": "by simp [is_prime]", "proof_incomplete": False},
    ],
    "mod_exp": [
        {"name": "mod_exp_eq_pow_mod", "statement": "theorem mod_exp_eq_pow_mod (b e m : Nat) : m > 0 → mod_exp b e m = (b ^ e) % m", "proof": "by sorry", "proof_incomplete": True},
        {"name": "mod_exp_lt_mod", "statement": "theorem mod_exp_lt_mod (b e m : Nat) : m > 0 → mod_exp b e m < m", "proof": "by sorry", "proof_incomplete": True},
        {"name": "mod_exp_zero_exp", "statement": "theorem mod_exp_zero_exp (b m : Nat) : m > 0 → mod_exp b 0 m = 1 % m", "proof": "by sorry", "proof_incomplete": True},
    ],
    "sum_digits": [
        {"name": "sum_digits_zero", "statement": "theorem sum_digits_zero : sum_digits 0 = 0", "proof": "by unfold sum_digits; simp", "proof_incomplete": False},
        {"name": "sum_digits_le", "statement": "theorem sum_digits_le (n : Nat) : sum_digits n ≤ n", "proof": "by sorry", "proof_incomplete": True},
        {"name": "sum_digits_mod_nine", "statement": "theorem sum_digits_mod_nine (n : Nat) : sum_digits n % 9 = n % 9", "proof": "by sorry", "proof_incomplete": True},
    ],
    "count_digits": [
        {"name": "count_digits_pos", "statement": "theorem count_digits_pos (n : Nat) : count_digits n ≥ 1", "proof": "by sorry", "proof_incomplete": True},
        {"name": "count_digits_zero", "statement": "theorem count_digits_zero : count_digits 0 = 1", "proof": "by simp [count_digits]", "proof_incomplete": False},
        {"name": "count_digits_single", "statement": "theorem count_digits_single (n : Nat) : n > 0 → n < 10 → count_digits n = 1", "proof": "by sorry", "proof_incomplete": True},
    ],
}

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch02_gcd_math.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    for lang in ["C", "Python"]:
        for name in FUNCTIONS:
            record = {
                "language": lang,
                "source": C_SOURCES[name] if lang == "C" else PY_SOURCES[name],
                "lean_translation": LEAN_TRANSLATIONS[name][lang],
                "tests": C_TESTS[name] if lang == "C" else PY_TESTS[name],
                "lean_tests": LEAN_TESTS[name],
                "theorems": THEOREMS[name],
                "deps_fully_translated": [],
                "axiomatized_deps": [],
                "skip_reason": None,
            }
            f.write(json.dumps(record) + "\n")

print(f"Generated {output_path} with {len(FUNCTIONS) * 2} records")
