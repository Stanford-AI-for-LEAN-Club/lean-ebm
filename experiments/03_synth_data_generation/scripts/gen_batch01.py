"""Generate JSONL for batch01_arithmetic: abs_val, max_of_two, min_of_two, clamp, factorial, fibonacci, sign."""
import json, os

FUNCTIONS = ["abs_val", "max_of_two", "min_of_two", "clamp", "factorial", "fibonacci", "sign"]

C_SOURCES = {
    "abs_val": "int abs_val(int x) {\n    if (x < 0) return -x;\n    return x;\n}",
    "max_of_two": "int max_of_two(int a, int b) {\n    if (a >= b) return a;\n    return b;\n}",
    "min_of_two": "int min_of_two(int a, int b) {\n    if (a <= b) return a;\n    return b;\n}",
    "clamp": "int clamp(int x, int lo, int hi) {\n    if (x < lo) return lo;\n    if (x > hi) return hi;\n    return x;\n}",
    "factorial": "unsigned int factorial(unsigned int n) {\n    unsigned int result = 1;\n    for (unsigned int i = 2; i <= n; i++) {\n        result *= i;\n    }\n    return result;\n}",
    "fibonacci": "unsigned int fibonacci(unsigned int n) {\n    if (n <= 1) return n;\n    unsigned int a = 0, b = 1;\n    for (unsigned int i = 2; i <= n; i++) {\n        unsigned int tmp = a + b;\n        a = b;\n        b = tmp;\n    }\n    return b;\n}",
    "sign": "int sign(int x) {\n    if (x > 0) return 1;\n    if (x < 0) return -1;\n    return 0;\n}",
}

PY_SOURCES = {
    "abs_val": "def abs_val(x: int) -> int:\n    if x < 0:\n        return -x\n    return x",
    "max_of_two": "def max_of_two(a: int, b: int) -> int:\n    if a >= b:\n        return a\n    return b",
    "min_of_two": "def min_of_two(a: int, b: int) -> int:\n    if a <= b:\n        return a\n    return b",
    "clamp": "def clamp(x: int, lo: int, hi: int) -> int:\n    if x < lo:\n        return lo\n    if x > hi:\n        return hi\n    return x",
    "factorial": "def factorial(n: int) -> int:\n    result = 1\n    for i in range(2, n + 1):\n        result *= i\n    return result",
    "fibonacci": "def fibonacci(n: int) -> int:\n    if n <= 1:\n        return n\n    a, b = 0, 1\n    for _ in range(2, n + 1):\n        a, b = b, a + b\n    return b",
    "sign": "def sign(x: int) -> int:\n    if x > 0:\n        return 1\n    if x < 0:\n        return -1\n    return 0",
}

LEAN = {
    "abs_val": "def abs_val (x : Int) : Int :=\n  if x < 0 then -x else x",
    "max_of_two": "def max_of_two (a b : Int) : Int :=\n  if a ≥ b then a else b",
    "min_of_two": "def min_of_two (a b : Int) : Int :=\n  if a ≤ b then a else b",
    "clamp": "def clamp (x lo hi : Int) : Int :=\n  if x < lo then lo\n  else if x > hi then hi\n  else x",
    "factorial": "def factorial : Nat → Nat\n  | 0 => 1\n  | n + 1 => (n + 1) * factorial n",
    "fibonacci": "def fibonacci : Nat → Nat\n  | 0 => 0\n  | 1 => 1\n  | n + 2 => fibonacci (n + 1) + fibonacci n",
    "sign": "def sign (x : Int) : Int :=\n  if x > 0 then 1\n  else if x < 0 then -1\n  else 0",
}

C_TESTS = {
    "abs_val": '#include <assert.h>\nint abs_val(int x) { if (x < 0) return -x; return x; }\nint main() { assert(abs_val(5)==5); assert(abs_val(-5)==5); assert(abs_val(0)==0); return 0; }',
    "max_of_two": '#include <assert.h>\nint max_of_two(int a, int b) { if (a >= b) return a; return b; }\nint main() { assert(max_of_two(5,3)==5); assert(max_of_two(3,5)==5); assert(max_of_two(4,4)==4); return 0; }',
    "min_of_two": '#include <assert.h>\nint min_of_two(int a, int b) { if (a <= b) return a; return b; }\nint main() { assert(min_of_two(5,3)==3); assert(min_of_two(3,5)==3); assert(min_of_two(4,4)==4); return 0; }',
    "clamp": '#include <assert.h>\nint clamp(int x, int lo, int hi) { if (x < lo) return lo; if (x > hi) return hi; return x; }\nint main() { assert(clamp(5,0,10)==5); assert(clamp(-5,0,10)==0); assert(clamp(15,0,10)==10); return 0; }',
    "factorial": '#include <assert.h>\nunsigned int factorial(unsigned int n) { unsigned int r=1; for(unsigned int i=2;i<=n;i++) r*=i; return r; }\nint main() { assert(factorial(0)==1); assert(factorial(5)==120); assert(factorial(1)==1); return 0; }',
    "fibonacci": '#include <assert.h>\nunsigned int fibonacci(unsigned int n) { if(n<=1) return n; unsigned int a=0,b=1; for(unsigned int i=2;i<=n;i++){unsigned int t=a+b;a=b;b=t;} return b; }\nint main() { assert(fibonacci(0)==0); assert(fibonacci(1)==1); assert(fibonacci(10)==55); return 0; }',
    "sign": '#include <assert.h>\nint sign(int x) { if(x>0) return 1; if(x<0) return -1; return 0; }\nint main() { assert(sign(10)==1); assert(sign(-10)==-1); assert(sign(0)==0); return 0; }',
}

PY_TESTS = {
    "abs_val": "def abs_val(x):\n    if x < 0: return -x\n    return x\nassert abs_val(5)==5\nassert abs_val(-5)==5\nassert abs_val(0)==0",
    "max_of_two": "def max_of_two(a,b):\n    if a>=b: return a\n    return b\nassert max_of_two(5,3)==5\nassert max_of_two(3,5)==5",
    "min_of_two": "def min_of_two(a,b):\n    if a<=b: return a\n    return b\nassert min_of_two(5,3)==3\nassert min_of_two(3,5)==3",
    "clamp": "def clamp(x,lo,hi):\n    if x<lo: return lo\n    if x>hi: return hi\n    return x\nassert clamp(5,0,10)==5\nassert clamp(-5,0,10)==0\nassert clamp(15,0,10)==10",
    "factorial": "def factorial(n):\n    r=1\n    for i in range(2,n+1): r*=i\n    return r\nassert factorial(0)==1\nassert factorial(5)==120",
    "fibonacci": "def fibonacci(n):\n    if n<=1: return n\n    a,b=0,1\n    for _ in range(2,n+1): a,b=b,a+b\n    return b\nassert fibonacci(0)==0\nassert fibonacci(1)==1\nassert fibonacci(10)==55",
    "sign": "def sign(x):\n    if x>0: return 1\n    if x<0: return -1\n    return 0\nassert sign(10)==1\nassert sign(-10)==-1\nassert sign(0)==0",
}

LEAN_TESTS = {
    "abs_val": "#eval abs_val 5  -- 5\n#eval abs_val (-5)  -- 5\n#eval abs_val 0  -- 0",
    "max_of_two": "#eval max_of_two 5 3  -- 5\n#eval max_of_two 3 5  -- 5",
    "min_of_two": "#eval min_of_two 5 3  -- 3\n#eval min_of_two 3 5  -- 3",
    "clamp": "#eval clamp 5 0 10  -- 5\n#eval clamp (-5) 0 10  -- 0\n#eval clamp 15 0 10  -- 10",
    "factorial": "#eval factorial 0  -- 1\n#eval factorial 5  -- 120",
    "fibonacci": "#eval fibonacci 0  -- 0\n#eval fibonacci 1  -- 1\n#eval fibonacci 10  -- 55",
    "sign": "#eval sign 10  -- 1\n#eval sign (-10)  -- -1\n#eval sign 0  -- 0",
}

THEOREMS = {
    "abs_val": [
        {"name": "abs_val_nonneg", "statement": "theorem abs_val_nonneg (x : Int) : 0 ≤ abs_val x", "proof": "by unfold abs_val; split <;> omega", "proof_incomplete": False},
        {"name": "abs_val_self_pos", "statement": "theorem abs_val_self_pos (x : Int) : x ≥ 0 → abs_val x = x", "proof": "by simp [abs_val]; intro h; split_ifs <;> omega", "proof_incomplete": False},
        {"name": "abs_val_neg", "statement": "theorem abs_val_neg (x : Int) : x < 0 → abs_val x = -x", "proof": "by simp [abs_val]; intro h; split_ifs <;> omega", "proof_incomplete": False},
    ],
    "max_of_two": [
        {"name": "max_of_two_ge_left", "statement": "theorem max_of_two_ge_left (a b : Int) : max_of_two a b ≥ a", "proof": "by unfold max_of_two; split <;> omega", "proof_incomplete": False},
        {"name": "max_of_two_ge_right", "statement": "theorem max_of_two_ge_right (a b : Int) : max_of_two a b ≥ b", "proof": "by unfold max_of_two; split <;> omega", "proof_incomplete": False},
        {"name": "max_of_two_comm", "statement": "theorem max_of_two_comm (a b : Int) : max_of_two a b = max_of_two b a", "proof": "by unfold max_of_two; split <;> omega", "proof_incomplete": False},
    ],
    "min_of_two": [
        {"name": "min_of_two_le_left", "statement": "theorem min_of_two_le_left (a b : Int) : min_of_two a b ≤ a", "proof": "by unfold min_of_two; split <;> omega", "proof_incomplete": False},
        {"name": "min_of_two_le_right", "statement": "theorem min_of_two_le_right (a b : Int) : min_of_two a b ≤ b", "proof": "by unfold min_of_two; split <;> omega", "proof_incomplete": False},
        {"name": "min_of_two_comm", "statement": "theorem min_of_two_comm (a b : Int) : min_of_two a b = min_of_two b a", "proof": "by unfold min_of_two; split <;> omega", "proof_incomplete": False},
    ],
    "clamp": [
        {"name": "clamp_bounds", "statement": "theorem clamp_bounds (x lo hi : Int) : lo ≤ hi → lo ≤ clamp x lo hi ∧ clamp x lo hi ≤ hi", "proof": "by intro h; unfold clamp; split · constructor <;> omega · split · constructor <;> omega · constructor <;> omega", "proof_incomplete": False},
        {"name": "clamp_idempotent", "statement": "theorem clamp_idempotent (x lo hi : Int) : lo ≤ hi → clamp (clamp x lo hi) lo hi = clamp x lo hi", "proof": "by intro h; simp only [clamp]; split <;> split <;> simp_all <;> omega", "proof_incomplete": False},
        {"name": "clamp_fixed_point", "statement": "theorem clamp_fixed_point (x lo hi : Int) : lo ≤ x → x ≤ hi → clamp x lo hi = x", "proof": "by unfold clamp; split <;> split <;> omega", "proof_incomplete": False},
    ],
    "factorial": [
        {"name": "factorial_zero", "statement": "theorem factorial_zero : factorial 0 = 1", "proof": "by simp [factorial]", "proof_incomplete": False},
        {"name": "factorial_succ", "statement": "theorem factorial_succ (n : Nat) : factorial (n + 1) = (n + 1) * factorial n", "proof": "by simp [factorial]", "proof_incomplete": False},
        {"name": "factorial_pos", "statement": "theorem factorial_pos (n : Nat) : factorial n > 0", "proof": "by sorry", "proof_incomplete": True},
    ],
    "fibonacci": [
        {"name": "fibonacci_recurrence", "statement": "theorem fibonacci_recurrence (n : Nat) : fibonacci (n + 2) = fibonacci (n + 1) + fibonacci n", "proof": "by simp [fibonacci]", "proof_incomplete": False},
        {"name": "fibonacci_zero", "statement": "theorem fibonacci_zero : fibonacci 0 = 0", "proof": "by simp [fibonacci]", "proof_incomplete": False},
        {"name": "fibonacci_one", "statement": "theorem fibonacci_one : fibonacci 1 = 1", "proof": "by simp [fibonacci]", "proof_incomplete": False},
    ],
    "sign": [
        {"name": "sign_pos", "statement": "theorem sign_pos (x : Int) : x > 0 → sign x = 1", "proof": "by simp [sign]; intro h; split_ifs <;> omega", "proof_incomplete": False},
        {"name": "sign_neg", "statement": "theorem sign_neg (x : Int) : x < 0 → sign x = -1", "proof": "by simp [sign]; intro h; split_ifs <;> omega", "proof_incomplete": False},
        {"name": "sign_trichotomy", "statement": "theorem sign_trichotomy (x : Int) : sign x = 1 ∨ sign x = -1 ∨ sign x = 0", "proof": "by unfold sign; split · left; rfl · split · right; left; rfl · right; right; rfl", "proof_incomplete": False},
    ],
}

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch01_arithmetic.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    for lang in ["C", "Python"]:
        for name in FUNCTIONS:
            record = {
                "language": lang,
                "source": C_SOURCES[name] if lang == "C" else PY_SOURCES[name],
                "lean_translation": LEAN[name],
                "tests": C_TESTS[name] if lang == "C" else PY_TESTS[name],
                "lean_tests": LEAN_TESTS[name],
                "theorems": THEOREMS[name],
                "deps_fully_translated": [],
                "axiomatized_deps": [],
                "skip_reason": None,
            }
            f.write(json.dumps(record) + "\n")

print(f"Generated {output_path} with {len(FUNCTIONS) * 2} records")
