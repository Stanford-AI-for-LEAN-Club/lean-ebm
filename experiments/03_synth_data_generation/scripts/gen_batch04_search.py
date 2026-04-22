import json
import os

def get_c_source(name):
    sources = {
        "linear_search": "int linear_search(const int *arr, int n, int target) {\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == target) return i;\n    }\n    return -1;\n}",
        "binary_search": "int binary_search(const int *arr, int n, int target) {\n    int lo = 0, hi = n - 1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (arr[mid] == target) return mid;\n        if (arr[mid] < target) lo = mid + 1;\n        else hi = mid - 1;\n    }\n    return -1;\n}",
        "find_first": "int find_first(const int *arr, int n, int target) {\n    int lo = 0, hi = n - 1, result = -1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (arr[mid] == target) {\n            result = mid;\n            hi = mid - 1;\n        } else if (arr[mid] < target) {\n            lo = mid + 1;\n        } else {\n            hi = mid - 1;\n        }\n    }\n    return result;\n}",
        "find_last": "int find_last(const int *arr, int n, int target) {\n    int lo = 0, hi = n - 1, result = -1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (arr[mid] == target) {\n            result = mid;\n            lo = mid + 1;\n        } else if (arr[mid] < target) {\n            lo = mid + 1;\n        } else {\n            hi = mid - 1;\n        }\n    }\n    return result;\n}",
        "contains": "int contains(const int *arr, int n, int val) {\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == val) return 1;\n    }\n    return 0;\n}",
        "index_of_max": "int index_of_max(const int *arr, int n) {\n    int idx = 0;\n    for (int i = 1; i < n; i++) {\n        if (arr[i] > arr[idx]) idx = i;\n    }\n    return idx;\n}"
    }
    return sources[name]

def get_py_source(name):
    sources = {
        "linear_search": "def linear_search(arr: list[int], target: int) -> int:\n    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n    return -1",
        "binary_search": "def binary_search(arr: list[int], target: int) -> int:\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target:\n            return mid\n        if arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
        "find_first": "def find_first(arr: list[int], target: int) -> int:\n    lo, hi, result = 0, len(arr) - 1, -1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target:\n            result = mid\n            hi = mid - 1\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return result",
        "find_last": "def find_last(arr: list[int], target: int) -> int:\n    lo, hi, result = 0, len(arr) - 1, -1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target:\n            result = mid\n            lo = mid + 1\n        elif arr[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return result",
        "contains": "def contains(arr: list[int], val: int) -> bool:\n    for x in arr:\n        if x == val:\n            return True\n    return False",
        "index_of_max": "def index_of_max(arr: list[int]) -> int:\n    idx = 0\n    for i in range(1, len(arr)):\n        if arr[i] > arr[idx]:\n            idx = i\n    return idx"
    }
    return sources[name]

def get_lean_translation(name, lang):
    translations = {
        "linear_search": "def linear_search (arr : Array Int) (target : Int) : Int :=\n  match arr.findIdx? (· == target) with\n  | some i => i\n  | none => -1",
        "binary_search": "partial def binary_search (arr : Array Int) (target : Int) : Int :=\n  let rec loop (lo hi : Int) : Int :=\n    if lo > hi then -1\n    else\n      let mid := lo + (hi - lo) / 2\n      if mid < 0 || mid >= arr.size then -1\n      else\n        let val := arr.get! mid.toNat\n        if val == target then mid\n        else if val < target then loop (mid + 1) hi\n        else loop lo (mid - 1)\n  loop 0 (arr.size - 1)",
        "find_first": "partial def find_first (arr : Array Int) (target : Int) : Int :=\n  let rec loop (lo hi : Int) (res : Int) : Int :=\n    if lo > hi then res\n    else\n      let mid := lo + (hi - lo) / 2\n      if mid < 0 || mid >= arr.size then res\n      else\n        let val := arr.get! mid.toNat\n        if val == target then loop lo (mid - 1) mid\n        else if val < target then loop (mid + 1) hi res\n        else loop lo (mid - 1) res\n  loop 0 (arr.size - 1) (-1)",
        "find_last": "partial def find_last (arr : Array Int) (target : Int) : Int :=\n  let rec loop (lo hi : Int) (res : Int) : Int :=\n    if lo > hi then res\n    else\n      let mid := lo + (hi - lo) / 2\n      if mid < 0 || mid >= arr.size then res\n      else\n        let val := arr.get! mid.toNat\n        if val == target then loop (mid + 1) hi mid\n        else if val < target then loop (mid + 1) hi res\n        else loop lo (mid - 1) res\n  loop 0 (arr.size - 1) (-1)",
        "contains": "def contains (arr : Array Int) (val : Int) : Bool :=\n  arr.contains val",
        "index_of_max": "def index_of_max (arr : Array Int) : Int :=\n  if arr.isEmpty then 0\n  else\n    let rec loop (i maxIdx : Nat) : Nat :=\n      if h : i < arr.size then\n        if arr.get! i > arr.get! maxIdx then loop (i + 1) i\n        else loop (i + 1) maxIdx\n      else maxIdx\n    termination_by arr.size - i\n    loop 1 0"
    }
    return translations[name]

def get_c_tests(name):
    source = get_c_source(name)
    main = ""
    if name == "linear_search":
        main = "int main() {\n    int arr[] = {1, 3, 5, 7, 9};\n    assert(linear_search(arr, 5, 5) == 2);\n    assert(linear_search(arr, 5, 1) == 0);\n    assert(linear_search(arr, 5, 9) == 4);\n    assert(linear_search(arr, 5, 2) == -1);\n    return 0;\n}"
    elif name == "binary_search":
        main = "int main() {\n    int arr[] = {1, 3, 5, 7, 9};\n    assert(binary_search(arr, 5, 5) == 2);\n    assert(binary_search(arr, 5, 1) == 0);\n    assert(binary_search(arr, 5, 9) == 4);\n    assert(binary_search(arr, 5, 2) == -1);\n    return 0;\n}"
    elif name == "find_first":
        main = "int main() {\n    int arr[] = {1, 3, 3, 3, 9};\n    assert(find_first(arr, 5, 3) == 1);\n    assert(find_first(arr, 5, 1) == 0);\n    assert(find_first(arr, 5, 9) == 4);\n    assert(find_first(arr, 5, 2) == -1);\n    return 0;\n}"
    elif name == "find_last":
        main = "int main() {\n    int arr[] = {1, 3, 3, 3, 9};\n    assert(find_last(arr, 5, 3) == 3);\n    assert(find_last(arr, 5, 1) == 0);\n    assert(find_last(arr, 5, 9) == 4);\n    assert(find_last(arr, 5, 2) == -1);\n    return 0;\n}"
    elif name == "contains":
        main = "int main() {\n    int arr[] = {1, 3, 5, 7, 9};\n    assert(contains(arr, 5, 5) == 1);\n    assert(contains(arr, 5, 2) == 0);\n    return 0;\n}"
    elif name == "index_of_max":
        main = "int main() {\n    int arr[] = {1, 3, 9, 7, 5};\n    assert(index_of_max(arr, 5) == 2);\n    int arr2[] = {10, 3, 9, 7, 5};\n    assert(index_of_max(arr2, 5) == 0);\n    return 0;\n}"
    return f"#include <assert.h>\n{source}\n{main}"

def get_py_tests(name):
    source = get_py_source(name)
    tests = ""
    if name == "linear_search":
        tests = "assert linear_search([1, 3, 5, 7, 9], 5) == 2\nassert linear_search([1, 3, 5, 7, 9], 1) == 0\nassert linear_search([1, 3, 5, 7, 9], 9) == 4\nassert linear_search([1, 3, 5, 7, 9], 2) == -1"
    elif name == "binary_search":
        tests = "assert binary_search([1, 3, 5, 7, 9], 5) == 2\nassert binary_search([1, 3, 5, 7, 9], 1) == 0\nassert binary_search([1, 3, 5, 7, 9], 9) == 4\nassert binary_search([1, 3, 5, 7, 9], 2) == -1"
    elif name == "find_first":
        tests = "assert find_first([1, 3, 3, 3, 9], 3) == 1\nassert find_first([1, 3, 3, 3, 9], 1) == 0\nassert find_first([1, 3, 3, 3, 9], 9) == 4\nassert find_first([1, 3, 3, 3, 9], 2) == -1"
    elif name == "find_last":
        tests = "assert find_last([1, 3, 3, 3, 9], 3) == 3\nassert find_last([1, 3, 3, 3, 9], 1) == 0\nassert find_last([1, 3, 3, 3, 9], 9) == 4\nassert find_last([1, 3, 3, 3, 9], 2) == -1"
    elif name == "contains":
        tests = "assert contains([1, 3, 5, 7, 9], 5) == True\nassert contains([1, 3, 5, 7, 9], 2) == False"
    elif name == "index_of_max":
        tests = "assert index_of_max([1, 3, 9, 7, 5]) == 2\nassert index_of_max([10, 3, 9, 7, 5]) == 0"
    return f"{source}\n{tests}"

def get_lean_tests(name, lang):
    if name == "linear_search":
        return "#eval linear_search #[1, 3, 5, 7, 9] 5\n#eval linear_search #[1, 3, 5, 7, 9] 2"
    elif name == "binary_search":
        return "#eval binary_search #[1, 3, 5, 7, 9] 5\n#eval binary_search #[1, 3, 5, 7, 9] 2"
    elif name == "find_first":
        return "#eval find_first #[1, 3, 3, 3, 9] 3\n#eval find_first #[1, 3, 3, 3, 9] 2"
    elif name == "find_last":
        return "#eval find_last #[1, 3, 3, 3, 9] 3\n#eval find_last #[1, 3, 3, 3, 9] 2"
    elif name == "contains":
        return "#eval contains #[1, 3, 5, 7, 9] 5\n#eval contains #[1, 3, 5, 7, 9] 2"
    elif name == "index_of_max":
        return "#eval index_of_max #[1, 3, 9, 7, 5]\n#eval index_of_max #[10, 3, 9, 7, 5]"

def get_theorems(name, lang):
    if name == "linear_search":
        return [
            {"name": "linear_search_found", "statement": "theorem linear_search_found (arr : Array Int) (target : Int) (i : Int) :\n  linear_search arr target = i ∧ i ≥ 0 → arr.get! i.toNat = target", "proof": "by sorry", "proof_incomplete": True},
            {"name": "linear_search_not_found", "statement": "theorem linear_search_not_found (arr : Array Int) (target : Int) :\n  linear_search arr target = -1 → ∀ x ∈ arr, x ≠ target", "proof": "by sorry", "proof_incomplete": True},
            {"name": "linear_search_first", "statement": "theorem linear_search_first (arr : Array Int) (target : Int) (i : Int) :\n  linear_search arr target = i ∧ i ≥ 0 → ∀ j : Nat, j < i.toNat → arr.get! j ≠ target", "proof": "by sorry", "proof_incomplete": True}
        ]
    elif name == "binary_search":
        return [
            {"name": "binary_search_found", "statement": "theorem binary_search_found (arr : Array Int) (target : Int) (i : Int) :\n  (List.Sorted (· ≤ ·) arr.toList) ∧ binary_search arr target = i ∧ i ≥ 0 → arr.get! i.toNat = target", "proof": "by sorry", "proof_incomplete": True},
            {"name": "binary_search_not_found", "statement": "theorem binary_search_not_found (arr : Array Int) (target : Int) :\n  (List.Sorted (· ≤ ·) arr.toList) ∧ binary_search arr target = -1 → ∀ x ∈ arr, x ≠ target", "proof": "by sorry", "proof_incomplete": True}
        ]
    elif name == "find_first":
        return [
            {"name": "find_first_found", "statement": "theorem find_first_found (arr : Array Int) (target : Int) (i : Int) :\n  (List.Sorted (· ≤ ·) arr.toList) ∧ find_first arr target = i ∧ i ≥ 0 → arr.get! i.toNat = target", "proof": "by sorry", "proof_incomplete": True},
            {"name": "find_first_is_first", "statement": "theorem find_first_is_first (arr : Array Int) (target : Int) (i : Int) :\n  (List.Sorted (· ≤ ·) arr.toList) ∧ find_first arr target = i ∧ i ≥ 0 → ∀ j : Nat, j < i.toNat → arr.get! j ≠ target", "proof": "by sorry", "proof_incomplete": True}
        ]
    elif name == "find_last":
        return [
            {"name": "find_last_found", "statement": "theorem find_last_found (arr : Array Int) (target : Int) (i : Int) :\n  (List.Sorted (· ≤ ·) arr.toList) ∧ find_last arr target = i ∧ i ≥ 0 → arr.get! i.toNat = target", "proof": "by sorry", "proof_incomplete": True},
            {"name": "find_last_is_last", "statement": "theorem find_last_is_last (arr : Array Int) (target : Int) (i : Int) :\n  (List.Sorted (· ≤ ·) arr.toList) ∧ find_last arr target = i ∧ i ≥ 0 → ∀ j : Nat, i.toNat < j ∧ j < arr.size → arr.get! j ≠ target", "proof": "by sorry", "proof_incomplete": True}
        ]
    elif name == "contains":
        return [
            {"name": "contains_iff_mem", "statement": "theorem contains_iff_mem (arr : Array Int) (val : Int) :\n  contains arr val = true ↔ val ∈ arr", "proof": "by\n  unfold contains\n  simp [Array.contains, Array.any, Array.foldl]\n  sorry", "proof_incomplete": True}
        ]
    elif name == "index_of_max":
        return [
            {"name": "index_of_max_is_max", "statement": "theorem index_of_max_is_max (arr : Array Int) :\n  arr.size > 0 → ∀ x ∈ arr, x ≤ arr.get! (index_of_max arr).toNat", "proof": "by sorry", "proof_incomplete": True},
            {"name": "index_of_max_in_bounds", "statement": "theorem index_of_max_in_bounds (arr : Array Int) :\n  arr.size > 0 → (index_of_max arr) ≥ 0 ∧ (index_of_max arr) < arr.size", "proof": "by sorry", "proof_incomplete": True}
        ]
    return []

functions = ["linear_search", "binary_search", "find_first", "find_last", "contains", "index_of_max"]

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch04_search.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    for lang in ["C", "Python"]:
        for name in functions:
            record = {
                "language": lang,
                "source": get_c_source(name) if lang == "C" else get_py_source(name),
                "lean_translation": get_lean_translation(name, lang),
                "tests": get_c_tests(name) if lang == "C" else get_py_tests(name),
                "lean_tests": get_lean_tests(name, lang),
                "theorems": get_theorems(name, lang),
                "deps_fully_translated": [],
                "axiomatized_deps": [],
                "skip_reason": None
            }
            f.write(json.dumps(record) + "\n")

print(f"Generated {output_path}")
