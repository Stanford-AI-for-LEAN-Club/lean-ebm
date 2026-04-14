"""Generate JSONL for batch08_math2: integer_sqrt, is_perfect_square, binomial, is_even, is_odd, triangular_number, collatz_steps, digital_root."""
import json, os

FUNCTIONS = ["integer_sqrt", "is_perfect_square", "binomial", "is_even", "is_odd", "triangular_number", "collatz_steps", "digital_root"]

C_SOURCES = {
    "integer_sqrt": "unsigned int integer_sqrt(unsigned int n) {\n    if (n == 0) return 0;\n    unsigned int x = n;\n    unsigned int y = (x + 1) / 2;\n    while (y < x) {\n        x = y;\n        y = (x + n / x) / 2;\n    }\n    return x;\n}",
    "is_perfect_square": "int is_perfect_square(unsigned int n) {\n    unsigned int s = integer_sqrt(n);\n    return s * s == n;\n}",
    "binomial": "unsigned int binomial(unsigned int n, unsigned int k) {\n    if (k > n) return 0;\n    if (k == 0 || k == n) return 1;\n    if (k > n - k) k = n - k;\n    unsigned int result = 1;\n    for (unsigned int i = 0; i < k; i++) {\n        result = result * (n - i) / (i + 1);\n    }\n    return result;\n}",
    "is_even": "int is_even(int n) {\n    return n % 2 == 0;\n}",
    "is_odd": "int is_odd(int n) {\n    return n % 2 != 0;\n}",
    "triangular_number": "unsigned int triangular_number(unsigned int n) {\n    return n * (n + 1) / 2;\n}",
    "collatz_steps": "int collatz_steps(unsigned int n) {\n    int steps = 0;\n    while (n != 1 && n != 0) {\n        if (n % 2 == 0) n = n / 2;\n        else n = 3 * n + 1;\n        steps++;\n    }\n    return steps;\n}",
    "digital_root": "unsigned int digital_root(unsigned int n) {\n    if (n == 0) return 0;\n    return 1 + (n - 1) % 9;\n}",
}

PY_SOURCES = {
    "integer_sqrt": "def integer_sqrt(n: int) -> int:\n    if n == 0:\n        return 0\n    x = n\n    y = (x + 1) // 2\n    while y < x:\n        x = y\n        y = (x + n // x) // 2\n    return x",
    "is_perfect_square": "def is_perfect_square(n: int) -> bool:\n    s = integer_sqrt(n)\n    return s * s == n",
    "binomial": "def binomial(n: int, k: int) -> int:\n    if k > n:\n        return 0\n    if k == 0 or k == n:\n        return 1\n    if k > n - k:\n        k = n - k\n    result = 1\n    for i in range(k):\n        result = result * (n - i) // (i + 1)\n    return result",
    "is_even": "def is_even(n: int) -> bool:\n    return n % 2 == 0",
    "is_odd": "def is_odd(n: int) -> bool:\n    return n % 2 != 0",
    "triangular_number": "def triangular_number(n: int) -> int:\n    return n * (n + 1) // 2",
    "collatz_steps": "def collatz_steps(n: int) -> int:\n    steps = 0\n    while n != 1 and n != 0:\n        if n % 2 == 0:\n            n = n // 2\n        else:\n            n = 3 * n + 1\n        steps += 1\n    return steps",
    "digital_root": "def digital_root(n: int) -> int:\n    if n == 0:\n        return 0\n    return 1 + (n - 1) % 9",
}

LEAN = {
    "integer_sqrt": "def integer_sqrt (n : Nat) : Nat :=\n  if n = 0 then 0\n  else Id.run do\n    let mut x := n\n    let mut y := (x + 1) / 2\n    while y < x do\n      x := y\n      y := (x + n / x) / 2\n    return x",
    "is_perfect_square": "def is_perfect_square (n : Nat) : Bool :=\n  let s := integer_sqrt n\n  s * s == n",
    "binomial": "def binomial (n k : Nat) : Nat :=\n  if k > n then 0\n  else Id.run do\n    let k := if k > n - k then n - k else k\n    let mut result := 1\n    for i in [:k] do\n      result := result * (n - i) / (i + 1)\n    return result",
    "is_even": "def is_even (n : Nat) : Bool :=\n  n % 2 == 0",
    "is_odd": "def is_odd (n : Nat) : Bool :=\n  n % 2 != 0",
    "triangular_number": "def triangular_number (n : Nat) : Nat :=\n  n * (n + 1) / 2",
    "collatz_steps": "partial def collatz_steps (n : Nat) : Nat :=\n  if n ≤ 1 then 0\n  else if n % 2 = 0 then 1 + collatz_steps (n / 2)\n  else 1 + collatz_steps (3 * n + 1)",
    "digital_root": "def digital_root (n : Nat) : Nat :=\n  if n = 0 then 0 else 1 + (n - 1) % 9",
}

C_TESTS = {
    "integer_sqrt": '#include <assert.h>\nunsigned int integer_sqrt(unsigned int n) { if(n==0) return 0; unsigned int x=n, y=(x+1)/2; while(y<x){x=y;y=(x+n/x)/2;} return x; }\nint main() { assert(integer_sqrt(0)==0); assert(integer_sqrt(1)==1); assert(integer_sqrt(4)==2); assert(integer_sqrt(10)==3); assert(integer_sqrt(100)==10); return 0; }',
    "is_perfect_square": '#include <assert.h>\nunsigned int integer_sqrt(unsigned int n) { if(n==0) return 0; unsigned int x=n, y=(x+1)/2; while(y<x){x=y;y=(x+n/x)/2;} return x; }\nint is_perfect_square(unsigned int n) { unsigned int s=integer_sqrt(n); return s*s==n; }\nint main() { assert(is_perfect_square(0)); assert(is_perfect_square(1)); assert(is_perfect_square(16)); assert(!is_perfect_square(10)); return 0; }',
    "binomial": '#include <assert.h>\nunsigned int binomial(unsigned int n, unsigned int k) { if(k>n) return 0; if(k==0||k==n) return 1; if(k>n-k) k=n-k; unsigned int r=1; for(unsigned int i=0;i<k;i++) r=r*(n-i)/(i+1); return r; }\nint main() { assert(binomial(5,2)==10); assert(binomial(10,0)==1); assert(binomial(10,10)==1); assert(binomial(3,5)==0); return 0; }',
    "is_even": '#include <assert.h>\nint is_even(int n) { return n%2==0; }\nint main() { assert(is_even(0)); assert(is_even(4)); assert(!is_even(3)); assert(is_even(-2)); return 0; }',
    "is_odd": '#include <assert.h>\nint is_odd(int n) { return n%2!=0; }\nint main() { assert(!is_odd(0)); assert(!is_odd(4)); assert(is_odd(3)); assert(is_odd(-1)); return 0; }',
    "triangular_number": '#include <assert.h>\nunsigned int triangular_number(unsigned int n) { return n*(n+1)/2; }\nint main() { assert(triangular_number(0)==0); assert(triangular_number(1)==1); assert(triangular_number(5)==15); assert(triangular_number(10)==55); return 0; }',
    "collatz_steps": '#include <assert.h>\nint collatz_steps(unsigned int n) { int s=0; while(n!=1&&n!=0){if(n%2==0) n=n/2; else n=3*n+1; s++;} return s; }\nint main() { assert(collatz_steps(1)==0); assert(collatz_steps(2)==1); assert(collatz_steps(6)==8); return 0; }',
    "digital_root": '#include <assert.h>\nunsigned int digital_root(unsigned int n) { if(n==0) return 0; return 1+(n-1)%9; }\nint main() { assert(digital_root(0)==0); assert(digital_root(1)==1); assert(digital_root(9)==9); assert(digital_root(10)==1); assert(digital_root(493)==7); return 0; }',
}

PY_TESTS = {
    "integer_sqrt": "def integer_sqrt(n):\n    if n==0: return 0\n    x=n; y=(x+1)//2\n    while y<x: x=y; y=(x+n//x)//2\n    return x\nassert integer_sqrt(0)==0\nassert integer_sqrt(4)==2\nassert integer_sqrt(10)==3\nassert integer_sqrt(100)==10",
    "is_perfect_square": "def integer_sqrt(n):\n    if n==0: return 0\n    x=n; y=(x+1)//2\n    while y<x: x=y; y=(x+n//x)//2\n    return x\ndef is_perfect_square(n):\n    s=integer_sqrt(n); return s*s==n\nassert is_perfect_square(0)\nassert is_perfect_square(16)\nassert not is_perfect_square(10)",
    "binomial": "def binomial(n, k):\n    if k>n: return 0\n    if k==0 or k==n: return 1\n    if k>n-k: k=n-k\n    r=1\n    for i in range(k): r=r*(n-i)//(i+1)\n    return r\nassert binomial(5,2)==10\nassert binomial(10,0)==1\nassert binomial(3,5)==0",
    "is_even": "def is_even(n): return n%2==0\nassert is_even(0)\nassert is_even(4)\nassert not is_even(3)",
    "is_odd": "def is_odd(n): return n%2!=0\nassert not is_odd(0)\nassert not is_odd(4)\nassert is_odd(3)",
    "triangular_number": "def triangular_number(n): return n*(n+1)//2\nassert triangular_number(0)==0\nassert triangular_number(5)==15\nassert triangular_number(10)==55",
    "collatz_steps": "def collatz_steps(n):\n    s=0\n    while n!=1 and n!=0:\n        if n%2==0: n=n//2\n        else: n=3*n+1\n        s+=1\n    return s\nassert collatz_steps(1)==0\nassert collatz_steps(2)==1\nassert collatz_steps(6)==8",
    "digital_root": "def digital_root(n):\n    if n==0: return 0\n    return 1+(n-1)%9\nassert digital_root(0)==0\nassert digital_root(9)==9\nassert digital_root(493)==7",
}

LEAN_TESTS = {
    "integer_sqrt": "#eval integer_sqrt 0  -- 0\n#eval integer_sqrt 4  -- 2\n#eval integer_sqrt 10  -- 3\n#eval integer_sqrt 100  -- 10",
    "is_perfect_square": "#eval is_perfect_square 0  -- true\n#eval is_perfect_square 16  -- true\n#eval is_perfect_square 10  -- false",
    "binomial": "#eval binomial 5 2  -- 10\n#eval binomial 10 0  -- 1\n#eval binomial 3 5  -- 0",
    "is_even": "#eval is_even 0  -- true\n#eval is_even 4  -- true\n#eval is_even 3  -- false",
    "is_odd": "#eval is_odd 0  -- false\n#eval is_odd 3  -- true",
    "triangular_number": "#eval triangular_number 0  -- 0\n#eval triangular_number 5  -- 15\n#eval triangular_number 10  -- 55",
    "collatz_steps": "#eval collatz_steps 1  -- 0\n#eval collatz_steps 2  -- 1\n#eval collatz_steps 6  -- 8",
    "digital_root": "#eval digital_root 0  -- 0\n#eval digital_root 9  -- 9\n#eval digital_root 493  -- 7",
}

THEOREMS = {
    "integer_sqrt": [
        {"name": "integer_sqrt_zero", "statement": "theorem integer_sqrt_zero : integer_sqrt 0 = 0", "proof": "by sorry", "proof_incomplete": True},
        {"name": "integer_sqrt_sq_le", "statement": "theorem integer_sqrt_sq_le (n : Nat) : integer_sqrt n * integer_sqrt n ≤ n", "proof": "by sorry", "proof_incomplete": True},
        {"name": "integer_sqrt_succ_sq_gt", "statement": "theorem integer_sqrt_succ_sq_gt (n : Nat) : (integer_sqrt n + 1) * (integer_sqrt n + 1) > n", "proof": "by sorry", "proof_incomplete": True},
    ],
    "is_perfect_square": [
        {"name": "is_perfect_square_iff", "statement": "theorem is_perfect_square_iff (n : Nat) : is_perfect_square n = true ↔ ∃ k, n = k * k", "proof": "by sorry", "proof_incomplete": True},
        {"name": "is_perfect_square_zero", "statement": "theorem is_perfect_square_zero : is_perfect_square 0 = true", "proof": "by native_decide", "proof_incomplete": False},
        {"name": "is_perfect_square_sq", "statement": "theorem is_perfect_square_sq (k : Nat) : is_perfect_square (k * k) = true", "proof": "by sorry", "proof_incomplete": True},
    ],
    "binomial": [
        {"name": "binomial_zero_right", "statement": "theorem binomial_zero_right (n : Nat) : binomial n 0 = 1", "proof": "by sorry", "proof_incomplete": True},
        {"name": "binomial_self", "statement": "theorem binomial_self (n : Nat) : binomial n n = 1", "proof": "by sorry", "proof_incomplete": True},
        {"name": "binomial_symmetry", "statement": "theorem binomial_symmetry (n k : Nat) : k ≤ n → binomial n k = binomial n (n - k)", "proof": "by sorry", "proof_incomplete": True},
    ],
    "is_even": [
        {"name": "is_even_zero", "statement": "theorem is_even_zero : is_even 0 = true", "proof": "by simp [is_even]", "proof_incomplete": False},
        {"name": "is_even_double", "statement": "theorem is_even_double (n : Nat) : is_even (2 * n) = true", "proof": "by sorry", "proof_incomplete": True},
        {"name": "is_even_not_odd", "statement": "theorem is_even_not_odd (n : Nat) : is_even n = true ↔ is_odd n = false", "proof": "by sorry", "proof_incomplete": True},
    ],
    "is_odd": [
        {"name": "is_odd_one", "statement": "theorem is_odd_one : is_odd 1 = true", "proof": "by simp [is_odd]", "proof_incomplete": False},
        {"name": "is_odd_double_plus_one", "statement": "theorem is_odd_double_plus_one (n : Nat) : is_odd (2 * n + 1) = true", "proof": "by sorry", "proof_incomplete": True},
        {"name": "is_odd_not_even", "statement": "theorem is_odd_not_even (n : Nat) : is_odd n = true ↔ is_even n = false", "proof": "by sorry", "proof_incomplete": True},
    ],
    "triangular_number": [
        {"name": "triangular_zero", "statement": "theorem triangular_zero : triangular_number 0 = 0", "proof": "by simp [triangular_number]", "proof_incomplete": False},
        {"name": "triangular_formula", "statement": "theorem triangular_formula (n : Nat) : 2 * triangular_number n = n * (n + 1)", "proof": "by sorry", "proof_incomplete": True},
        {"name": "triangular_succ", "statement": "theorem triangular_succ (n : Nat) : triangular_number (n + 1) = triangular_number n + (n + 1)", "proof": "by sorry", "proof_incomplete": True},
    ],
    "collatz_steps": [
        {"name": "collatz_steps_one", "statement": "theorem collatz_steps_one : collatz_steps 1 = 0", "proof": "by simp [collatz_steps]", "proof_incomplete": False},
        {"name": "collatz_steps_nonneg", "statement": "theorem collatz_steps_nonneg (n : Nat) : collatz_steps n ≥ 0", "proof": "by omega", "proof_incomplete": False},
        {"name": "collatz_steps_even", "statement": "theorem collatz_steps_even (n : Nat) : n > 1 → n % 2 = 0 → collatz_steps n = 1 + collatz_steps (n / 2)", "proof": "by sorry", "proof_incomplete": True},
    ],
    "digital_root": [
        {"name": "digital_root_zero", "statement": "theorem digital_root_zero : digital_root 0 = 0", "proof": "by simp [digital_root]", "proof_incomplete": False},
        {"name": "digital_root_range", "statement": "theorem digital_root_range (n : Nat) : n > 0 → digital_root n ≥ 1 ∧ digital_root n ≤ 9", "proof": "by sorry", "proof_incomplete": True},
        {"name": "digital_root_mod_nine", "statement": "theorem digital_root_mod_nine (n : Nat) : n > 0 → digital_root n % 9 = n % 9", "proof": "by sorry", "proof_incomplete": True},
    ],
}

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch08_math2.jsonl"
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
                "deps_fully_translated": ["integer_sqrt"] if name == "is_perfect_square" else [],
                "axiomatized_deps": [],
                "skip_reason": None,
            }
            f.write(json.dumps(record) + "\n")

print(f"Generated {output_path} with {len(FUNCTIONS) * 2} records")
