"""Generate JSONL for batch04_search: linear_search, binary_search, find_first, find_last, contains, index_of_max."""
import json, os

FUNCTIONS = ["linear_search", "binary_search", "find_first", "find_last", "contains", "index_of_max"]

C_SOURCES = {
    "linear_search": "int linear_search(const int *arr, int n, int target) {\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == target) return i;\n    }\n    return -1;\n}",
    "binary_search": "int binary_search(const int *arr, int n, int target) {\n    int lo = 0, hi = n - 1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (arr[mid] == target) return mid;\n        if (arr[mid] < target) lo = mid + 1;\n        else hi = mid - 1;\n    }\n    return -1;\n}",
    "find_first": "int find_first(const int *arr, int n, int target) {\n    int lo = 0, hi = n - 1, result = -1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (arr[mid] == target) { result = mid; hi = mid - 1; }\n        else if (arr[mid] < target) lo = mid + 1;\n        else hi = mid - 1;\n    }\n    return result;\n}",
    "find_last": "int find_last(const int *arr, int n, int target) {\n    int lo = 0, hi = n - 1, result = -1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (arr[mid] == target) { result = mid; lo = mid + 1; }\n        else if (arr[mid] < target) lo = mid + 1;\n        else hi = mid - 1;\n    }\n    return result;\n}",
    "contains": "int contains(const int *arr, int n, int val) {\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == val) return 1;\n    }\n    return 0;\n}",
    "index_of_max": "int index_of_max(const int *arr, int n) {\n    int idx = 0;\n    for (int i = 1; i < n; i++) {\n        if (arr[i] > arr[idx]) idx = i;\n    }\n    return idx;\n}",
}

PY_SOURCES = {
    "linear_search": "def linear_search(arr: list[int], target: int) -> int:\n    for i in range(len(arr)):\n        if arr[i] == target:\n            return i\n    return -1",
    "binary_search": "def binary_search(arr: list[int], target: int) -> int:\n    lo, hi = 0, len(arr) - 1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target: return mid\n        if arr[mid] < target: lo = mid + 1\n        else: hi = mid - 1\n    return -1",
    "find_first": "def find_first(arr: list[int], target: int) -> int:\n    lo, hi, result = 0, len(arr) - 1, -1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target: result = mid; hi = mid - 1\n        elif arr[mid] < target: lo = mid + 1\n        else: hi = mid - 1\n    return result",
    "find_last": "def find_last(arr: list[int], target: int) -> int:\n    lo, hi, result = 0, len(arr) - 1, -1\n    while lo <= hi:\n        mid = lo + (hi - lo) // 2\n        if arr[mid] == target: result = mid; lo = mid + 1\n        elif arr[mid] < target: lo = mid + 1\n        else: hi = mid - 1\n    return result",
    "contains": "def contains(arr: list[int], val: int) -> bool:\n    for x in arr:\n        if x == val:\n            return True\n    return False",
    "index_of_max": "def index_of_max(arr: list[int]) -> int:\n    idx = 0\n    for i in range(1, len(arr)):\n        if arr[i] > arr[idx]:\n            idx = i\n    return idx",
}

LEAN = {
    "linear_search": {
        "C": "def linear_search (arr : List Int) (target : Int) : Int :=\n  match arr.indexOf? target with\n  | some i => i\n  | none => -1",
        "Python": "def linear_search (arr : List Int) (target : Int) : Int :=\n  match arr.indexOf? target with\n  | some i => i\n  | none => -1",
    },
    "binary_search": {
        "C": "partial def binary_search (arr : List Int) (target : Int) : Int :=\n  let rec loop (lo hi : Int) : Int :=\n    if lo > hi then -1\n    else\n      let mid := lo + (hi - lo) / 2\n      match arr.get? mid.toNat with\n      | some x =>\n        if x == target then mid\n        else if x < target then loop (mid + 1) hi\n        else loop lo (mid - 1)\n      | none => -1\n  loop 0 (arr.length - 1)",
        "Python": "partial def binary_search (arr : List Int) (target : Int) : Int :=\n  let rec loop (lo hi : Int) : Int :=\n    if lo > hi then -1\n    else\n      let mid := lo + (hi - lo) / 2\n      match arr.get? mid.toNat with\n      | some x =>\n        if x == target then mid\n        else if x < target then loop (mid + 1) hi\n        else loop lo (mid - 1)\n      | none => -1\n  loop 0 (arr.length - 1)",
    },
    "find_first": {
        "C": "partial def find_first (arr : List Int) (target : Int) : Int :=\n  let rec loop (lo hi result : Int) : Int :=\n    if lo > hi then result\n    else\n      let mid := lo + (hi - lo) / 2\n      match arr.get? mid.toNat with\n      | some x =>\n        if x == target then loop lo (mid - 1) mid\n        else if x < target then loop (mid + 1) hi result\n        else loop lo (mid - 1) result\n      | none => result\n  loop 0 (arr.length - 1) (-1)",
        "Python": "partial def find_first (arr : List Int) (target : Int) : Int :=\n  let rec loop (lo hi result : Int) : Int :=\n    if lo > hi then result\n    else\n      let mid := lo + (hi - lo) / 2\n      match arr.get? mid.toNat with\n      | some x =>\n        if x == target then loop lo (mid - 1) mid\n        else if x < target then loop (mid + 1) hi result\n        else loop lo (mid - 1) result\n      | none => result\n  loop 0 (arr.length - 1) (-1)",
    },
    "find_last": {
        "C": "partial def find_last (arr : List Int) (target : Int) : Int :=\n  let rec loop (lo hi result : Int) : Int :=\n    if lo > hi then result\n    else\n      let mid := lo + (hi - lo) / 2\n      match arr.get? mid.toNat with\n      | some x =>\n        if x == target then loop (mid + 1) hi mid\n        else if x < target then loop (mid + 1) hi result\n        else loop lo (mid - 1) result\n      | none => result\n  loop 0 (arr.length - 1) (-1)",
        "Python": "partial def find_last (arr : List Int) (target : Int) : Int :=\n  let rec loop (lo hi result : Int) : Int :=\n    if lo > hi then result\n    else\n      let mid := lo + (hi - lo) / 2\n      match arr.get? mid.toNat with\n      | some x =>\n        if x == target then loop (mid + 1) hi mid\n        else if x < target then loop (mid + 1) hi result\n        else loop lo (mid - 1) result\n      | none => result\n  loop 0 (arr.length - 1) (-1)",
    },
    "contains": {
        "C": "def contains (arr : List Int) (val : Int) : Bool :=\n  arr.any (· == val)",
        "Python": "def contains (arr : List Int) (val : Int) : Bool :=\n  arr.any (· == val)",
    },
    "index_of_max": {
        "C": "def index_of_max (arr : List Int) : Nat :=\n  match arr with\n  | [] => 0\n  | _ => Id.run do\n    let mut idx := 0\n    for i in [:arr.length] do\n      if arr[i]! > arr[idx]! then idx := i\n    return idx",
        "Python": "def index_of_max (arr : List Int) : Nat :=\n  match arr with\n  | [] => 0\n  | _ => Id.run do\n    let mut idx := 0\n    for i in [:arr.length] do\n      if arr[i]! > arr[idx]! then idx := i\n    return idx",
    },
}

C_TESTS = {
    "linear_search": '#include <assert.h>\nint linear_search(const int *arr, int n, int target) { for(int i=0;i<n;i++) if(arr[i]==target) return i; return -1; }\nint main() { int a[]={1,3,5,7,9}; assert(linear_search(a,5,5)==2); assert(linear_search(a,5,10)==-1); assert(linear_search(a,5,1)==0); return 0; }',
    "binary_search": '#include <assert.h>\nint binary_search(const int *arr, int n, int target) { int lo=0,hi=n-1; while(lo<=hi) { int mid=lo+(hi-lo)/2; if(arr[mid]==target) return mid; if(arr[mid]<target) lo=mid+1; else hi=mid-1; } return -1; }\nint main() { int a[]={1,3,5,7,9}; assert(binary_search(a,5,5)==2); assert(binary_search(a,5,4)==-1); return 0; }',
    "find_first": '#include <assert.h>\nint find_first(const int *a, int n, int t) { int lo=0,hi=n-1,r=-1; while(lo<=hi) { int m=lo+(hi-lo)/2; if(a[m]==t){r=m;hi=m-1;} else if(a[m]<t) lo=m+1; else hi=m-1; } return r; }\nint main() { int a[]={1,2,2,2,3}; assert(find_first(a,5,2)==1); assert(find_first(a,5,4)==-1); return 0; }',
    "find_last": '#include <assert.h>\nint find_last(const int *a, int n, int t) { int lo=0,hi=n-1,r=-1; while(lo<=hi) { int m=lo+(hi-lo)/2; if(a[m]==t){r=m;lo=m+1;} else if(a[m]<t) lo=m+1; else hi=m-1; } return r; }\nint main() { int a[]={1,2,2,2,3}; assert(find_last(a,5,2)==3); assert(find_last(a,5,4)==-1); return 0; }',
    "contains": '#include <assert.h>\nint contains(const int *a, int n, int v) { for(int i=0;i<n;i++) if(a[i]==v) return 1; return 0; }\nint main() { int a[]={1,2,3}; assert(contains(a,3,2)==1); assert(contains(a,3,4)==0); return 0; }',
    "index_of_max": '#include <assert.h>\nint index_of_max(const int *a, int n) { int idx=0; for(int i=1;i<n;i++) if(a[i]>a[idx]) idx=i; return idx; }\nint main() { int a[]={1,5,3,7,2}; assert(index_of_max(a,5)==3); int b[]={10,2,3}; assert(index_of_max(b,3)==0); return 0; }',
}

PY_TESTS = {
    "linear_search": "def linear_search(arr, target):\n    for i in range(len(arr)):\n        if arr[i]==target: return i\n    return -1\nassert linear_search([1,3,5,7,9],5)==2\nassert linear_search([1,3,5,7,9],10)==-1",
    "binary_search": "def binary_search(arr, target):\n    lo,hi=0,len(arr)-1\n    while lo<=hi:\n        mid=lo+(hi-lo)//2\n        if arr[mid]==target: return mid\n        if arr[mid]<target: lo=mid+1\n        else: hi=mid-1\n    return -1\nassert binary_search([1,3,5,7,9],5)==2\nassert binary_search([1,3,5,7,9],4)==-1",
    "find_first": "def find_first(arr, target):\n    lo,hi,r=0,len(arr)-1,-1\n    while lo<=hi:\n        m=lo+(hi-lo)//2\n        if arr[m]==target: r=m; hi=m-1\n        elif arr[m]<target: lo=m+1\n        else: hi=m-1\n    return r\nassert find_first([1,2,2,2,3],2)==1\nassert find_first([1,2,2,2,3],4)==-1",
    "find_last": "def find_last(arr, target):\n    lo,hi,r=0,len(arr)-1,-1\n    while lo<=hi:\n        m=lo+(hi-lo)//2\n        if arr[m]==target: r=m; lo=m+1\n        elif arr[m]<target: lo=m+1\n        else: hi=m-1\n    return r\nassert find_last([1,2,2,2,3],2)==3\nassert find_last([1,2,2,2,3],4)==-1",
    "contains": "def contains(arr, val):\n    for x in arr:\n        if x==val: return True\n    return False\nassert contains([1,2,3],2)\nassert not contains([1,2,3],4)",
    "index_of_max": "def index_of_max(arr):\n    idx=0\n    for i in range(1,len(arr)):\n        if arr[i]>arr[idx]: idx=i\n    return idx\nassert index_of_max([1,5,3,7,2])==3\nassert index_of_max([10,2,3])==0",
}

LEAN_TESTS = {
    "linear_search": "#eval linear_search [1,3,5,7,9] 5  -- 2\n#eval linear_search [1,3,5,7,9] 10  -- -1",
    "binary_search": "#eval binary_search [1,3,5,7,9] 5  -- 2\n#eval binary_search [1,3,5,7,9] 4  -- -1",
    "find_first": "#eval find_first [1,2,2,2,3] 2  -- 1\n#eval find_first [1,2,2,2,3] 4  -- -1",
    "find_last": "#eval find_last [1,2,2,2,3] 2  -- 3\n#eval find_last [1,2,2,2,3] 4  -- -1",
    "contains": "#eval contains [1,2,3] 2  -- true\n#eval contains [1,2,3] 4  -- false",
    "index_of_max": "#eval index_of_max [1,5,3,7,2]  -- 3\n#eval index_of_max [10,2,3]  -- 0",
}

THEOREMS = {
    "linear_search": [
        {"name": "linear_search_not_found", "statement": "theorem linear_search_not_found (arr : List Int) (target : Int) : linear_search arr target = -1 → target ∉ arr", "proof": "by sorry", "proof_incomplete": True},
        {"name": "linear_search_found_valid", "statement": "theorem linear_search_found_valid (arr : List Int) (target : Int) (h : linear_search arr target ≠ -1) : 0 ≤ linear_search arr target ∧ linear_search arr target < arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "linear_search_nil", "statement": "theorem linear_search_nil (target : Int) : linear_search [] target = -1", "proof": "by simp [linear_search]", "proof_incomplete": False},
    ],
    "binary_search": [
        {"name": "binary_search_found_valid", "statement": "theorem binary_search_found_valid (arr : List Int) (target : Int) (h : binary_search arr target ≠ -1) : 0 ≤ binary_search arr target ∧ binary_search arr target < arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "binary_search_nil", "statement": "theorem binary_search_nil (target : Int) : binary_search [] target = -1", "proof": "by sorry", "proof_incomplete": True},
        {"name": "binary_search_found_eq", "statement": "theorem binary_search_found_eq (arr : List Int) (target : Int) (h : binary_search arr target ≠ -1) : arr.get? (binary_search arr target).toNat = some target", "proof": "by sorry", "proof_incomplete": True},
    ],
    "find_first": [
        {"name": "find_first_le_find_last", "statement": "theorem find_first_le_find_last (arr : List Int) (target : Int) : find_first arr target ≤ find_last arr target ∨ find_first arr target = -1", "proof": "by sorry", "proof_incomplete": True},
        {"name": "find_first_is_first", "statement": "theorem find_first_is_first (arr : List Int) (target : Int) (i : Nat) : find_first arr target ≠ -1 → (i : Int) < find_first arr target → 0 ≤ i → arr.get? i.toNat ≠ some target", "proof": "by sorry", "proof_incomplete": True},
    ],
    "find_last": [
        {"name": "find_last_is_last", "statement": "theorem find_last_is_last (arr : List Int) (target : Int) (i : Int) : find_last arr target ≠ -1 → find_last arr target < i → i < arr.length → arr.get? i.toNat ≠ some target", "proof": "by sorry", "proof_incomplete": True},
        {"name": "find_last_found_eq", "statement": "theorem find_last_found_eq (arr : List Int) (target : Int) (h : find_last arr target ≠ -1) : arr.get? (find_last arr target).toNat = some target", "proof": "by sorry", "proof_incomplete": True},
    ],
    "contains": [
        {"name": "contains_iff_mem", "statement": "theorem contains_iff_mem (arr : List Int) (val : Int) : contains arr val = true ↔ val ∈ arr", "proof": "by sorry", "proof_incomplete": True},
        {"name": "contains_nil", "statement": "theorem contains_nil (val : Int) : contains [] val = false", "proof": "by simp [contains, List.any]", "proof_incomplete": False},
        {"name": "contains_cons_self", "statement": "theorem contains_cons_self (val : Int) (xs : List Int) : contains (val :: xs) val = true", "proof": "by sorry", "proof_incomplete": True},
    ],
    "index_of_max": [
        {"name": "index_of_max_valid", "statement": "theorem index_of_max_valid (arr : List Int) (h : arr ≠ []) : index_of_max arr < arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "index_of_max_ge_all", "statement": "theorem index_of_max_ge_all (arr : List Int) (h : arr ≠ []) : ∀ x ∈ arr, x ≤ arr.get! (index_of_max arr)", "proof": "by sorry", "proof_incomplete": True},
    ],
}

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch04_search.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, "w") as f:
    for lang in ["C", "Python"]:
        for name in FUNCTIONS:
            record = {
                "language": lang,
                "source": C_SOURCES[name] if lang == "C" else PY_SOURCES[name],
                "lean_translation": LEAN[name][lang],
                "tests": C_TESTS[name] if lang == "C" else PY_TESTS[name],
                "lean_tests": LEAN_TESTS[name],
                "theorems": THEOREMS[name],
                "deps_fully_translated": [],
                "axiomatized_deps": [],
                "skip_reason": None,
            }
            f.write(json.dumps(record) + "\n")

print(f"Generated {output_path} with {len(FUNCTIONS) * 2} records")
