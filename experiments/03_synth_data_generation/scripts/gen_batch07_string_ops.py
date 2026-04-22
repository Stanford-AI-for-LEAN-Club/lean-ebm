#!/usr/bin/env python3

import json
from pathlib import Path


ROOT = Path("/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation")
OUTPUT_PATH = ROOT / "output" / "batch07_string_ops.jsonl"
FUNCTIONS = [
    "str_len",
    "str_equal",
    "is_palindrome",
    "count_char",
    "to_upper",
    "to_lower",
    "char_is_digit",
    "char_is_alpha",
]


def theorem(name: str, statement: str, proof: str, proof_incomplete: bool = False) -> dict:
    return {
        "name": name,
        "statement": statement,
        "proof": proof,
        "proof_incomplete": proof_incomplete,
    }


def get_c_source(name: str) -> str:
    sources = {
        "str_len": """int str_len(const char *s) {
    int len = 0;
    while (s[len] != '\\0') {
        len++;
    }
    return len;
}""",
        "str_equal": """int str_equal(const char *a, const char *b) {
    int i = 0;
    while (a[i] != '\\0' && b[i] != '\\0') {
        if (a[i] != b[i]) return 0;
        i++;
    }
    return a[i] == b[i];
}""",
        "is_palindrome": """int is_palindrome(const char *s, int len) {
    for (int i = 0; i < len / 2; i++) {
        if (s[i] != s[len - 1 - i]) return 0;
    }
    return 1;
}""",
        "count_char": """int count_char(const char *s, char c) {
    int count = 0;
    for (int i = 0; s[i] != '\\0'; i++) {
        if (s[i] == c) count++;
    }
    return count;
}""",
        "to_upper": """void to_upper(char *s) {
    for (int i = 0; s[i] != '\\0'; i++) {
        if (s[i] >= 'a' && s[i] <= 'z') {
            s[i] = s[i] - 'a' + 'A';
        }
    }
}""",
        "to_lower": """void to_lower(char *s) {
    for (int i = 0; s[i] != '\\0'; i++) {
        if (s[i] >= 'A' && s[i] <= 'Z') {
            s[i] = s[i] - 'A' + 'a';
        }
    }
}""",
        "char_is_digit": """int char_is_digit(char c) {
    return c >= '0' && c <= '9';
}""",
        "char_is_alpha": """int char_is_alpha(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z');
}""",
    }
    return sources[name]


def get_py_source(name: str) -> str:
    sources = {
        "str_len": """def str_len(s: str) -> int:
    count = 0
    for _ in s:
        count += 1
    return count""",
        "str_equal": """def str_equal(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True""",
        "is_palindrome": """def is_palindrome(s: str) -> bool:
    n = len(s)
    for i in range(n // 2):
        if s[i] != s[n - 1 - i]:
            return False
    return True""",
        "count_char": """def count_char(s: str, c: str) -> int:
    count = 0
    for ch in s:
        if ch == c:
            count += 1
    return count""",
        "to_upper": """def to_upper(s: str) -> str:
    result = []
    for c in s:
        if 'a' <= c <= 'z':
            result.append(chr(ord(c) - ord('a') + ord('A')))
        else:
            result.append(c)
    return ''.join(result)""",
        "to_lower": """def to_lower(s: str) -> str:
    result = []
    for c in s:
        if 'A' <= c <= 'Z':
            result.append(chr(ord(c) - ord('A') + ord('a')))
        else:
            result.append(c)
    return ''.join(result)""",
        "char_is_digit": """def char_is_digit(c: str) -> bool:
    return '0' <= c <= '9'""",
        "char_is_alpha": """def char_is_alpha(c: str) -> bool:
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z')""",
    }
    return sources[name]


LEAN_STR_LEN = """def str_len (s : String) : Nat :=
  s.length"""

LEAN_STR_EQUAL = """def str_equal (a b : String) : Bool :=
  a == b"""

LEAN_IS_PALINDROME_C = """def is_palindrome (s : String) (len : Nat) : Bool :=
  let xs := s.toList.take len
  xs == xs.reverse"""

LEAN_IS_PALINDROME_PY = """def is_palindrome (s : String) : Bool :=
  let xs := s.toList
  xs == xs.reverse"""

LEAN_COUNT_CHAR = """def count_char (s : String) (c : Char) : Nat :=
  (s.toList.filter (fun ch => ch == c)).length"""

LEAN_TO_UPPER = """def upperChar (c : Char) : Char :=
  if 'a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat then
    Char.ofNat (c.toNat - 'a'.toNat + 'A'.toNat)
  else
    c

def to_upper (s : String) : String :=
  String.mk (s.toList.map upperChar)"""

LEAN_TO_LOWER = """def lowerChar (c : Char) : Char :=
  if 'A'.toNat ≤ c.toNat ∧ c.toNat ≤ 'Z'.toNat then
    Char.ofNat (c.toNat - 'A'.toNat + 'a'.toNat)
  else
    c

def to_lower (s : String) : String :=
  String.mk (s.toList.map lowerChar)"""

LEAN_CHAR_IS_DIGIT = """def char_is_digit (c : Char) : Bool :=
  decide ('0'.toNat ≤ c.toNat ∧ c.toNat ≤ '9'.toNat)"""

LEAN_CHAR_IS_ALPHA = """def char_is_alpha (c : Char) : Bool :=
  decide (('a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat) ∨ ('A'.toNat ≤ c.toNat ∧ c.toNat ≤ 'Z'.toNat))"""


def get_lean_translation(name: str, lang: str) -> str:
    translations = {
        "str_len": LEAN_STR_LEN,
        "str_equal": LEAN_STR_EQUAL,
        "count_char": LEAN_COUNT_CHAR,
        "to_upper": LEAN_TO_UPPER,
        "to_lower": LEAN_TO_LOWER,
        "char_is_digit": LEAN_CHAR_IS_DIGIT,
        "char_is_alpha": LEAN_CHAR_IS_ALPHA,
    }
    if name == "is_palindrome":
        return LEAN_IS_PALINDROME_C if lang == "C" else LEAN_IS_PALINDROME_PY
    return translations[name]


def get_c_tests(name: str) -> str:
    source = get_c_source(name)
    mains = {
        "str_len": """int main(void) {
    assert(str_len("") == 0);
    assert(str_len("lean") == 4);
    assert(str_len("racecar") == 7);
    return 0;
}""",
        "str_equal": """int main(void) {
    assert(str_equal("", "") == 1);
    assert(str_equal("lean", "lean") == 1);
    assert(str_equal("lean", "Lean") == 0);
    assert(str_equal("abc", "abcd") == 0);
    return 0;
}""",
        "is_palindrome": """int main(void) {
    assert(is_palindrome("racecar", 7) == 1);
    assert(is_palindrome("abba", 4) == 1);
    assert(is_palindrome("abc", 3) == 0);
    assert(is_palindrome("abbaXYZ", 4) == 1);
    return 0;
}""",
        "count_char": """int main(void) {
    assert(count_char("", 'a') == 0);
    assert(count_char("banana", 'a') == 3);
    assert(count_char("banana", 'n') == 2);
    assert(count_char("banana", 'z') == 0);
    return 0;
}""",
        "to_upper": """int main(void) {
    char s1[] = "Lean42!";
    char s2[] = "already UPPER";
    char s3[] = "";
    to_upper(s1);
    to_upper(s2);
    to_upper(s3);
    assert(strcmp(s1, "LEAN42!") == 0);
    assert(strcmp(s2, "ALREADY UPPER") == 0);
    assert(strcmp(s3, "") == 0);
    return 0;
}""",
        "to_lower": """int main(void) {
    char s1[] = "Lean42!";
    char s2[] = "already lower";
    char s3[] = "";
    to_lower(s1);
    to_lower(s2);
    to_lower(s3);
    assert(strcmp(s1, "lean42!") == 0);
    assert(strcmp(s2, "already lower") == 0);
    assert(strcmp(s3, "") == 0);
    return 0;
}""",
        "char_is_digit": """int main(void) {
    assert(char_is_digit('0') == 1);
    assert(char_is_digit('5') == 1);
    assert(char_is_digit('9') == 1);
    assert(char_is_digit('a') == 0);
    return 0;
}""",
        "char_is_alpha": """int main(void) {
    assert(char_is_alpha('a') == 1);
    assert(char_is_alpha('Z') == 1);
    assert(char_is_alpha('5') == 0);
    assert(char_is_alpha('_') == 0);
    return 0;
}""",
    }
    headers = "#include <assert.h>\n#include <string.h>\n\n"
    return f"{headers}{source}\n\n{mains[name]}"


def get_py_tests(name: str) -> str:
    source = get_py_source(name)
    tests = {
        "str_len": """assert str_len("") == 0
assert str_len("lean") == 4
assert str_len("racecar") == 7""",
        "str_equal": """assert str_equal("", "") is True
assert str_equal("lean", "lean") is True
assert str_equal("lean", "Lean") is False
assert str_equal("abc", "abcd") is False""",
        "is_palindrome": """assert is_palindrome("racecar") is True
assert is_palindrome("abba") is True
assert is_palindrome("abc") is False
assert is_palindrome("") is True""",
        "count_char": """assert count_char("", "a") == 0
assert count_char("banana", "a") == 3
assert count_char("banana", "n") == 2
assert count_char("banana", "z") == 0""",
        "to_upper": '''assert to_upper("Lean42!") == "LEAN42!"
assert to_upper("already UPPER") == "ALREADY UPPER"
assert to_upper("") == ""''',
        "to_lower": '''assert to_lower("Lean42!") == "lean42!"
assert to_lower("already lower") == "already lower"
assert to_lower("") == ""''',
        "char_is_digit": """assert char_is_digit("0") is True
assert char_is_digit("5") is True
assert char_is_digit("9") is True
assert char_is_digit("a") is False""",
        "char_is_alpha": """assert char_is_alpha("a") is True
assert char_is_alpha("Z") is True
assert char_is_alpha("5") is False
assert char_is_alpha("_") is False""",
    }
    return f"{source}\n\n{tests[name]}"


def get_lean_tests(name: str, lang: str) -> str:
    if name == "str_len":
        return """#eval str_len ""
#eval str_len "lean"
#eval str_len "racecar"
#check str_len"""
    if name == "str_equal":
        return """#eval str_equal "" ""
#eval str_equal "lean" "lean"
#eval str_equal "lean" "Lean"
#check str_equal"""
    if name == "is_palindrome" and lang == "C":
        return """#eval is_palindrome "racecar" 7
#eval is_palindrome "abc" 3
#eval is_palindrome "abbaXYZ" 4
#check is_palindrome"""
    if name == "is_palindrome":
        return """#eval is_palindrome "racecar"
#eval is_palindrome "abc"
#eval is_palindrome ""
#check is_palindrome"""
    if name == "count_char":
        return """#eval count_char "" 'a'
#eval count_char "banana" 'a'
#eval count_char "banana" 'n'
#check count_char"""
    if name == "to_upper":
        return """#eval to_upper "Lean42!"
#eval to_upper "already UPPER"
#eval to_upper ""
#check to_upper"""
    if name == "to_lower":
        return """#eval to_lower "Lean42!"
#eval to_lower "already lower"
#eval to_lower ""
#check to_lower"""
    if name == "char_is_digit":
        return """#eval char_is_digit '0'
#eval char_is_digit '5'
#eval char_is_digit 'a'
#check char_is_digit"""
    return """#eval char_is_alpha 'a'
#eval char_is_alpha 'Z'
#eval char_is_alpha '5'
#check char_is_alpha"""


def get_theorems(name: str, lang: str) -> list[dict]:
    if name == "str_len":
        return [
            theorem(
                "str_len_eq_length",
                "theorem str_len_eq_length (s : String) : str_len s = s.length",
                "by\n  rfl",
            ),
            theorem(
                "str_len_append",
                "theorem str_len_append (s t : String) : str_len (s ++ t) = str_len s + str_len t",
                "by\n  simpa [str_len] using String.length_append s t",
            ),
        ]
    if name == "str_equal":
        return [
            theorem(
                "str_equal_eq_true_iff",
                "theorem str_equal_eq_true_iff (a b : String) : str_equal a b = true ↔ a = b",
                "by\n  simp [str_equal]",
            ),
            theorem(
                "str_equal_refl",
                "theorem str_equal_refl (s : String) : str_equal s s = true",
                "by\n  simp [str_equal]",
            ),
            theorem(
                "str_equal_comm",
                "theorem str_equal_comm (a b : String) : str_equal a b = str_equal b a",
                "by\n  sorry",
                proof_incomplete=True,
            ),
        ]
    if name == "is_palindrome" and lang == "C":
        return [
            theorem(
                "is_palindrome_prefix_iff",
                """theorem is_palindrome_prefix_iff (s : String) (len : Nat) :
    is_palindrome s len = true ↔ s.toList.take len = (s.toList.take len).reverse""",
                "by\n  simp [is_palindrome]",
            ),
            theorem(
                "is_palindrome_full_length_iff",
                """theorem is_palindrome_full_length_iff (s : String) :
    is_palindrome s s.length = true ↔ s.toList = s.toList.reverse""",
                "by\n  sorry",
                proof_incomplete=True,
            ),
            theorem(
                "is_palindrome_zero_len",
                "theorem is_palindrome_zero_len (s : String) : is_palindrome s 0 = true",
                "by\n  simp [is_palindrome]",
            ),
        ]
    if name == "is_palindrome":
        return [
            theorem(
                "is_palindrome_iff",
                "theorem is_palindrome_iff (s : String) : is_palindrome s = true ↔ s.toList = s.toList.reverse",
                "by\n  simp [is_palindrome]",
            ),
            theorem(
                "is_palindrome_mirror",
                """theorem is_palindrome_mirror (s : String) :
    is_palindrome (String.mk (s.toList ++ s.toList.reverse)) = true""",
                "by\n  sorry",
                proof_incomplete=True,
            ),
        ]
    if name == "count_char":
        return [
            theorem(
                "count_char_eq_filter_length",
                """theorem count_char_eq_filter_length (s : String) (c : Char) :
    count_char s c = (s.toList.filter (fun ch => ch == c)).length""",
                "by\n  rfl",
            ),
            theorem(
                "count_char_append",
                """theorem count_char_append (s t : String) (c : Char) :
    count_char (s ++ t) c = count_char s c + count_char t c""",
                "by\n  sorry",
                proof_incomplete=True,
            ),
            theorem(
                "count_char_zero_of_no_match",
                """theorem count_char_zero_of_no_match (s : String) (c : Char)
    (h : ∀ ch ∈ s.toList, ch ≠ c) : count_char s c = 0""",
                "by\n  sorry",
                proof_incomplete=True,
            ),
        ]
    if name == "to_upper":
        return [
            theorem(
                "to_upper_toList",
                "theorem to_upper_toList (s : String) : (to_upper s).toList = s.toList.map upperChar",
                "by\n  simp [to_upper]",
            ),
            theorem(
                "to_upper_length",
                "theorem to_upper_length (s : String) : (to_upper s).toList.length = s.toList.length",
                "by\n  simp [to_upper]",
            ),
            theorem(
                "to_upper_idempotent",
                "theorem to_upper_idempotent (s : String) : to_upper (to_upper s) = to_upper s",
                "by\n  sorry",
                proof_incomplete=True,
            ),
        ]
    if name == "to_lower":
        return [
            theorem(
                "to_lower_toList",
                "theorem to_lower_toList (s : String) : (to_lower s).toList = s.toList.map lowerChar",
                "by\n  simp [to_lower]",
            ),
            theorem(
                "to_lower_length",
                "theorem to_lower_length (s : String) : (to_lower s).toList.length = s.toList.length",
                "by\n  simp [to_lower]",
            ),
            theorem(
                "to_lower_idempotent",
                "theorem to_lower_idempotent (s : String) : to_lower (to_lower s) = to_lower s",
                "by\n  sorry",
                proof_incomplete=True,
            ),
        ]
    if name == "char_is_digit":
        return [
            theorem(
                "char_is_digit_iff",
                """theorem char_is_digit_iff (c : Char) :
    char_is_digit c = true ↔ '0'.toNat ≤ c.toNat ∧ c.toNat ≤ '9'.toNat""",
                "by\n  simp [char_is_digit]",
            ),
            theorem(
                "char_is_digit_false_outside_range",
                """theorem char_is_digit_false_outside_range (c : Char)
    (h : c.toNat < '0'.toNat ∨ '9'.toNat < c.toNat) : char_is_digit c = false""",
                "by\n  sorry",
                proof_incomplete=True,
            ),
        ]
    return [
        theorem(
            "char_is_alpha_iff",
            """theorem char_is_alpha_iff (c : Char) :
    char_is_alpha c = true ↔ (('a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat) ∨ ('A'.toNat ≤ c.toNat ∧ c.toNat ≤ 'Z'.toNat))""",
            "by\n  simp [char_is_alpha]",
        ),
        theorem(
            "char_is_alpha_false_outside_ranges",
            """theorem char_is_alpha_false_outside_ranges (c : Char)
    (h : ('a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat) = False)
    (h' : ('A'.toNat ≤ c.toNat ∧ c.toNat ≤ 'Z'.toNat) = False) :
    char_is_alpha c = false""",
            "by\n  sorry",
            proof_incomplete=True,
        ),
    ]


def build_record(lang: str, name: str) -> dict:
    return {
        "language": lang,
        "source": get_c_source(name) if lang == "C" else get_py_source(name),
        "lean_translation": get_lean_translation(name, lang),
        "tests": get_c_tests(name) if lang == "C" else get_py_tests(name),
        "lean_tests": get_lean_tests(name, lang),
        "theorems": get_theorems(name, lang),
        "deps_fully_translated": [],
        "axiomatized_deps": [],
        "skip_reason": None,
    }


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for lang in ["C", "Python"]:
        for name in FUNCTIONS:
            records.append(build_record(lang, name))

    with OUTPUT_PATH.open("w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")

    print(f"Wrote {len(records)} records to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
