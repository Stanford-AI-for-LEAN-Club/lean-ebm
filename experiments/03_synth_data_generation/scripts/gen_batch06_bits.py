import json
from pathlib import Path
from textwrap import dedent


def block(text: str) -> str:
    return dedent(text).strip()


def get_c_source(name: str) -> str:
    sources = {
        "is_power_of_two": block(
            """
            int is_power_of_two(unsigned int n) {
                return n != 0 && (n & (n - 1)) == 0;
            }
            """
        ),
        "count_set_bits": block(
            """
            unsigned int count_set_bits(unsigned int n) {
                unsigned int count = 0;
                while (n) {
                    count += n & 1;
                    n >>= 1;
                }
                return count;
            }
            """
        ),
        "parity": block(
            """
            unsigned int parity(unsigned int n) {
                unsigned int p = 0;
                while (n) {
                    p ^= (n & 1);
                    n >>= 1;
                }
                return p;
            }
            """
        ),
        "reverse_bits": block(
            """
            unsigned int reverse_bits(unsigned int n) {
                unsigned int result = 0;
                for (int i = 0; i < 32; i++) {
                    result = (result << 1) | (n & 1);
                    n >>= 1;
                }
                return result;
            }
            """
        ),
        "next_power_of_two": block(
            """
            unsigned int next_power_of_two(unsigned int n) {
                if (n == 0) return 1;
                n--;
                n |= n >> 1;
                n |= n >> 2;
                n |= n >> 4;
                n |= n >> 8;
                n |= n >> 16;
                return n + 1;
            }
            """
        ),
        "lowest_set_bit": block(
            """
            unsigned int lowest_set_bit(unsigned int n) {
                return n & (~n + 1);
            }
            """
        ),
        "clear_lowest_set_bit": block(
            """
            unsigned int clear_lowest_set_bit(unsigned int n) {
                return n & (n - 1);
            }
            """
        ),
    }
    return sources[name]


def get_py_source(name: str) -> str:
    sources = {
        "is_power_of_two": block(
            """
            def is_power_of_two(n: int) -> bool:
                return n != 0 and (n & (n - 1)) == 0
            """
        ),
        "count_set_bits": block(
            """
            def count_set_bits(n: int) -> int:
                count = 0
                while n:
                    count += n & 1
                    n >>= 1
                return count
            """
        ),
        "parity": block(
            """
            def parity(n: int) -> int:
                p = 0
                while n:
                    p ^= (n & 1)
                    n >>= 1
                return p
            """
        ),
        "reverse_bits_32": block(
            """
            def reverse_bits_32(n: int) -> int:
                result = 0
                for _ in range(32):
                    result = (result << 1) | (n & 1)
                    n >>= 1
                return result
            """
        ),
        "next_power_of_two": block(
            """
            def next_power_of_two(n: int) -> int:
                if n == 0:
                    return 1
                n -= 1
                n |= n >> 1
                n |= n >> 2
                n |= n >> 4
                n |= n >> 8
                n |= n >> 16
                return n + 1
            """
        ),
        "lowest_set_bit": block(
            """
            def lowest_set_bit(n: int) -> int:
                return n & (~n + 1)
            """
        ),
        "clear_lowest_set_bit": block(
            """
            def clear_lowest_set_bit(n: int) -> int:
                return n & (n - 1)
            """
        ),
    }
    return sources[name]


def get_lean_translation(name: str, language: str) -> str:
    c_translations = {
        "is_power_of_two": block(
            """
            def is_power_of_two (n : UInt32) : Bool :=
              n != 0 && (n &&& (n - 1)) == 0
            """
        ),
        "count_set_bits": block(
            """
            def count_set_bits_go (n acc : UInt32) : Nat -> UInt32
              | 0 => acc
              | fuel + 1 =>
                  if n == 0 then acc
                  else count_set_bits_go (n >>> 1) (acc + (n &&& 1)) fuel

            def count_set_bits (n : UInt32) : UInt32 :=
              count_set_bits_go n 0 32
            """
        ),
        "parity": block(
            """
            def parity_go (n acc : UInt32) : Nat -> UInt32
              | 0 => acc
              | fuel + 1 =>
                  if n == 0 then acc
                  else parity_go (n >>> 1) (acc ^^^ (n &&& 1)) fuel

            def parity (n : UInt32) : UInt32 :=
              parity_go n 0 32
            """
        ),
        "reverse_bits": block(
            """
            def reverse_bits_go (n acc : UInt32) : Nat -> UInt32
              | 0 => acc
              | fuel + 1 =>
                  reverse_bits_go (n >>> 1) ((acc <<< 1) ||| (n &&& 1)) fuel

            def reverse_bits (n : UInt32) : UInt32 :=
              reverse_bits_go n 0 32
            """
        ),
        "next_power_of_two": block(
            """
            def next_power_of_two (n : UInt32) : UInt32 :=
              if n == 0 then 1
              else
                let n := n - 1
                let n := n ||| (n >>> 1)
                let n := n ||| (n >>> 2)
                let n := n ||| (n >>> 4)
                let n := n ||| (n >>> 8)
                let n := n ||| (n >>> 16)
                n + 1
            """
        ),
        "lowest_set_bit": block(
            """
            def lowest_set_bit (n : UInt32) : UInt32 :=
              n &&& ((~~~n) + 1)
            """
        ),
        "clear_lowest_set_bit": block(
            """
            def clear_lowest_set_bit (n : UInt32) : UInt32 :=
              n &&& (n - 1)
            """
        ),
    }

    py_translations = {
        "is_power_of_two": block(
            """
            def is_power_of_two_go (m : Nat) : Nat -> Bool
              | 0 => false
              | fuel + 1 =>
                  if m == 1 then true
                  else if m == 0 then false
                  else if m % 2 == 1 then false
                  else is_power_of_two_go (m / 2) fuel

            def is_power_of_two (n : Nat) : Bool :=
              is_power_of_two_go n (n + 1)
            """
        ),
        "count_set_bits": block(
            """
            def count_set_bits_go (m acc : Nat) : Nat -> Nat
              | 0 => acc
              | fuel + 1 =>
                  if m == 0 then acc
                  else count_set_bits_go (m / 2) (acc + (m % 2)) fuel

            def count_set_bits (n : Nat) : Nat :=
              count_set_bits_go n 0 (n + 1)
            """
        ),
        "parity": block(
            """
            def parity (n : Nat) : Nat :=
              count_set_bits n % 2
            """
        ),
        "reverse_bits_32": block(
            """
            def reverse_bits_32_go (m acc : Nat) : Nat -> Nat
              | 0 => acc
              | fuel + 1 =>
                  reverse_bits_32_go (m / 2) (acc * 2 + (m % 2)) fuel

            def reverse_bits_32 (n : Nat) : Nat :=
              reverse_bits_32_go n 0 32
            """
        ),
        "next_power_of_two": block(
            """
            def next_power_of_two_go (target candidate : Nat) : Nat -> Nat
              | 0 => candidate
              | fuel + 1 =>
                  if candidate < target then next_power_of_two_go target (candidate * 2) fuel
                  else candidate

            def next_power_of_two (n : Nat) : Nat :=
              if n == 0 then 1 else next_power_of_two_go n 1 (n + 1)
            """
        ),
        "lowest_set_bit": block(
            """
            def lowest_set_bit_go (m bit : Nat) : Nat -> Nat
              | 0 => 0
              | fuel + 1 =>
                  if m == 0 then 0
                  else if m % 2 == 1 then bit
                  else lowest_set_bit_go (m / 2) (bit * 2) fuel

            def lowest_set_bit (n : Nat) : Nat :=
              lowest_set_bit_go n 1 (n + 1)
            """
        ),
        "clear_lowest_set_bit": block(
            """
            def clear_lowest_set_bit (n : Nat) : Nat :=
              n - lowest_set_bit n
            """
        ),
    }

    translations = c_translations if language == "C" else py_translations
    return translations[name]


def get_c_tests(name: str) -> str:
    tests = {
        "is_power_of_two": block(
            """
            #include <assert.h>
            #include <stdio.h>

            int is_power_of_two(unsigned int n) {
                return n != 0 && (n & (n - 1)) == 0;
            }

            int main() {
                assert(is_power_of_two(0) == 0);
                assert(is_power_of_two(1) == 1);
                assert(is_power_of_two(16) == 1);
                assert(is_power_of_two(18) == 0);
                assert(is_power_of_two(1024) == 1);
                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "count_set_bits": block(
            """
            #include <assert.h>
            #include <stdio.h>

            unsigned int count_set_bits(unsigned int n) {
                unsigned int count = 0;
                while (n) {
                    count += n & 1;
                    n >>= 1;
                }
                return count;
            }

            int main() {
                assert(count_set_bits(0u) == 0u);
                assert(count_set_bits(1u) == 1u);
                assert(count_set_bits(7u) == 3u);
                assert(count_set_bits(0xF0F0u) == 8u);
                assert(count_set_bits(0xFFFFFFFFu) == 32u);
                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "parity": block(
            """
            #include <assert.h>
            #include <stdio.h>

            unsigned int parity(unsigned int n) {
                unsigned int p = 0;
                while (n) {
                    p ^= (n & 1);
                    n >>= 1;
                }
                return p;
            }

            int main() {
                assert(parity(0u) == 0u);
                assert(parity(1u) == 1u);
                assert(parity(7u) == 1u);
                assert(parity(10u) == 0u);
                assert(parity(0xFFFFFFFFu) == 0u);
                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "reverse_bits": block(
            """
            #include <assert.h>
            #include <stdio.h>

            unsigned int reverse_bits(unsigned int n) {
                unsigned int result = 0;
                for (int i = 0; i < 32; i++) {
                    result = (result << 1) | (n & 1);
                    n >>= 1;
                }
                return result;
            }

            int main() {
                assert(reverse_bits(0u) == 0u);
                assert(reverse_bits(1u) == 0x80000000u);
                assert(reverse_bits(5u) == 0xA0000000u);
                assert(reverse_bits(0xF0F0F0F0u) == 0x0F0F0F0Fu);
                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "next_power_of_two": block(
            """
            #include <assert.h>
            #include <stdio.h>

            unsigned int next_power_of_two(unsigned int n) {
                if (n == 0) return 1;
                n--;
                n |= n >> 1;
                n |= n >> 2;
                n |= n >> 4;
                n |= n >> 8;
                n |= n >> 16;
                return n + 1;
            }

            int main() {
                assert(next_power_of_two(0u) == 1u);
                assert(next_power_of_two(1u) == 1u);
                assert(next_power_of_two(5u) == 8u);
                assert(next_power_of_two(16u) == 16u);
                assert(next_power_of_two(31u) == 32u);
                assert(next_power_of_two(1025u) == 2048u);
                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "lowest_set_bit": block(
            """
            #include <assert.h>
            #include <stdio.h>

            unsigned int lowest_set_bit(unsigned int n) {
                return n & (~n + 1);
            }

            int main() {
                assert(lowest_set_bit(0u) == 0u);
                assert(lowest_set_bit(1u) == 1u);
                assert(lowest_set_bit(12u) == 4u);
                assert(lowest_set_bit(40u) == 8u);
                assert(lowest_set_bit(48u) == 16u);
                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "clear_lowest_set_bit": block(
            """
            #include <assert.h>
            #include <stdio.h>

            unsigned int clear_lowest_set_bit(unsigned int n) {
                return n & (n - 1);
            }

            int main() {
                assert(clear_lowest_set_bit(0u) == 0u);
                assert(clear_lowest_set_bit(1u) == 0u);
                assert(clear_lowest_set_bit(12u) == 8u);
                assert(clear_lowest_set_bit(40u) == 32u);
                assert(clear_lowest_set_bit(48u) == 32u);
                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
    }
    return tests[name]


def get_py_tests(name: str) -> str:
    tests = {
        "is_power_of_two": block(
            """
            def is_power_of_two(n: int) -> bool:
                return n != 0 and (n & (n - 1)) == 0

            assert is_power_of_two(0) is False
            assert is_power_of_two(1) is True
            assert is_power_of_two(16) is True
            assert is_power_of_two(18) is False
            assert is_power_of_two(1024) is True
            print("All tests passed!")
            """
        ),
        "count_set_bits": block(
            """
            def count_set_bits(n: int) -> int:
                count = 0
                while n:
                    count += n & 1
                    n >>= 1
                return count

            assert count_set_bits(0) == 0
            assert count_set_bits(1) == 1
            assert count_set_bits(7) == 3
            assert count_set_bits(0xF0F0) == 8
            assert count_set_bits(0xFFFFFFFF) == 32
            print("All tests passed!")
            """
        ),
        "parity": block(
            """
            def parity(n: int) -> int:
                p = 0
                while n:
                    p ^= (n & 1)
                    n >>= 1
                return p

            assert parity(0) == 0
            assert parity(1) == 1
            assert parity(7) == 1
            assert parity(10) == 0
            assert parity(0xFFFFFFFF) == 0
            print("All tests passed!")
            """
        ),
        "reverse_bits_32": block(
            """
            def reverse_bits_32(n: int) -> int:
                result = 0
                for _ in range(32):
                    result = (result << 1) | (n & 1)
                    n >>= 1
                return result

            assert reverse_bits_32(0) == 0
            assert reverse_bits_32(1) == 0x80000000
            assert reverse_bits_32(5) == 0xA0000000
            assert reverse_bits_32(0xF0F0F0F0) == 0x0F0F0F0F
            print("All tests passed!")
            """
        ),
        "next_power_of_two": block(
            """
            def next_power_of_two(n: int) -> int:
                if n == 0:
                    return 1
                n -= 1
                n |= n >> 1
                n |= n >> 2
                n |= n >> 4
                n |= n >> 8
                n |= n >> 16
                return n + 1

            assert next_power_of_two(0) == 1
            assert next_power_of_two(1) == 1
            assert next_power_of_two(5) == 8
            assert next_power_of_two(16) == 16
            assert next_power_of_two(31) == 32
            assert next_power_of_two(1025) == 2048
            print("All tests passed!")
            """
        ),
        "lowest_set_bit": block(
            """
            def lowest_set_bit(n: int) -> int:
                return n & (~n + 1)

            assert lowest_set_bit(0) == 0
            assert lowest_set_bit(1) == 1
            assert lowest_set_bit(12) == 4
            assert lowest_set_bit(40) == 8
            assert lowest_set_bit(48) == 16
            print("All tests passed!")
            """
        ),
        "clear_lowest_set_bit": block(
            """
            def clear_lowest_set_bit(n: int) -> int:
                return n & (n - 1)

            assert clear_lowest_set_bit(0) == 0
            assert clear_lowest_set_bit(1) == 0
            assert clear_lowest_set_bit(12) == 8
            assert clear_lowest_set_bit(40) == 32
            assert clear_lowest_set_bit(48) == 32
            print("All tests passed!")
            """
        ),
    }
    return tests[name]


def get_lean_tests(name: str, language: str) -> str:
    tests = {
        ("C", "is_power_of_two"): block(
            """
            #eval is_power_of_two 0
            #eval is_power_of_two 16
            #eval is_power_of_two 18
            """
        ),
        ("C", "count_set_bits"): block(
            """
            #eval count_set_bits 0
            #eval count_set_bits 7
            #eval count_set_bits 61680
            """
        ),
        ("C", "parity"): block(
            """
            #eval parity 0
            #eval parity 7
            #eval parity 10
            """
        ),
        ("C", "reverse_bits"): block(
            """
            #eval reverse_bits 0
            #eval reverse_bits 1
            #eval reverse_bits 5
            """
        ),
        ("C", "next_power_of_two"): block(
            """
            #eval next_power_of_two 0
            #eval next_power_of_two 5
            #eval next_power_of_two 31
            """
        ),
        ("C", "lowest_set_bit"): block(
            """
            #eval lowest_set_bit 0
            #eval lowest_set_bit 12
            #eval lowest_set_bit 40
            """
        ),
        ("C", "clear_lowest_set_bit"): block(
            """
            #eval clear_lowest_set_bit 0
            #eval clear_lowest_set_bit 12
            #eval clear_lowest_set_bit 40
            """
        ),
        ("Python", "is_power_of_two"): block(
            """
            #eval is_power_of_two 0
            #eval is_power_of_two 16
            #eval is_power_of_two 18
            """
        ),
        ("Python", "count_set_bits"): block(
            """
            #eval count_set_bits 0
            #eval count_set_bits 7
            #eval count_set_bits 61680
            """
        ),
        ("Python", "parity"): block(
            """
            #eval parity 0
            #eval parity 7
            #eval parity 10
            """
        ),
        ("Python", "reverse_bits_32"): block(
            """
            #eval reverse_bits_32 0
            #eval reverse_bits_32 1
            #eval reverse_bits_32 5
            """
        ),
        ("Python", "next_power_of_two"): block(
            """
            #eval next_power_of_two 0
            #eval next_power_of_two 5
            #eval next_power_of_two 31
            """
        ),
        ("Python", "lowest_set_bit"): block(
            """
            #eval lowest_set_bit 0
            #eval lowest_set_bit 12
            #eval lowest_set_bit 40
            """
        ),
        ("Python", "clear_lowest_set_bit"): block(
            """
            #eval clear_lowest_set_bit 0
            #eval clear_lowest_set_bit 12
            #eval clear_lowest_set_bit 40
            """
        ),
    }
    return tests[(language, name)]


def theorem(name: str, statement: str, proof: str, proof_incomplete: bool) -> dict[str, object]:
    return {
        "name": name,
        "statement": statement,
        "proof": proof,
        "proof_incomplete": proof_incomplete,
    }


def get_theorems(name: str, language: str) -> list[dict[str, object]]:
    c_theorems = {
        "is_power_of_two": [
            theorem(
                "is_power_of_two_eq_bit_test",
                "theorem is_power_of_two_eq_bit_test (n : UInt32) : is_power_of_two n = (n != 0 && (n &&& (n - 1)) == 0)",
                "by rfl",
                False,
            ),
            theorem(
                "is_power_of_two_true_iff_single_bit",
                "theorem is_power_of_two_true_iff_single_bit (n : UInt32) : Iff (is_power_of_two n = true) (And (n != 0) ((n &&& (n - 1)) = 0))",
                "by sorry",
                True,
            ),
            theorem(
                "is_power_of_two_shifted_one",
                "theorem is_power_of_two_shifted_one (k : Nat) (hk : k < 32) : is_power_of_two (UInt32.ofNat (2 ^ k)) = true",
                "by sorry",
                True,
            ),
        ],
        "count_set_bits": [
            theorem(
                "count_set_bits_eq_go",
                "theorem count_set_bits_eq_go (n : UInt32) : count_set_bits n = count_set_bits_go n 0 32",
                "by rfl",
                False,
            ),
            theorem(
                "count_set_bits_zero_iff",
                "theorem count_set_bits_zero_iff (n : UInt32) : Iff (count_set_bits n = 0) (n = 0)",
                "by sorry",
                True,
            ),
            theorem(
                "count_set_bits_le_32",
                "theorem count_set_bits_le_32 (n : UInt32) : count_set_bits n <= 32",
                "by sorry",
                True,
            ),
            theorem(
                "count_set_bits_singleton_bit",
                "theorem count_set_bits_singleton_bit (k : Nat) (hk : k < 32) : count_set_bits (UInt32.ofNat (2 ^ k)) = 1",
                "by sorry",
                True,
            ),
        ],
        "parity": [
            theorem(
                "parity_eq_go",
                "theorem parity_eq_go (n : UInt32) : parity n = parity_go n 0 32",
                "by rfl",
                False,
            ),
            theorem(
                "parity_range",
                "theorem parity_range (n : UInt32) : Or (parity n = 0) (parity n = 1)",
                "by sorry",
                True,
            ),
            theorem(
                "parity_singleton_bit",
                "theorem parity_singleton_bit (k : Nat) (hk : k < 32) : parity (UInt32.ofNat (2 ^ k)) = 1",
                "by sorry",
                True,
            ),
            theorem(
                "parity_xor_hom",
                "theorem parity_xor_hom (a b : UInt32) : parity (a ^^^ b) = (parity a ^^^ parity b)",
                "by sorry",
                True,
            ),
        ],
        "reverse_bits": [
            theorem(
                "reverse_bits_eq_go",
                "theorem reverse_bits_eq_go (n : UInt32) : reverse_bits n = reverse_bits_go n 0 32",
                "by rfl",
                False,
            ),
            theorem(
                "reverse_bits_involution",
                "theorem reverse_bits_involution (n : UInt32) : reverse_bits (reverse_bits n) = n",
                "by sorry",
                True,
            ),
            theorem(
                "reverse_bits_singleton_bit",
                "theorem reverse_bits_singleton_bit (k : Nat) (hk : k < 32) : reverse_bits (UInt32.ofNat (2 ^ k)) = UInt32.ofNat (2 ^ (31 - k))",
                "by sorry",
                True,
            ),
        ],
        "next_power_of_two": [
            theorem(
                "next_power_of_two_fixpoint",
                "theorem next_power_of_two_fixpoint (k : Nat) (hk : k < 32) : next_power_of_two (UInt32.ofNat (2 ^ k)) = UInt32.ofNat (2 ^ k)",
                "by sorry",
                True,
            ),
            theorem(
                "next_power_of_two_output_is_power_of_two",
                "theorem next_power_of_two_output_is_power_of_two (n : UInt32) (hpos : 0 < n.toNat) (hbound : n.toNat <= 2 ^ 31) : is_power_of_two (next_power_of_two n) = true",
                "by sorry",
                True,
            ),
            theorem(
                "next_power_of_two_lower_bound",
                "theorem next_power_of_two_lower_bound (n : UInt32) (hpos : 0 < n.toNat) (hbound : n.toNat <= 2 ^ 31) : n.toNat <= (next_power_of_two n).toNat",
                "by sorry",
                True,
            ),
        ],
        "lowest_set_bit": [
            theorem(
                "lowest_set_bit_eq_mask",
                "theorem lowest_set_bit_eq_mask (n : UInt32) : lowest_set_bit n = (n &&& ((~~~n) + 1))",
                "by rfl",
                False,
            ),
            theorem(
                "lowest_set_bit_zero_iff",
                "theorem lowest_set_bit_zero_iff (n : UInt32) : Iff (lowest_set_bit n = 0) (n = 0)",
                "by sorry",
                True,
            ),
            theorem(
                "lowest_set_bit_is_power_of_two",
                "theorem lowest_set_bit_is_power_of_two (n : UInt32) (h : n != 0) : is_power_of_two (lowest_set_bit n) = true",
                "by sorry",
                True,
            ),
            theorem(
                "lowest_set_bit_submask",
                "theorem lowest_set_bit_submask (n : UInt32) : (lowest_set_bit n &&& n) = lowest_set_bit n",
                "by sorry",
                True,
            ),
        ],
        "clear_lowest_set_bit": [
            theorem(
                "clear_lowest_set_bit_eq_mask",
                "theorem clear_lowest_set_bit_eq_mask (n : UInt32) : clear_lowest_set_bit n = (n &&& (n - 1))",
                "by rfl",
                False,
            ),
            theorem(
                "clear_lowest_set_bit_fixed_zero",
                "theorem clear_lowest_set_bit_fixed_zero (n : UInt32) : Iff (clear_lowest_set_bit n = n) (n = 0)",
                "by sorry",
                True,
            ),
            theorem(
                "clear_lowest_set_bit_lt",
                "theorem clear_lowest_set_bit_lt (n : UInt32) (h : n != 0) : clear_lowest_set_bit n < n",
                "by sorry",
                True,
            ),
            theorem(
                "clear_lowest_set_bit_popcount",
                "theorem clear_lowest_set_bit_popcount (n : UInt32) (h : n != 0) : count_set_bits (clear_lowest_set_bit n) + 1 = count_set_bits n",
                "by sorry",
                True,
            ),
        ],
    }

    py_theorems = {
        "is_power_of_two": [
            theorem(
                "is_power_of_two_eq_go",
                "theorem is_power_of_two_eq_go (n : Nat) : is_power_of_two n = is_power_of_two_go n (n + 1)",
                "by rfl",
                False,
            ),
            theorem(
                "is_power_of_two_iff_exists_pow",
                "theorem is_power_of_two_iff_exists_pow (n : Nat) : Iff (is_power_of_two n = true) (Exists fun k : Nat => n = 2 ^ k)",
                "by sorry",
                True,
            ),
            theorem(
                "is_power_of_two_of_pow",
                "theorem is_power_of_two_of_pow (k : Nat) : is_power_of_two (2 ^ k) = true",
                "by sorry",
                True,
            ),
            theorem(
                "is_power_of_two_double",
                "theorem is_power_of_two_double (n : Nat) (h : n != 0) : is_power_of_two (2 * n) = is_power_of_two n",
                "by sorry",
                True,
            ),
        ],
        "count_set_bits": [
            theorem(
                "count_set_bits_eq_go",
                "theorem count_set_bits_eq_go (n : Nat) : count_set_bits n = count_set_bits_go n 0 (n + 1)",
                "by rfl",
                False,
            ),
            theorem(
                "count_set_bits_zero_iff",
                "theorem count_set_bits_zero_iff (n : Nat) : Iff (count_set_bits n = 0) (n = 0)",
                "by sorry",
                True,
            ),
            theorem(
                "count_set_bits_even",
                "theorem count_set_bits_even (n : Nat) : count_set_bits (2 * n) = count_set_bits n",
                "by sorry",
                True,
            ),
            theorem(
                "count_set_bits_odd",
                "theorem count_set_bits_odd (n : Nat) : count_set_bits (2 * n + 1) = count_set_bits n + 1",
                "by sorry",
                True,
            ),
        ],
        "parity": [
            theorem(
                "parity_eq_count_set_bits_mod_two",
                "theorem parity_eq_count_set_bits_mod_two (n : Nat) : parity n = count_set_bits n % 2",
                "by rfl",
                False,
            ),
            theorem(
                "parity_range",
                "theorem parity_range (n : Nat) : parity n <= 1",
                "by sorry",
                True,
            ),
            theorem(
                "parity_even",
                "theorem parity_even (n : Nat) : parity (2 * n) = parity n",
                "by sorry",
                True,
            ),
            theorem(
                "parity_odd",
                "theorem parity_odd (n : Nat) : parity (2 * n + 1) = if parity n = 0 then 1 else 0",
                "by sorry",
                True,
            ),
        ],
        "reverse_bits_32": [
            theorem(
                "reverse_bits_32_eq_go",
                "theorem reverse_bits_32_eq_go (n : Nat) : reverse_bits_32 n = reverse_bits_32_go n 0 32",
                "by rfl",
                False,
            ),
            theorem(
                "reverse_bits_32_lt",
                "theorem reverse_bits_32_lt (n : Nat) : reverse_bits_32 n < 2 ^ 32",
                "by sorry",
                True,
            ),
            theorem(
                "reverse_bits_32_involution_mod",
                "theorem reverse_bits_32_involution_mod (n : Nat) : reverse_bits_32 (reverse_bits_32 n) = n % 2 ^ 32",
                "by sorry",
                True,
            ),
            theorem(
                "reverse_bits_32_singleton_bit",
                "theorem reverse_bits_32_singleton_bit (k : Nat) (hk : k < 32) : reverse_bits_32 (2 ^ k) = 2 ^ (31 - k)",
                "by sorry",
                True,
            ),
        ],
        "next_power_of_two": [
            theorem(
                "next_power_of_two_def",
                "theorem next_power_of_two_def (n : Nat) : next_power_of_two n = (if n == 0 then 1 else next_power_of_two_go n 1 (n + 1))",
                "by rfl",
                False,
            ),
            theorem(
                "next_power_of_two_is_power_of_two",
                "theorem next_power_of_two_is_power_of_two (n : Nat) : is_power_of_two (next_power_of_two n) = true",
                "by sorry",
                True,
            ),
            theorem(
                "next_power_of_two_lower_bound",
                "theorem next_power_of_two_lower_bound (n : Nat) : n <= next_power_of_two n",
                "by sorry",
                True,
            ),
            theorem(
                "next_power_of_two_fixpoint",
                "theorem next_power_of_two_fixpoint (k : Nat) : next_power_of_two (2 ^ k) = 2 ^ k",
                "by sorry",
                True,
            ),
        ],
        "lowest_set_bit": [
            theorem(
                "lowest_set_bit_eq_go",
                "theorem lowest_set_bit_eq_go (n : Nat) : lowest_set_bit n = lowest_set_bit_go n 1 (n + 1)",
                "by rfl",
                False,
            ),
            theorem(
                "lowest_set_bit_zero_iff",
                "theorem lowest_set_bit_zero_iff (n : Nat) : Iff (lowest_set_bit n = 0) (n = 0)",
                "by sorry",
                True,
            ),
            theorem(
                "lowest_set_bit_dvd",
                "theorem lowest_set_bit_dvd (n : Nat) : lowest_set_bit n ∣ n",
                "by sorry",
                True,
            ),
            theorem(
                "lowest_set_bit_is_power_of_two",
                "theorem lowest_set_bit_is_power_of_two (n : Nat) (h : n != 0) : is_power_of_two (lowest_set_bit n) = true",
                "by sorry",
                True,
            ),
        ],
        "clear_lowest_set_bit": [
            theorem(
                "clear_lowest_set_bit_eq_sub",
                "theorem clear_lowest_set_bit_eq_sub (n : Nat) : clear_lowest_set_bit n = n - lowest_set_bit n",
                "by rfl",
                False,
            ),
            theorem(
                "clear_lowest_set_bit_add_lowest",
                "theorem clear_lowest_set_bit_add_lowest (n : Nat) : clear_lowest_set_bit n + lowest_set_bit n = n",
                "by sorry",
                True,
            ),
            theorem(
                "clear_lowest_set_bit_lt",
                "theorem clear_lowest_set_bit_lt (n : Nat) (h : n != 0) : clear_lowest_set_bit n < n",
                "by sorry",
                True,
            ),
            theorem(
                "clear_lowest_set_bit_popcount",
                "theorem clear_lowest_set_bit_popcount (n : Nat) (h : n != 0) : count_set_bits (clear_lowest_set_bit n) + 1 = count_set_bits n",
                "by sorry",
                True,
            ),
        ],
    }

    theorems = c_theorems if language == "C" else py_theorems
    return theorems[name]


def get_deps(name: str, language: str) -> list[str]:
    deps = {
        ("C", "is_power_of_two"): [],
        ("C", "count_set_bits"): [],
        ("C", "parity"): [],
        ("C", "reverse_bits"): [],
        ("C", "next_power_of_two"): ["is_power_of_two"],
        ("C", "lowest_set_bit"): ["is_power_of_two"],
        ("C", "clear_lowest_set_bit"): ["count_set_bits"],
        ("Python", "is_power_of_two"): [],
        ("Python", "count_set_bits"): [],
        ("Python", "parity"): ["count_set_bits"],
        ("Python", "reverse_bits_32"): [],
        ("Python", "next_power_of_two"): ["is_power_of_two"],
        ("Python", "lowest_set_bit"): ["is_power_of_two"],
        ("Python", "clear_lowest_set_bit"): ["count_set_bits", "lowest_set_bit"],
    }
    return deps[(language, name)]


FUNCTIONS_BY_LANGUAGE = {
    "C": [
        "is_power_of_two",
        "count_set_bits",
        "parity",
        "reverse_bits",
        "next_power_of_two",
        "lowest_set_bit",
        "clear_lowest_set_bit",
    ],
    "Python": [
        "is_power_of_two",
        "count_set_bits",
        "parity",
        "reverse_bits_32",
        "next_power_of_two",
        "lowest_set_bit",
        "clear_lowest_set_bit",
    ],
}

OUTPUT_PATH = Path(
    "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch06_bits.jsonl"
)


def build_record(language: str, name: str) -> dict[str, object]:
    return {
        "language": language,
        "source": get_c_source(name) if language == "C" else get_py_source(name),
        "lean_translation": get_lean_translation(name, language),
        "tests": get_c_tests(name) if language == "C" else get_py_tests(name),
        "lean_tests": get_lean_tests(name, language),
        "theorems": get_theorems(name, language),
        "deps_fully_translated": get_deps(name, language),
        "axiomatized_deps": [],
        "skip_reason": None,
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8") as handle:
        for language, names in FUNCTIONS_BY_LANGUAGE.items():
            for name in names:
                handle.write(json.dumps(build_record(language, name)) + "\n")


if __name__ == "__main__":
    main()
