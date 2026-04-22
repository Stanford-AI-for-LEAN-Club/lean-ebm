import json
import os

def get_c_source(name):
    sources = {
        "sum_array": "int sum_array(const int *arr, int n) {\n    int s = 0;\n    for (int i = 0; i < n; i++) {\n        s += arr[i];\n    }\n    return s;\n}",
        "product_array": "int product_array(const int *arr, int n) {\n    int p = 1;\n    for (int i = 0; i < n; i++) {\n        p *= arr[i];\n    }\n    return p;\n}",
        "max_element": "int max_element(const int *arr, int n) {\n    int m = arr[0];\n    for (int i = 1; i < n; i++) {\n        if (arr[i] > m) m = arr[i];\n    }\n    return m;\n}",
        "min_element": "int min_element(const int *arr, int n) {\n    int m = arr[0];\n    for (int i = 1; i < n; i++) {\n        if (arr[i] < m) m = arr[i];\n    }\n    return m;\n}",
        "reverse_array": "void reverse_array(int *arr, int n) {\n    for (int i = 0; i < n / 2; i++) {\n        int tmp = arr[i];\n        arr[i] = arr[n - 1 - i];\n        arr[n - 1 - i] = tmp;\n    }\n}",
        "is_sorted": "int is_sorted(const int *arr, int n) {\n    for (int i = 0; i < n - 1; i++) {\n        if (arr[i] > arr[i + 1]) return 0;\n    }\n    return 1;\n}",
        "count_occurrences": "int count_occurrences(const int *arr, int n, int val) {\n    int c = 0;\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == val) c++;\n    }\n    return c;\n}"
    }
    return sources[name]

def get_py_source(name):
    sources = {
        "sum_array": "def sum_array(arr: list[int]) -> int:\n    s = 0\n    for x in arr:\n        s += x\n    return s",
        "product_array": "def product_array(arr: list[int]) -> int:\n    p = 1\n    for x in arr:\n        p *= x\n    return p",
        "max_element": "def max_element(arr: list[int]) -> int:\n    m = arr[0]\n    for i in range(1, len(arr)):\n        if arr[i] > m:\n            m = arr[i]\n    return m",
        "min_element": "def min_element(arr: list[int]) -> int:\n    m = arr[0]\n    for i in range(1, len(arr)):\n        if arr[i] < m:\n            m = arr[i]\n    return m",
        "reverse_array": "def reverse_array(arr: list[int]) -> list[int]:\n    result = arr[:]\n    n = len(result)\n    for i in range(n // 2):\n        result[i], result[n - 1 - i] = result[n - 1 - i], result[i]\n    return result",
        "is_sorted": "def is_sorted(arr: list[int]) -> bool:\n    for i in range(len(arr) - 1):\n        if arr[i] > arr[i + 1]:\n            return False\n    return True",
        "count_occurrences": "def count_occurrences(arr: list[int], val: int) -> int:\n    c = 0\n    for x in arr:\n        if x == val:\n            c += 1\n    return c"
    }
    return sources[name]

def get_lean_translation(name, lang):
    if lang == "C":
        translations = {
            "sum_array": "def sum_array (arr : Array Int) : Int :=\n  arr.foldl (· + ·) 0",
            "product_array": "def product_array (arr : Array Int) : Int :=\n  arr.foldl (· * ·) 1",
            "max_element": "def max_element (arr : Array Int) : Int :=\n  if h : arr.size > 0 then\n    arr.foldl (init := arr[0]) (f := fun acc x => if x > acc then x else acc)\n  else 0",
            "min_element": "def min_element (arr : Array Int) : Int :=\n  if h : arr.size > 0 then\n    arr.foldl (init := arr[0]) (f := fun acc x => if x < acc then x else acc)\n  else 0",
            "reverse_array": "def reverse_array (arr : Array Int) : Array Int :=\n  arr.reverse",
            "is_sorted": "def is_sorted (arr : Array Int) : Bool :=\n  let n := arr.size\n  if n < 2 then true\n  else\n    Id.run do\n      for i in [0:n - 1] do\n        if arr[i] > arr[i + 1] then\n          return false\n      return true",
            "count_occurrences": "def count_occurrences (arr : Array Int) (val : Int) : Nat :=\n  arr.foldl (fun acc x => if x == val then acc + 1 else acc) 0"
        }
    else: # Python -> List Int
        translations = {
            "sum_array": "def sum_array (arr : List Int) : Int :=\n  arr.foldl (· + ·) 0",
            "product_array": "def product_array (arr : List Int) : Int :=\n  arr.foldl (· * ·) 1",
            "max_element": "def max_element (arr : List Int) : Int :=\n  match arr with\n  | [] => 0\n  | x :: xs => xs.foldl (fun acc y => if y > acc then y else acc) x",
            "min_element": "def min_element (arr : List Int) : Int :=\n  match arr with\n  | [] => 0\n  | x :: xs => xs.foldl (fun acc y => if y < acc then y else acc) x",
            "reverse_array": "def reverse_array (arr : List Int) : List Int :=\n  arr.reverse",
            "is_sorted": "def is_sorted (arr : List Int) : Bool :=\n  match arr with\n  | [] => true\n  | [_] => true\n  | x :: y :: rest => if x > y then false else is_sorted (y :: rest)",
            "count_occurrences": "def count_occurrences (arr : List Int) (val : Int) : Nat :=\n  arr.foldl (fun acc x => if x == val then acc + 1 else acc) 0"
        }
    return translations[name]

def get_c_tests(name):
    source = get_c_source(name)
    main = ""
    if name == "sum_array":
        main = "int main() { int a[] = {1, 2, 3, 4, 5}; assert(sum_array(a, 5) == 15); int b[] = {10, -5, 2}; assert(sum_array(b, 3) == 7); return 0; }"
    elif name == "product_array":
        main = "int main() { int a[] = {1, 2, 3, 4}; assert(product_array(a, 4) == 24); int b[] = {5, 0, 10}; assert(product_array(b, 3) == 0); return 0; }"
    elif name == "max_element":
        main = "int main() { int a[] = {1, 5, 3, 2}; assert(max_element(a, 4) == 5); int b[] = {-10, -5, -20}; assert(max_element(b, 3) == -5); return 0; }"
    elif name == "min_element":
        main = "int main() { int a[] = {1, 5, 3, 2}; assert(min_element(a, 4) == 1); int b[] = {-10, -5, -20}; assert(min_element(b, 3) == -20); return 0; }"
    elif name == "reverse_array":
        main = "int main() { int a[] = {1, 2, 3, 4}; reverse_array(a, 4); assert(a[0] == 4 && a[1] == 3 && a[2] == 2 && a[3] == 1); return 0; }"
    elif name == "is_sorted":
        main = "int main() { int a[] = {1, 2, 3, 4}; assert(is_sorted(a, 4) == 1); int b[] = {1, 3, 2, 4}; assert(is_sorted(b, 4) == 0); return 0; }"
    elif name == "count_occurrences":
        main = "int main() { int a[] = {1, 2, 1, 3, 1}; assert(count_occurrences(a, 5, 1) == 3); assert(count_occurrences(a, 5, 4) == 0); return 0; }"
    return f"#include <assert.h>\n{source}\n{main}"

def get_py_tests(name):
    source = get_py_source(name)
    tests = ""
    if name == "sum_array":
        tests = "assert sum_array([1, 2, 3, 4, 5]) == 15\nassert sum_array([10, -5, 2]) == 7"
    elif name == "product_array":
        tests = "assert product_array([1, 2, 3, 4]) == 24\nassert product_array([5, 0, 10]) == 0"
    elif name == "max_element":
        tests = "assert max_element([1, 5, 3, 2]) == 5\nassert max_element([-10, -5, -20]) == -5"
    elif name == "min_element":
        tests = "assert min_element([1, 5, 3, 2]) == 1\nassert min_element([-10, -5, -20]) == -20"
    elif name == "reverse_array":
        tests = "assert reverse_array([1, 2, 3, 4]) == [4, 3, 2, 1]"
    elif name == "is_sorted":
        tests = "assert is_sorted([1, 2, 3, 4]) == True\nassert is_sorted([1, 3, 2, 4]) == False"
    elif name == "count_occurrences":
        tests = "assert count_occurrences([1, 2, 1, 3, 1], 1) == 3\nassert count_occurrences([1, 2, 1, 3, 1], 4) == 0"
    return f"{source}\n{tests}"

def get_lean_tests(name):
    if name == "sum_array":
        return "#eval sum_array #[1, 2, 3, 4, 5]\n#eval sum_array [10, -5, 2]"
    elif name == "product_array":
        return "#eval product_array #[1, 2, 3, 4]\n#eval product_array [5, 0, 10]"
    elif name == "max_element":
        return "#eval max_element #[1, 5, 3, 2]\n#eval max_element [-10, -5, -20]"
    elif name == "min_element":
        return "#eval min_element #[1, 5, 3, 2]\n#eval min_element [-10, -5, -20]"
    elif name == "reverse_array":
        return "#eval reverse_array #[1, 2, 3, 4]\n#eval reverse_array [1, 2, 3, 4]"
    elif name == "is_sorted":
        return "#eval is_sorted #[1, 2, 3, 4]\n#eval is_sorted [1, 3, 2, 4]"
    elif name == "count_occurrences":
        return "#eval count_occurrences #[1, 2, 1, 3, 1] 1\n#eval count_occurrences [1, 2, 1, 3, 1] 4"

def get_theorems(name, lang):
    t_type = "Array Int" if lang == "C" else "List Int"
    rev_call = "arr.reverse" if lang == "C" else "arr.reverse"
    size_call = "arr.size" if lang == "C" else "arr.length"
    
    if name == "sum_array":
        return [
            {"name": "sum_array_append", "statement": f"theorem sum_array_append (arr1 arr2 : {t_type}) : sum_array (arr1 ++ arr2) = sum_array arr1 + sum_array arr2", "proof": "by sorry", "proof_incomplete": True},
            {"name": "sum_array_rev", "statement": f"theorem sum_array_rev (arr : {t_type}) : sum_array {rev_call} = sum_array arr", "proof": "by sorry", "proof_incomplete": True}
        ]
    elif name == "product_array":
        return [
            {"name": "product_array_append", "statement": f"theorem product_array_append (arr1 arr2 : {t_type}) : product_array (arr1 ++ arr2) = product_array arr1 * product_array arr2", "proof": "by sorry", "proof_incomplete": True},
            {"name": "product_array_rev", "statement": f"theorem product_array_rev (arr : {t_type}) : product_array {rev_call} = product_array arr", "proof": "by sorry", "proof_incomplete": True}
        ]
    elif name == "max_element":
        if lang == "C":
            return [
                {"name": "max_element_ge", "statement": f"theorem max_element_ge (arr : Array Int) (i : Fin arr.size) : arr.size > 0 → arr[i] ≤ max_element arr", "proof": "by sorry", "proof_incomplete": True},
                {"name": "max_element_mem", "statement": f"theorem max_element_mem (arr : Array Int) : arr.size > 0 → ∃ i : Fin arr.size, arr[i] = max_element arr", "proof": "by sorry", "proof_incomplete": True}
            ]
        else:
            return [
                {"name": "max_element_ge", "statement": f"theorem max_element_ge (arr : List Int) (x : Int) : x ∈ arr → x ≤ max_element arr", "proof": "by sorry", "proof_incomplete": True},
                {"name": "max_element_mem", "statement": f"theorem max_element_mem (arr : List Int) : arr ≠ [] → max_element arr ∈ arr", "proof": "by sorry", "proof_incomplete": True}
            ]
    elif name == "min_element":
        if lang == "C":
            return [
                {"name": "min_element_le", "statement": f"theorem min_element_le (arr : Array Int) (i : Fin arr.size) : arr.size > 0 → arr[i] ≥ min_element arr", "proof": "by sorry", "proof_incomplete": True},
                {"name": "min_element_mem", "statement": f"theorem min_element_mem (arr : Array Int) : arr.size > 0 → ∃ i : Fin arr.size, arr[i] = min_element arr", "proof": "by sorry", "proof_incomplete": True}
            ]
        else:
            return [
                {"name": "min_element_le", "statement": f"theorem min_element_le (arr : List Int) (x : Int) : x ∈ arr → x ≥ min_element arr", "proof": "by sorry", "proof_incomplete": True},
                {"name": "min_element_mem", "statement": f"theorem min_element_mem (arr : List Int) : arr ≠ [] → min_element arr ∈ arr", "proof": "by sorry", "proof_incomplete": True}
            ]
    elif name == "reverse_array":
        return [
            {"name": "reverse_array_length", "statement": f"theorem reverse_array_length (arr : {t_type}) : ({size_call} (reverse_array arr)) = {size_call} arr", "proof": "by sorry", "proof_incomplete": True},
            {"name": "reverse_array_involution", "statement": f"theorem reverse_array_involution (arr : {t_type}) : reverse_array (reverse_array arr) = arr", "proof": "by sorry", "proof_incomplete": True}
        ]
    elif name == "is_sorted":
        if lang == "C":
            return [
                {"name": "is_sorted_iff", "statement": "theorem is_sorted_iff (arr : Array Int) : is_sorted arr = true ↔ ∀ i j : Fin arr.size, i < j → arr[i] ≤ arr[j]", "proof": "by sorry", "proof_incomplete": True},
                {"name": "is_sorted_empty", "statement": "theorem is_sorted_empty : is_sorted #[] = true", "proof": "by rfl", "proof_incomplete": False}
            ]
        else:
            return [
                {"name": "is_sorted_empty", "statement": "theorem is_sorted_empty : is_sorted [] = true", "proof": "by rfl", "proof_incomplete": False},
                {"name": "is_sorted_cons", "statement": "theorem is_sorted_cons (x y : Int) (rest : List Int) : is_sorted (x :: y :: rest) = (x ≤ y ∧ is_sorted (y :: rest))", "proof": "by sorry", "proof_incomplete": True}
            ]
    elif name == "count_occurrences":
        return [
            {"name": "count_occurrences_le_size", "statement": f"theorem count_occurrences_le_size (arr : {t_type}) (val : Int) : count_occurrences arr val ≤ {size_call} arr", "proof": "by sorry", "proof_incomplete": True},
            {"name": "count_occurrences_append", "statement": f"theorem count_occurrences_append (arr1 arr2 : {t_type}) (val : Int) : count_occurrences (arr1 ++ arr2) val = count_occurrences arr1 val + count_occurrences arr2 val", "proof": "by sorry", "proof_incomplete": True}
        ]
    return []

functions = ["sum_array", "product_array", "max_element", "min_element", "reverse_array", "is_sorted", "count_occurrences"]

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch03_array_ops.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    for lang in ["C", "Python"]:
        for name in functions:
            record = {
                "language": lang,
                "source": get_c_source(name) if lang == "C" else get_py_source(name),
                "lean_translation": get_lean_translation(name, lang),
                "tests": get_c_tests(name) if lang == "C" else get_py_tests(name),
                "lean_tests": get_lean_tests(name),
                "theorems": get_theorems(name, lang),
                "deps_fully_translated": [],
                "axiomatized_deps": [],
                "skip_reason": None
            }
            f.write(json.dumps(record) + "\n")
