"""Generate JSONL for batch06_bits: is_power_of_two, count_set_bits, parity, reverse_bits, next_power_of_two, lowest_set_bit, clear_lowest_set_bit."""
import json, os

FUNCTIONS = ["is_power_of_two", "count_set_bits", "parity", "next_power_of_two", "lowest_set_bit", "clear_lowest_set_bit"]
# reverse_bits omitted: 32-bit fixed-width reversal doesn't translate cleanly to Nat

C_SOURCES = {
    "is_power_of_two": "int is_power_of_two(unsigned int n) {\n    return n != 0 && (n & (n - 1)) == 0;\n}",
    "count_set_bits": "unsigned int count_set_bits(unsigned int n) {\n    unsigned int count = 0;\n    while (n) {\n        count += n & 1;\n        n >>= 1;\n    }\n    return count;\n}",
    "parity": "unsigned int parity(unsigned int n) {\n    unsigned int p = 0;\n    while (n) {\n        p ^= (n & 1);\n        n >>= 1;\n    }\n    return p;\n}",
    "next_power_of_two": "unsigned int next_power_of_two(unsigned int n) {\n    if (n == 0) return 1;\n    n--;\n    n |= n >> 1;\n    n |= n >> 2;\n    n |= n >> 4;\n    n |= n >> 8;\n    n |= n >> 16;\n    return n + 1;\n}",
    "lowest_set_bit": "unsigned int lowest_set_bit(unsigned int n) {\n    return n & (~n + 1);\n}",
    "clear_lowest_set_bit": "unsigned int clear_lowest_set_bit(unsigned int n) {\n    return n & (n - 1);\n}",
}

PY_SOURCES = {
    "is_power_of_two": "def is_power_of_two(n: int) -> bool:\n    return n != 0 and (n & (n - 1)) == 0",
    "count_set_bits": "def count_set_bits(n: int) -> int:\n    count = 0\n    while n:\n        count += n & 1\n        n >>= 1\n    return count",
    "parity": "def parity(n: int) -> int:\n    p = 0\n    while n:\n        p ^= (n & 1)\n        n >>= 1\n    return p",
    "next_power_of_two": "def next_power_of_two(n: int) -> int:\n    if n == 0:\n        return 1\n    n -= 1\n    n |= n >> 1\n    n |= n >> 2\n    n |= n >> 4\n    n |= n >> 8\n    n |= n >> 16\n    return n + 1",
    "lowest_set_bit": "def lowest_set_bit(n: int) -> int:\n    return n & (~n + 1)",
    "clear_lowest_set_bit": "def clear_lowest_set_bit(n: int) -> int:\n    return n & (n - 1)",
}

LEAN = {
    "is_power_of_two": "def is_power_of_two (n : Nat) : Bool :=\n  n != 0 && (n &&& (n - 1)) == 0",
    "count_set_bits": "def count_set_bits (n : Nat) : Nat :=\n  if h : n = 0 then 0\n  else (n % 2) + count_set_bits (n / 2)\ntermination_by n\ndecreasing_by exact Nat.div_lt_self (Nat.pos_of_ne_zero h) (by omega)",
    "parity": "def parity (n : Nat) : Nat :=\n  if h : n = 0 then 0\n  else (n % 2 + parity (n / 2)) % 2\ntermination_by n\ndecreasing_by exact Nat.div_lt_self (Nat.pos_of_ne_zero h) (by omega)",
    "next_power_of_two": "def next_power_of_two (n : Nat) : Nat :=\n  if n = 0 then 1\n  else\n    let rec go (p : Nat) : Nat :=\n      if p >= n then p else go (p * 2)\n    go 1",
    "lowest_set_bit": "def lowest_set_bit (n : Nat) : Nat :=\n  if h : n = 0 then 0\n  else if n % 2 = 1 then 1\n  else 2 * lowest_set_bit (n / 2)\ntermination_by n\ndecreasing_by exact Nat.div_lt_self (Nat.pos_of_ne_zero h) (by omega)",
    "clear_lowest_set_bit": "def clear_lowest_set_bit (n : Nat) : Nat :=\n  n - lowest_set_bit n",
}

C_TESTS = {
    "is_power_of_two": '#include <assert.h>\nint is_power_of_two(unsigned int n) { return n!=0 && (n&(n-1))==0; }\nint main() { assert(is_power_of_two(1)); assert(is_power_of_two(16)); assert(!is_power_of_two(0)); assert(!is_power_of_two(6)); return 0; }',
    "count_set_bits": '#include <assert.h>\nunsigned int count_set_bits(unsigned int n) { unsigned int c=0; while(n){c+=n&1;n>>=1;} return c; }\nint main() { assert(count_set_bits(0)==0); assert(count_set_bits(7)==3); assert(count_set_bits(255)==8); assert(count_set_bits(1)==1); return 0; }',
    "parity": '#include <assert.h>\nunsigned int parity(unsigned int n) { unsigned int p=0; while(n){p^=(n&1);n>>=1;} return p; }\nint main() { assert(parity(0)==0); assert(parity(7)==1); assert(parity(3)==0); assert(parity(1)==1); return 0; }',
    "next_power_of_two": '#include <assert.h>\nunsigned int next_power_of_two(unsigned int n) { if(n==0)return 1; n--;n|=n>>1;n|=n>>2;n|=n>>4;n|=n>>8;n|=n>>16;return n+1; }\nint main() { assert(next_power_of_two(0)==1); assert(next_power_of_two(5)==8); assert(next_power_of_two(8)==8); assert(next_power_of_two(1)==1); return 0; }',
    "lowest_set_bit": '#include <assert.h>\nunsigned int lowest_set_bit(unsigned int n) { return n&(~n+1); }\nint main() { assert(lowest_set_bit(12)==4); assert(lowest_set_bit(1)==1); assert(lowest_set_bit(0)==0); assert(lowest_set_bit(6)==2); return 0; }',
    "clear_lowest_set_bit": '#include <assert.h>\nunsigned int clear_lowest_set_bit(unsigned int n) { return n&(n-1); }\nint main() { assert(clear_lowest_set_bit(12)==8); assert(clear_lowest_set_bit(1)==0); assert(clear_lowest_set_bit(0)==0); assert(clear_lowest_set_bit(7)==6); return 0; }',
}

PY_TESTS = {
    "is_power_of_two": "def is_power_of_two(n):\n    return n!=0 and (n&(n-1))==0\nassert is_power_of_two(1)\nassert is_power_of_two(16)\nassert not is_power_of_two(0)\nassert not is_power_of_two(6)",
    "count_set_bits": "def count_set_bits(n):\n    c=0\n    while n: c+=n&1; n>>=1\n    return c\nassert count_set_bits(0)==0\nassert count_set_bits(7)==3\nassert count_set_bits(255)==8",
    "parity": "def parity(n):\n    p=0\n    while n: p^=(n&1); n>>=1\n    return p\nassert parity(0)==0\nassert parity(7)==1\nassert parity(3)==0",
    "next_power_of_two": "def next_power_of_two(n):\n    if n==0: return 1\n    n-=1; n|=n>>1; n|=n>>2; n|=n>>4; n|=n>>8; n|=n>>16\n    return n+1\nassert next_power_of_two(0)==1\nassert next_power_of_two(5)==8\nassert next_power_of_two(8)==8",
    "lowest_set_bit": "def lowest_set_bit(n):\n    return n&(~n+1)\nassert lowest_set_bit(12)==4\nassert lowest_set_bit(1)==1\nassert lowest_set_bit(0)==0",
    "clear_lowest_set_bit": "def clear_lowest_set_bit(n):\n    return n&(n-1)\nassert clear_lowest_set_bit(12)==8\nassert clear_lowest_set_bit(1)==0\nassert clear_lowest_set_bit(0)==0",
}

LEAN_TESTS = {
    "is_power_of_two": "#eval is_power_of_two 1  -- true\n#eval is_power_of_two 16  -- true\n#eval is_power_of_two 0  -- false\n#eval is_power_of_two 6  -- false",
    "count_set_bits": "#eval count_set_bits 0  -- 0\n#eval count_set_bits 7  -- 3\n#eval count_set_bits 255  -- 8",
    "parity": "#eval parity 0  -- 0\n#eval parity 7  -- 1\n#eval parity 3  -- 0",
    "next_power_of_two": "#eval next_power_of_two 0  -- 1\n#eval next_power_of_two 5  -- 8\n#eval next_power_of_two 8  -- 8",
    "lowest_set_bit": "#eval lowest_set_bit 12  -- 4\n#eval lowest_set_bit 1  -- 1\n#eval lowest_set_bit 0  -- 0",
    "clear_lowest_set_bit": "#eval clear_lowest_set_bit 12  -- 8\n#eval clear_lowest_set_bit 1  -- 0\n#eval clear_lowest_set_bit 0  -- 0",
}

THEOREMS = {
    "is_power_of_two": [
        {"name": "is_power_of_two_one", "statement": "theorem is_power_of_two_one : is_power_of_two 1 = true", "proof": "by native_decide", "proof_incomplete": False},
        {"name": "is_power_of_two_zero", "statement": "theorem is_power_of_two_zero : is_power_of_two 0 = false", "proof": "by native_decide", "proof_incomplete": False},
        {"name": "is_power_of_two_iff", "statement": "theorem is_power_of_two_iff (n : Nat) : is_power_of_two n = true ↔ ∃ k, n = 2 ^ k", "proof": "by sorry", "proof_incomplete": True},
    ],
    "count_set_bits": [
        {"name": "count_set_bits_zero", "statement": "theorem count_set_bits_zero : count_set_bits 0 = 0", "proof": "by simp [count_set_bits]", "proof_incomplete": False},
        {"name": "count_set_bits_le_log", "statement": "theorem count_set_bits_le (n : Nat) : count_set_bits n ≤ n", "proof": "by sorry", "proof_incomplete": True},
        {"name": "count_set_bits_power_of_two", "statement": "theorem count_set_bits_power_of_two (k : Nat) : count_set_bits (2 ^ k) = 1", "proof": "by sorry", "proof_incomplete": True},
    ],
    "parity": [
        {"name": "parity_zero", "statement": "theorem parity_zero : parity 0 = 0", "proof": "by simp [parity]", "proof_incomplete": False},
        {"name": "parity_mod2_count", "statement": "theorem parity_mod2_count (n : Nat) : parity n = count_set_bits n % 2", "proof": "by sorry", "proof_incomplete": True},
        {"name": "parity_range", "statement": "theorem parity_range (n : Nat) : parity n = 0 ∨ parity n = 1", "proof": "by sorry", "proof_incomplete": True},
    ],
    "next_power_of_two": [
        {"name": "next_power_of_two_ge", "statement": "theorem next_power_of_two_ge (n : Nat) : next_power_of_two n ≥ n", "proof": "by sorry", "proof_incomplete": True},
        {"name": "next_power_of_two_is_pow2", "statement": "theorem next_power_of_two_is_pow2 (n : Nat) : is_power_of_two (next_power_of_two n) = true", "proof": "by sorry", "proof_incomplete": True},
        {"name": "next_power_of_two_zero", "statement": "theorem next_power_of_two_zero : next_power_of_two 0 = 1", "proof": "by simp [next_power_of_two]", "proof_incomplete": False},
    ],
    "lowest_set_bit": [
        {"name": "lowest_set_bit_zero", "statement": "theorem lowest_set_bit_zero : lowest_set_bit 0 = 0", "proof": "by simp [lowest_set_bit]", "proof_incomplete": False},
        {"name": "lowest_set_bit_dvd", "statement": "theorem lowest_set_bit_dvd (n : Nat) : n > 0 → lowest_set_bit n ∣ n", "proof": "by sorry", "proof_incomplete": True},
        {"name": "lowest_set_bit_is_pow2", "statement": "theorem lowest_set_bit_is_pow2 (n : Nat) : n > 0 → is_power_of_two (lowest_set_bit n) = true", "proof": "by sorry", "proof_incomplete": True},
    ],
    "clear_lowest_set_bit": [
        {"name": "clear_lowest_set_bit_zero", "statement": "theorem clear_lowest_set_bit_zero : clear_lowest_set_bit 0 = 0", "proof": "by simp [clear_lowest_set_bit, lowest_set_bit]", "proof_incomplete": False},
        {"name": "clear_lowest_set_bit_le", "statement": "theorem clear_lowest_set_bit_le (n : Nat) : clear_lowest_set_bit n ≤ n", "proof": "by sorry", "proof_incomplete": True},
        {"name": "clear_lowest_set_bit_count", "statement": "theorem clear_lowest_set_bit_count (n : Nat) : n > 0 → count_set_bits (clear_lowest_set_bit n) = count_set_bits n - 1", "proof": "by sorry", "proof_incomplete": True},
    ],
}

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch06_bits.jsonl"
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
