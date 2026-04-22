"""Generate JSONL for batch03_array_ops: sum, product, max, min, reverse, is_sorted, count_occurrences."""
import json, os

FUNCTIONS = ["sum_array", "product_array", "max_element", "min_element", "reverse_array", "is_sorted", "count_occurrences"]

C_SOURCES = {
    "sum_array": "int sum_array(const int *arr, int n) {\n    int s = 0;\n    for (int i = 0; i < n; i++) {\n        s += arr[i];\n    }\n    return s;\n}",
    "product_array": "int product_array(const int *arr, int n) {\n    int p = 1;\n    for (int i = 0; i < n; i++) {\n        p *= arr[i];\n    }\n    return p;\n}",
    "max_element": "int max_element(const int *arr, int n) {\n    int m = arr[0];\n    for (int i = 1; i < n; i++) {\n        if (arr[i] > m) m = arr[i];\n    }\n    return m;\n}",
    "min_element": "int min_element(const int *arr, int n) {\n    int m = arr[0];\n    for (int i = 1; i < n; i++) {\n        if (arr[i] < m) m = arr[i];\n    }\n    return m;\n}",
    "reverse_array": "void reverse_array(int *arr, int n) {\n    for (int i = 0; i < n / 2; i++) {\n        int tmp = arr[i];\n        arr[i] = arr[n - 1 - i];\n        arr[n - 1 - i] = tmp;\n    }\n}",
    "is_sorted": "int is_sorted(const int *arr, int n) {\n    for (int i = 0; i < n - 1; i++) {\n        if (arr[i] > arr[i + 1]) return 0;\n    }\n    return 1;\n}",
    "count_occurrences": "int count_occurrences(const int *arr, int n, int val) {\n    int c = 0;\n    for (int i = 0; i < n; i++) {\n        if (arr[i] == val) c++;\n    }\n    return c;\n}",
}

PY_SOURCES = {
    "sum_array": "def sum_array(arr: list[int]) -> int:\n    s = 0\n    for x in arr:\n        s += x\n    return s",
    "product_array": "def product_array(arr: list[int]) -> int:\n    p = 1\n    for x in arr:\n        p *= x\n    return p",
    "max_element": "def max_element(arr: list[int]) -> int:\n    m = arr[0]\n    for i in range(1, len(arr)):\n        if arr[i] > m:\n            m = arr[i]\n    return m",
    "min_element": "def min_element(arr: list[int]) -> int:\n    m = arr[0]\n    for i in range(1, len(arr)):\n        if arr[i] < m:\n            m = arr[i]\n    return m",
    "reverse_array": "def reverse_array(arr: list[int]) -> list[int]:\n    result = arr[:]\n    n = len(result)\n    for i in range(n // 2):\n        result[i], result[n - 1 - i] = result[n - 1 - i], result[i]\n    return result",
    "is_sorted": "def is_sorted(arr: list[int]) -> bool:\n    for i in range(len(arr) - 1):\n        if arr[i] > arr[i + 1]:\n            return False\n    return True",
    "count_occurrences": "def count_occurrences(arr: list[int], val: int) -> int:\n    c = 0\n    for x in arr:\n        if x == val:\n            c += 1\n    return c",
}

LEAN = {
    "sum_array": "def sum_array (arr : List Int) : Int :=\n  arr.foldl (· + ·) 0",
    "product_array": "def product_array (arr : List Int) : Int :=\n  arr.foldl (· * ·) 1",
    "max_element": "def max_element (arr : List Int) : Int :=\n  match arr with\n  | [] => 0\n  | x :: xs => xs.foldl (fun m a => if a > m then a else m) x",
    "min_element": "def min_element (arr : List Int) : Int :=\n  match arr with\n  | [] => 0\n  | x :: xs => xs.foldl (fun m a => if a < m then a else m) x",
    "reverse_array": "def reverse_array (arr : List Int) : List Int :=\n  arr.reverse",
    "is_sorted": "def is_sorted (arr : List Int) : Bool :=\n  match arr with\n  | [] => true\n  | [_] => true\n  | x :: y :: rest => decide (x ≤ y) && is_sorted (y :: rest)",
    "count_occurrences": "def count_occurrences (arr : List Int) (val : Int) : Nat :=\n  arr.filter (· == val) |>.length",
}

C_TESTS = {
    "sum_array": '#include <assert.h>\nint sum_array(const int *arr, int n) { int s=0; for(int i=0;i<n;i++) s+=arr[i]; return s; }\nint main() { int a[]={1,-2,3,4}; assert(sum_array(a,4)==6); assert(sum_array(a,0)==0); int b[]={5}; assert(sum_array(b,1)==5); return 0; }',
    "product_array": '#include <assert.h>\nint product_array(const int *arr, int n) { int p=1; for(int i=0;i<n;i++) p*=arr[i]; return p; }\nint main() { int a[]={2,-3,4}; assert(product_array(a,3)==-24); assert(product_array(a,0)==1); return 0; }',
    "max_element": '#include <assert.h>\nint max_element(const int *arr, int n) { int m=arr[0]; for(int i=1;i<n;i++) if(arr[i]>m) m=arr[i]; return m; }\nint main() { int a[]={1,9,3,7}; assert(max_element(a,4)==9); int b[]={-5,-2,-10}; assert(max_element(b,3)==-2); return 0; }',
    "min_element": '#include <assert.h>\nint min_element(const int *arr, int n) { int m=arr[0]; for(int i=1;i<n;i++) if(arr[i]<m) m=arr[i]; return m; }\nint main() { int a[]={1,9,3,7}; assert(min_element(a,4)==1); int b[]={-5,-2,-10}; assert(min_element(b,3)==-10); return 0; }',
    "reverse_array": '#include <assert.h>\nvoid reverse_array(int *arr, int n) { for(int i=0;i<n/2;i++) { int t=arr[i]; arr[i]=arr[n-1-i]; arr[n-1-i]=t; } }\nint main() { int a[]={1,2,3,4}; reverse_array(a,4); assert(a[0]==4 && a[1]==3 && a[2]==2 && a[3]==1); return 0; }',
    "is_sorted": '#include <assert.h>\nint is_sorted(const int *arr, int n) { for(int i=0;i<n-1;i++) if(arr[i]>arr[i+1]) return 0; return 1; }\nint main() { int a[]={1,2,2,5}; assert(is_sorted(a,4)==1); int b[]={3,1,2}; assert(is_sorted(b,3)==0); return 0; }',
    "count_occurrences": '#include <assert.h>\nint count_occurrences(const int *arr, int n, int val) { int c=0; for(int i=0;i<n;i++) if(arr[i]==val) c++; return c; }\nint main() { int a[]={1,2,1,3,1}; assert(count_occurrences(a,5,1)==3); assert(count_occurrences(a,5,4)==0); return 0; }',
}

PY_TESTS = {
    "sum_array": "def sum_array(arr):\n    s=0\n    for x in arr: s+=x\n    return s\nassert sum_array([])==0\nassert sum_array([1,-2,3,4])==6\nassert sum_array([5])==5",
    "product_array": "def product_array(arr):\n    p=1\n    for x in arr: p*=x\n    return p\nassert product_array([])==1\nassert product_array([2,-3,4])==-24",
    "max_element": "def max_element(arr):\n    m=arr[0]\n    for i in range(1,len(arr)):\n        if arr[i]>m: m=arr[i]\n    return m\nassert max_element([1,9,3,7])==9\nassert max_element([-5,-2,-10])==-2",
    "min_element": "def min_element(arr):\n    m=arr[0]\n    for i in range(1,len(arr)):\n        if arr[i]<m: m=arr[i]\n    return m\nassert min_element([1,9,3,7])==1\nassert min_element([-5,-2,-10])==-10",
    "reverse_array": "def reverse_array(arr):\n    r=arr[:]; n=len(r)\n    for i in range(n//2): r[i],r[n-1-i]=r[n-1-i],r[i]\n    return r\nassert reverse_array([])==[]\nassert reverse_array([1,2,3,4])==[4,3,2,1]",
    "is_sorted": "def is_sorted(arr):\n    for i in range(len(arr)-1):\n        if arr[i]>arr[i+1]: return False\n    return True\nassert is_sorted([])\nassert is_sorted([1,2,2,5])\nassert not is_sorted([3,1,2])",
    "count_occurrences": "def count_occurrences(arr, val):\n    c=0\n    for x in arr:\n        if x==val: c+=1\n    return c\nassert count_occurrences([],5)==0\nassert count_occurrences([1,2,1,3,1],1)==3\nassert count_occurrences([1,2,3],4)==0",
}

LEAN_TESTS = {
    "sum_array": "#eval sum_array []  -- 0\n#eval sum_array [1, -2, 3, 4]  -- 6",
    "product_array": "#eval product_array []  -- 1\n#eval product_array [2, -3, 4]  -- -24",
    "max_element": "#eval max_element [1, 9, 3, 7]  -- 9\n#eval max_element [-5, -2, -10]  -- -2",
    "min_element": "#eval min_element [1, 9, 3, 7]  -- 1\n#eval min_element [-5, -2, -10]  -- -10",
    "reverse_array": "#eval reverse_array []  -- []\n#eval reverse_array [1, 2, 3, 4]  -- [4, 3, 2, 1]",
    "is_sorted": "#eval is_sorted ([] : List Int)  -- true\n#eval is_sorted [1, 2, 2, 5]  -- true\n#eval is_sorted [3, 1, 2]  -- false",
    "count_occurrences": "#eval count_occurrences [] 5  -- 0\n#eval count_occurrences [1, 2, 1, 3, 1] 1  -- 3",
}

THEOREMS = {
    "sum_array": [
        {"name": "sum_array_nil", "statement": "theorem sum_array_nil : sum_array [] = 0", "proof": "by simp [sum_array, List.foldl]", "proof_incomplete": False},
        {"name": "sum_array_cons", "statement": "theorem sum_array_cons (x : Int) (xs : List Int) : sum_array (x :: xs) = x + sum_array xs", "proof": "by sorry", "proof_incomplete": True},
        {"name": "sum_array_append", "statement": "theorem sum_array_append (a b : List Int) : sum_array (a ++ b) = sum_array a + sum_array b", "proof": "by sorry", "proof_incomplete": True},
    ],
    "product_array": [
        {"name": "product_array_nil", "statement": "theorem product_array_nil : product_array [] = 1", "proof": "by simp [product_array, List.foldl]", "proof_incomplete": False},
        {"name": "product_array_cons", "statement": "theorem product_array_cons (x : Int) (xs : List Int) : product_array (x :: xs) = x * product_array xs", "proof": "by sorry", "proof_incomplete": True},
        {"name": "product_array_append", "statement": "theorem product_array_append (a b : List Int) : product_array (a ++ b) = product_array a * product_array b", "proof": "by sorry", "proof_incomplete": True},
    ],
    "max_element": [
        {"name": "max_element_mem", "statement": "theorem max_element_mem (arr : List Int) (h : arr ≠ []) : max_element arr ∈ arr", "proof": "by sorry", "proof_incomplete": True},
        {"name": "max_element_ge_all", "statement": "theorem max_element_ge_all (arr : List Int) (h : arr ≠ []) : ∀ x ∈ arr, x ≤ max_element arr", "proof": "by sorry", "proof_incomplete": True},
        {"name": "max_element_singleton", "statement": "theorem max_element_singleton (x : Int) : max_element [x] = x", "proof": "by simp [max_element, List.foldl]", "proof_incomplete": False},
    ],
    "min_element": [
        {"name": "min_element_mem", "statement": "theorem min_element_mem (arr : List Int) (h : arr ≠ []) : min_element arr ∈ arr", "proof": "by sorry", "proof_incomplete": True},
        {"name": "min_element_le_all", "statement": "theorem min_element_le_all (arr : List Int) (h : arr ≠ []) : ∀ x ∈ arr, min_element arr ≤ x", "proof": "by sorry", "proof_incomplete": True},
        {"name": "min_element_singleton", "statement": "theorem min_element_singleton (x : Int) : min_element [x] = x", "proof": "by simp [min_element, List.foldl]", "proof_incomplete": False},
    ],
    "reverse_array": [
        {"name": "reverse_array_length", "statement": "theorem reverse_array_length (arr : List Int) : (reverse_array arr).length = arr.length", "proof": "by simp [reverse_array]", "proof_incomplete": False},
        {"name": "reverse_array_involution", "statement": "theorem reverse_array_involution (arr : List Int) : reverse_array (reverse_array arr) = arr", "proof": "by simp [reverse_array]", "proof_incomplete": False},
        {"name": "reverse_array_nil", "statement": "theorem reverse_array_nil : reverse_array [] = []", "proof": "by simp [reverse_array]", "proof_incomplete": False},
    ],
    "is_sorted": [
        {"name": "is_sorted_nil", "statement": "theorem is_sorted_nil : is_sorted ([] : List Int) = true", "proof": "by simp [is_sorted]", "proof_incomplete": False},
        {"name": "is_sorted_singleton", "statement": "theorem is_sorted_singleton (x : Int) : is_sorted [x] = true", "proof": "by simp [is_sorted]", "proof_incomplete": False},
        {"name": "is_sorted_cons_le", "statement": "theorem is_sorted_cons_le (x y : Int) (rest : List Int) : is_sorted (x :: y :: rest) = true → x ≤ y", "proof": "by sorry", "proof_incomplete": True},
    ],
    "count_occurrences": [
        {"name": "count_occurrences_nil", "statement": "theorem count_occurrences_nil (val : Int) : count_occurrences [] val = 0", "proof": "by simp [count_occurrences, List.filter]", "proof_incomplete": False},
        {"name": "count_occurrences_le_length", "statement": "theorem count_occurrences_le_length (arr : List Int) (val : Int) : count_occurrences arr val ≤ arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "count_occurrences_append", "statement": "theorem count_occurrences_append (a b : List Int) (val : Int) : count_occurrences (a ++ b) val = count_occurrences a val + count_occurrences b val", "proof": "by sorry", "proof_incomplete": True},
    ],
}

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch03_array_ops.jsonl"
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
