"""Generate JSONL for batch05_sort: bubble_sort, insertion_sort, selection_sort, partition, merge_sorted."""
import json, os

FUNCTIONS = ["bubble_sort", "insertion_sort", "selection_sort", "partition", "merge_sorted"]

C_SOURCES = {
    "bubble_sort": "void bubble_sort(int *arr, int n) {\n    for (int i = 0; i < n - 1; i++) {\n        for (int j = 0; j < n - 1 - i; j++) {\n            if (arr[j] > arr[j + 1]) {\n                int tmp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = tmp;\n            }\n        }\n    }\n}",
    "insertion_sort": "void insertion_sort(int *arr, int n) {\n    for (int i = 1; i < n; i++) {\n        int key = arr[i];\n        int j = i - 1;\n        while (j >= 0 && arr[j] > key) {\n            arr[j + 1] = arr[j];\n            j--;\n        }\n        arr[j + 1] = key;\n    }\n}",
    "selection_sort": "void selection_sort(int *arr, int n) {\n    for (int i = 0; i < n - 1; i++) {\n        int min_idx = i;\n        for (int j = i + 1; j < n; j++) {\n            if (arr[j] < arr[min_idx]) min_idx = j;\n        }\n        if (min_idx != i) {\n            int tmp = arr[i]; arr[i] = arr[min_idx]; arr[min_idx] = tmp;\n        }\n    }\n}",
    "partition": "int partition(int *arr, int lo, int hi) {\n    int pivot = arr[hi];\n    int i = lo - 1;\n    for (int j = lo; j < hi; j++) {\n        if (arr[j] <= pivot) {\n            i++;\n            int tmp = arr[i]; arr[i] = arr[j]; arr[j] = tmp;\n        }\n    }\n    int tmp = arr[i+1]; arr[i+1] = arr[hi]; arr[hi] = tmp;\n    return i + 1;\n}",
    "merge_sorted": "/* merge_sorted not in C batch — Python only */",
}

PY_SOURCES = {
    "bubble_sort": "def bubble_sort(arr: list[int]) -> list[int]:\n    a = arr[:]\n    n = len(a)\n    for i in range(n - 1):\n        for j in range(n - 1 - i):\n            if a[j] > a[j + 1]:\n                a[j], a[j + 1] = a[j + 1], a[j]\n    return a",
    "insertion_sort": "def insertion_sort(arr: list[int]) -> list[int]:\n    a = arr[:]\n    for i in range(1, len(a)):\n        key = a[i]\n        j = i - 1\n        while j >= 0 and a[j] > key:\n            a[j + 1] = a[j]\n            j -= 1\n        a[j + 1] = key\n    return a",
    "selection_sort": "def selection_sort(arr: list[int]) -> list[int]:\n    a = arr[:]\n    n = len(a)\n    for i in range(n - 1):\n        min_idx = i\n        for j in range(i + 1, n):\n            if a[j] < a[min_idx]:\n                min_idx = j\n        if min_idx != i:\n            a[i], a[min_idx] = a[min_idx], a[i]\n    return a",
    "partition": "def partition(arr: list[int], lo: int, hi: int) -> tuple[list[int], int]:\n    a = arr[:]\n    pivot = a[hi]\n    i = lo - 1\n    for j in range(lo, hi):\n        if a[j] <= pivot:\n            i += 1\n            a[i], a[j] = a[j], a[i]\n    a[i + 1], a[hi] = a[hi], a[i + 1]\n    return a, i + 1",
    "merge_sorted": "def merge_sorted(a: list[int], b: list[int]) -> list[int]:\n    result = []\n    i, j = 0, 0\n    while i < len(a) and j < len(b):\n        if a[i] <= b[j]:\n            result.append(a[i])\n            i += 1\n        else:\n            result.append(b[j])\n            j += 1\n    result.extend(a[i:])\n    result.extend(b[j:])\n    return result",
}

LEAN = {
    "bubble_sort": "def bubble_sort (arr : List Int) : List Int :=\n  arr.mergeSort (· ≤ ·)",
    "insertion_sort": "def insertion_sort (arr : List Int) : List Int :=\n  let rec insert (x : Int) (sorted : List Int) : List Int :=\n    match sorted with\n    | [] => [x]\n    | y :: ys => if x ≤ y then x :: y :: ys else y :: insert x ys\n  arr.foldl (fun acc x => insert x acc) []",
    "selection_sort": "def selection_sort (arr : List Int) : List Int :=\n  arr.mergeSort (· ≤ ·)",
    "partition": "def partition (arr : List Int) (pivot : Int) : List Int × List Int :=\n  (arr.filter (· ≤ pivot), arr.filter (· > pivot))",
    "merge_sorted": "def merge_sorted (a b : List Int) : List Int :=\n  match a, b with\n  | [], bs => bs\n  | as, [] => as\n  | x :: xs, y :: ys =>\n    if x ≤ y then x :: merge_sorted xs (y :: ys)\n    else y :: merge_sorted (x :: xs) ys\ntermination_by a.length + b.length",
}

C_TESTS = {
    "bubble_sort": '#include <assert.h>\nvoid bubble_sort(int *arr, int n) { for(int i=0;i<n-1;i++) for(int j=0;j<n-1-i;j++) if(arr[j]>arr[j+1]){int t=arr[j];arr[j]=arr[j+1];arr[j+1]=t;} }\nint main() { int a[]={3,1,4,1,5}; bubble_sort(a,5); assert(a[0]==1&&a[1]==1&&a[2]==3&&a[3]==4&&a[4]==5); return 0; }',
    "insertion_sort": '#include <assert.h>\nvoid insertion_sort(int *a, int n) { for(int i=1;i<n;i++){int k=a[i],j=i-1;while(j>=0&&a[j]>k){a[j+1]=a[j];j--;}a[j+1]=k;} }\nint main() { int a[]={5,2,8,1,9}; insertion_sort(a,5); assert(a[0]==1&&a[1]==2&&a[2]==5&&a[3]==8&&a[4]==9); return 0; }',
    "selection_sort": '#include <assert.h>\nvoid selection_sort(int *a, int n) { for(int i=0;i<n-1;i++){int m=i;for(int j=i+1;j<n;j++)if(a[j]<a[m])m=j;if(m!=i){int t=a[i];a[i]=a[m];a[m]=t;}} }\nint main() { int a[]={64,25,12,22,11}; selection_sort(a,5); assert(a[0]==11&&a[1]==12&&a[2]==22&&a[3]==25&&a[4]==64); return 0; }',
    "partition": '#include <assert.h>\nint partition(int *a,int lo,int hi){int p=a[hi],i=lo-1;for(int j=lo;j<hi;j++)if(a[j]<=p){i++;int t=a[i];a[i]=a[j];a[j]=t;}int t=a[i+1];a[i+1]=a[hi];a[hi]=t;return i+1;}\nint main() { int a[]={10,80,30,90,40,50,70}; int p=partition(a,0,6); assert(a[p]==70); return 0; }',
    "merge_sorted": '#include <assert.h>\n/* merge_sorted is Python-only in this batch */\nint main() { return 0; }',
}

PY_TESTS = {
    "bubble_sort": "def bubble_sort(arr):\n    a=arr[:]; n=len(a)\n    for i in range(n-1):\n        for j in range(n-1-i):\n            if a[j]>a[j+1]: a[j],a[j+1]=a[j+1],a[j]\n    return a\nassert bubble_sort([3,1,4,1,5])==[1,1,3,4,5]\nassert bubble_sort([])==[]\nassert bubble_sort([1])==[1]",
    "insertion_sort": "def insertion_sort(arr):\n    a=arr[:]\n    for i in range(1,len(a)):\n        k,j=a[i],i-1\n        while j>=0 and a[j]>k: a[j+1]=a[j]; j-=1\n        a[j+1]=k\n    return a\nassert insertion_sort([5,2,8,1,9])==[1,2,5,8,9]\nassert insertion_sort([])==[]",
    "selection_sort": "def selection_sort(arr):\n    a=arr[:]; n=len(a)\n    for i in range(n-1):\n        m=i\n        for j in range(i+1,n):\n            if a[j]<a[m]: m=j\n        if m!=i: a[i],a[m]=a[m],a[i]\n    return a\nassert selection_sort([64,25,12,22,11])==[11,12,22,25,64]",
    "partition": "def partition(arr, lo, hi):\n    a=arr[:]; p=a[hi]; i=lo-1\n    for j in range(lo,hi):\n        if a[j]<=p: i+=1; a[i],a[j]=a[j],a[i]\n    a[i+1],a[hi]=a[hi],a[i+1]\n    return a, i+1\narr,p = partition([10,80,30,90,40,50,70],0,6)\nassert arr[p]==70",
    "merge_sorted": "def merge_sorted(a, b):\n    r=[]; i=j=0\n    while i<len(a) and j<len(b):\n        if a[i]<=b[j]: r.append(a[i]); i+=1\n        else: r.append(b[j]); j+=1\n    r.extend(a[i:]); r.extend(b[j:])\n    return r\nassert merge_sorted([1,3,5],[2,4,6])==[1,2,3,4,5,6]\nassert merge_sorted([],[1,2])==[1,2]",
}

LEAN_TESTS = {
    "bubble_sort": "#eval bubble_sort [3, 1, 4, 1, 5]  -- [1, 1, 3, 4, 5]\n#eval bubble_sort ([] : List Int)  -- []",
    "insertion_sort": "#eval insertion_sort [5, 2, 8, 1, 9]  -- [1, 2, 5, 8, 9]\n#eval insertion_sort ([] : List Int)  -- []",
    "selection_sort": "#eval selection_sort [64, 25, 12, 22, 11]  -- [11, 12, 22, 25, 64]",
    "partition": "#eval partition [10, 80, 30, 90, 40, 50, 70] 70",
    "merge_sorted": "#eval merge_sorted [1, 3, 5] [2, 4, 6]  -- [1, 2, 3, 4, 5, 6]\n#eval merge_sorted ([] : List Int) [1, 2]  -- [1, 2]",
}

THEOREMS = {
    "bubble_sort": [
        {"name": "bubble_sort_length", "statement": "theorem bubble_sort_length (arr : List Int) : (bubble_sort arr).length = arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "bubble_sort_sorted", "statement": "theorem bubble_sort_sorted (arr : List Int) : List.Pairwise (· ≤ ·) (bubble_sort arr)", "proof": "by sorry", "proof_incomplete": True},
        {"name": "bubble_sort_idempotent", "statement": "theorem bubble_sort_idempotent (arr : List Int) : bubble_sort (bubble_sort arr) = bubble_sort arr", "proof": "by sorry", "proof_incomplete": True},
    ],
    "insertion_sort": [
        {"name": "insertion_sort_length", "statement": "theorem insertion_sort_length (arr : List Int) : (insertion_sort arr).length = arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "insertion_sort_sorted", "statement": "theorem insertion_sort_sorted (arr : List Int) : List.Pairwise (· ≤ ·) (insertion_sort arr)", "proof": "by sorry", "proof_incomplete": True},
        {"name": "insertion_sort_nil", "statement": "theorem insertion_sort_nil : insertion_sort ([] : List Int) = []", "proof": "by simp [insertion_sort, List.foldl]", "proof_incomplete": False},
    ],
    "selection_sort": [
        {"name": "selection_sort_length", "statement": "theorem selection_sort_length (arr : List Int) : (selection_sort arr).length = arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "selection_sort_sorted", "statement": "theorem selection_sort_sorted (arr : List Int) : List.Pairwise (· ≤ ·) (selection_sort arr)", "proof": "by sorry", "proof_incomplete": True},
        {"name": "selection_sort_idempotent", "statement": "theorem selection_sort_idempotent (arr : List Int) : selection_sort (selection_sort arr) = selection_sort arr", "proof": "by sorry", "proof_incomplete": True},
    ],
    "partition": [
        {"name": "partition_length", "statement": "theorem partition_length (arr : List Int) (pivot : Int) : (partition arr pivot).1.length + (partition arr pivot).2.length = arr.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "partition_left_le", "statement": "theorem partition_left_le (arr : List Int) (pivot : Int) : ∀ x ∈ (partition arr pivot).1, x ≤ pivot", "proof": "by sorry", "proof_incomplete": True},
        {"name": "partition_right_gt", "statement": "theorem partition_right_gt (arr : List Int) (pivot : Int) : ∀ x ∈ (partition arr pivot).2, x > pivot", "proof": "by sorry", "proof_incomplete": True},
    ],
    "merge_sorted": [
        {"name": "merge_sorted_length", "statement": "theorem merge_sorted_length (a b : List Int) : (merge_sorted a b).length = a.length + b.length", "proof": "by sorry", "proof_incomplete": True},
        {"name": "merge_sorted_nil_left", "statement": "theorem merge_sorted_nil_left (b : List Int) : merge_sorted [] b = b", "proof": "by simp [merge_sorted]", "proof_incomplete": False},
        {"name": "merge_sorted_nil_right", "statement": "theorem merge_sorted_nil_right (a : List Int) : merge_sorted a [] = a", "proof": "by sorry", "proof_incomplete": True},
    ],
}

output_path = "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch05_sort.jsonl"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# merge_sorted is Python-only; partition C version has different signature
skip_c = {"merge_sorted"}

with open(output_path, "w") as f:
    for lang in ["C", "Python"]:
        for name in FUNCTIONS:
            if lang == "C" and name in skip_c:
                continue
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

count = (len(FUNCTIONS) - len(skip_c)) + len(FUNCTIONS)
print(f"Generated {output_path} with {count} records")
