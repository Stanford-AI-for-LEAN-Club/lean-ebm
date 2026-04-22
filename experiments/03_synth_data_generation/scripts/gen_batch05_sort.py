import json
from pathlib import Path
from textwrap import dedent


def block(text: str) -> str:
    return dedent(text).strip()


def thm(name: str, statement: str, proof: str, proof_incomplete: bool) -> dict:
    return {
        "name": name,
        "statement": statement,
        "proof": proof,
        "proof_incomplete": proof_incomplete,
    }


def get_c_source(name: str) -> str:
    sources = {
        "swap": block(
            """
            void swap(int *a, int *b) {
                int tmp = *a;
                *a = *b;
                *b = tmp;
            }
            """
        ),
        "bubble_sort": block(
            """
            void bubble_sort(int *arr, int n) {
                for (int i = 0; i < n - 1; i++) {
                    for (int j = 0; j < n - 1 - i; j++) {
                        if (arr[j] > arr[j + 1]) {
                            swap(&arr[j], &arr[j + 1]);
                        }
                    }
                }
            }
            """
        ),
        "insertion_sort": block(
            """
            void insertion_sort(int *arr, int n) {
                for (int i = 1; i < n; i++) {
                    int key = arr[i];
                    int j = i - 1;
                    while (j >= 0 && arr[j] > key) {
                        arr[j + 1] = arr[j];
                        j--;
                    }
                    arr[j + 1] = key;
                }
            }
            """
        ),
        "selection_sort": block(
            """
            void selection_sort(int *arr, int n) {
                for (int i = 0; i < n - 1; i++) {
                    int min_idx = i;
                    for (int j = i + 1; j < n; j++) {
                        if (arr[j] < arr[min_idx]) {
                            min_idx = j;
                        }
                    }
                    if (min_idx != i) {
                        swap(&arr[i], &arr[min_idx]);
                    }
                }
            }
            """
        ),
        "partition": block(
            """
            int partition(int *arr, int lo, int hi) {
                int pivot = arr[hi];
                int i = lo - 1;
                for (int j = lo; j < hi; j++) {
                    if (arr[j] <= pivot) {
                        i++;
                        swap(&arr[i], &arr[j]);
                    }
                }
                swap(&arr[i + 1], &arr[hi]);
                return i + 1;
            }
            """
        ),
    }
    return sources[name]


def get_py_source(name: str) -> str:
    sources = {
        "bubble_sort": block(
            """
            def bubble_sort(arr: list[int]) -> list[int]:
                a = arr[:]
                n = len(a)
                for i in range(n - 1):
                    for j in range(n - 1 - i):
                        if a[j] > a[j + 1]:
                            a[j], a[j + 1] = a[j + 1], a[j]
                return a
            """
        ),
        "insertion_sort": block(
            """
            def insertion_sort(arr: list[int]) -> list[int]:
                a = arr[:]
                for i in range(1, len(a)):
                    key = a[i]
                    j = i - 1
                    while j >= 0 and a[j] > key:
                        a[j + 1] = a[j]
                        j -= 1
                    a[j + 1] = key
                return a
            """
        ),
        "selection_sort": block(
            """
            def selection_sort(arr: list[int]) -> list[int]:
                a = arr[:]
                n = len(a)
                for i in range(n - 1):
                    min_idx = i
                    for j in range(i + 1, n):
                        if a[j] < a[min_idx]:
                            min_idx = j
                    if min_idx != i:
                        a[i], a[min_idx] = a[min_idx], a[i]
                return a
            """
        ),
        "partition": block(
            """
            def partition(arr: list[int], lo: int, hi: int) -> tuple[list[int], int]:
                a = arr[:]
                pivot = a[hi]
                i = lo - 1
                for j in range(lo, hi):
                    if a[j] <= pivot:
                        i += 1
                        a[i], a[j] = a[j], a[i]
                a[i + 1], a[hi] = a[hi], a[i + 1]
                return a, i + 1
            """
        ),
        "merge_sorted": block(
            """
            def merge_sorted(a: list[int], b: list[int]) -> list[int]:
                result = []
                i, j = 0, 0
                while i < len(a) and j < len(b):
                    if a[i] <= b[j]:
                        result.append(a[i])
                        i += 1
                    else:
                        result.append(b[j])
                        j += 1
                result.extend(a[i:])
                result.extend(b[j:])
                return result
            """
        ),
    }
    return sources[name]


def get_lean_translation(name: str, lang: str) -> str:
    translations = {
        ("C", "swap"): block(
            """
            def swap (a b : Int) : Int × Int :=
              (b, a)
            """
        ),
        ("C", "bubble_sort"): block(
            """
            def is_sorted_ints : List Int → Prop
              | [] => True
              | [_] => True
              | x :: y :: xs => x ≤ y ∧ is_sorted_ints (y :: xs)

            def bubble_carry (carry : Int) : List Int → List Int × Int
              | [] => ([], carry)
              | y :: ys =>
                  if carry ≤ y then
                    let (front, last) := bubble_carry y ys
                    (carry :: front, last)
                  else
                    let (front, last) := bubble_carry carry ys
                    (y :: front, last)

            def bubble_pass : List Int → List Int
              | [] => []
              | x :: xs =>
                  let (front, last) := bubble_carry x xs
                  front ++ [last]

            def bubble_sort_fuel : Nat → List Int → List Int
              | 0, xs => xs
              | fuel + 1, xs =>
                  bubble_sort_fuel fuel (bubble_pass xs)

            def bubble_sort (arr : Array Int) : Array Int :=
              (bubble_sort_fuel arr.toList.length arr.toList).toArray
            """
        ),
        ("C", "insertion_sort"): block(
            """
            def is_sorted_ints : List Int → Prop
              | [] => True
              | [_] => True
              | x :: y :: xs => x ≤ y ∧ is_sorted_ints (y :: xs)

            def insert_sorted (x : Int) : List Int → List Int
              | [] => [x]
              | y :: ys =>
                  if x ≤ y then
                    x :: y :: ys
                  else
                    y :: insert_sorted x ys

            def insertion_sort (arr : Array Int) : Array Int :=
              (arr.toList.foldl (fun acc x => insert_sorted x acc) []).toArray
            """
        ),
        ("C", "selection_sort"): block(
            """
            def is_sorted_ints : List Int → Prop
              | [] => True
              | [_] => True
              | x :: y :: xs => x ≤ y ∧ is_sorted_ints (y :: xs)

            def min_element : List Int → Option Int
              | [] => none
              | [x] => some x
              | x :: xs =>
                  match min_element xs with
                  | none => some x
                  | some m => some (if x ≤ m then x else m)

            def remove_first (target : Int) : List Int → List Int
              | [] => []
              | x :: xs => if x = target then xs else x :: remove_first target xs

            def selection_sort_fuel : Nat → List Int → List Int
              | 0, _ => []
              | fuel + 1, [] => []
              | fuel + 1, xs =>
                  match min_element xs with
                  | none => []
                  | some m => m :: selection_sort_fuel fuel (remove_first m xs)

            def selection_sort (arr : Array Int) : Array Int :=
              (selection_sort_fuel arr.toList.length arr.toList).toArray
            """
        ),
        ("C", "partition"): block(
            """
            def split_le (pivot : Int) (xs : List Int) : List Int × List Int :=
              xs.foldr
                (fun x acc =>
                  if x ≤ pivot then
                    (x :: acc.1, acc.2)
                  else
                    (acc.1, x :: acc.2))
                ([], [])

            def partition (arr : Array Int) (lo hi : Nat) : Array Int × Nat :=
              match arr.get? hi with
              | none => (arr, lo)
              | some pivot =>
                  let xs := arr.toList
                  let prefix := xs.take lo
                  let middle := (xs.drop lo).take (hi - lo)
                  let suffix := xs.drop (hi + 1)
                  let (small, big) := split_le pivot middle
                  let pivotIdx := lo + small.length
                  ((prefix ++ small ++ [pivot] ++ big ++ suffix).toArray, pivotIdx)

            def partition_left (arr : Array Int) (lo hi : Nat) : List Int :=
              let result := partition arr lo hi
              (result.1.toList.drop lo).take (result.2 - lo)

            def partition_right (arr : Array Int) (lo hi : Nat) : List Int :=
              let result := partition arr lo hi
              (result.1.toList.drop (result.2 + 1)).take (hi - result.2)
            """
        ),
        ("Python", "bubble_sort"): block(
            """
            def is_sorted_ints : List Int → Prop
              | [] => True
              | [_] => True
              | x :: y :: xs => x ≤ y ∧ is_sorted_ints (y :: xs)

            def bubble_carry (carry : Int) : List Int → List Int × Int
              | [] => ([], carry)
              | y :: ys =>
                  if carry ≤ y then
                    let (front, last) := bubble_carry y ys
                    (carry :: front, last)
                  else
                    let (front, last) := bubble_carry carry ys
                    (y :: front, last)

            def bubble_pass : List Int → List Int
              | [] => []
              | x :: xs =>
                  let (front, last) := bubble_carry x xs
                  front ++ [last]

            def bubble_sort_fuel : Nat → List Int → List Int
              | 0, xs => xs
              | fuel + 1, xs =>
                  bubble_sort_fuel fuel (bubble_pass xs)

            def bubble_sort (arr : List Int) : List Int :=
              bubble_sort_fuel arr.length arr
            """
        ),
        ("Python", "insertion_sort"): block(
            """
            def is_sorted_ints : List Int → Prop
              | [] => True
              | [_] => True
              | x :: y :: xs => x ≤ y ∧ is_sorted_ints (y :: xs)

            def insert_sorted (x : Int) : List Int → List Int
              | [] => [x]
              | y :: ys =>
                  if x ≤ y then
                    x :: y :: ys
                  else
                    y :: insert_sorted x ys

            def insertion_sort (arr : List Int) : List Int :=
              arr.foldl (fun acc x => insert_sorted x acc) []
            """
        ),
        ("Python", "selection_sort"): block(
            """
            def is_sorted_ints : List Int → Prop
              | [] => True
              | [_] => True
              | x :: y :: xs => x ≤ y ∧ is_sorted_ints (y :: xs)

            def min_element : List Int → Option Int
              | [] => none
              | [x] => some x
              | x :: xs =>
                  match min_element xs with
                  | none => some x
                  | some m => some (if x ≤ m then x else m)

            def remove_first (target : Int) : List Int → List Int
              | [] => []
              | x :: xs => if x = target then xs else x :: remove_first target xs

            def selection_sort_fuel : Nat → List Int → List Int
              | 0, _ => []
              | fuel + 1, [] => []
              | fuel + 1, xs =>
                  match min_element xs with
                  | none => []
                  | some m => m :: selection_sort_fuel fuel (remove_first m xs)

            def selection_sort (arr : List Int) : List Int :=
              selection_sort_fuel arr.length arr
            """
        ),
        ("Python", "partition"): block(
            """
            def split_le (pivot : Int) (xs : List Int) : List Int × List Int :=
              xs.foldr
                (fun x acc =>
                  if x ≤ pivot then
                    (x :: acc.1, acc.2)
                  else
                    (acc.1, x :: acc.2))
                ([], [])

            def partition (arr : List Int) (lo hi : Nat) : List Int × Nat :=
              match arr.get? hi with
              | none => (arr, lo)
              | some pivot =>
                  let prefix := arr.take lo
                  let middle := (arr.drop lo).take (hi - lo)
                  let suffix := arr.drop (hi + 1)
                  let (small, big) := split_le pivot middle
                  let pivotIdx := lo + small.length
                  (prefix ++ small ++ [pivot] ++ big ++ suffix, pivotIdx)

            def partition_left (arr : List Int) (lo hi : Nat) : List Int :=
              let result := partition arr lo hi
              (result.1.drop lo).take (result.2 - lo)

            def partition_right (arr : List Int) (lo hi : Nat) : List Int :=
              let result := partition arr lo hi
              (result.1.drop (result.2 + 1)).take (hi - result.2)
            """
        ),
        ("Python", "merge_sorted"): block(
            """
            def is_sorted_ints : List Int → Prop
              | [] => True
              | [_] => True
              | x :: y :: xs => x ≤ y ∧ is_sorted_ints (y :: xs)

            def merge_sorted_fuel : Nat → List Int → List Int → List Int
              | 0, xs, ys => xs ++ ys
              | fuel + 1, [], ys => ys
              | fuel + 1, xs, [] => xs
              | fuel + 1, x :: xs, y :: ys =>
                  if x ≤ y then
                    x :: merge_sorted_fuel fuel xs (y :: ys)
                  else
                    y :: merge_sorted_fuel fuel (x :: xs) ys

            def merge_sorted (a b : List Int) : List Int :=
              merge_sorted_fuel (a.length + b.length) a b
            """
        ),
    }
    return translations[(lang, name)]


def get_c_tests(name: str) -> str:
    tests = {
        "swap": block(
            """
            #include <assert.h>
            #include <stdio.h>

            void swap(int *a, int *b) {
                int tmp = *a;
                *a = *b;
                *b = tmp;
            }

            int main() {
                int x = 3;
                int y = 7;
                swap(&x, &y);
                assert(x == 7);
                assert(y == 3);

                int a = -2;
                int b = -2;
                swap(&a, &b);
                assert(a == -2);
                assert(b == -2);

                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "bubble_sort": block(
            """
            #include <assert.h>
            #include <stdio.h>

            void swap(int *a, int *b) {
                int tmp = *a;
                *a = *b;
                *b = tmp;
            }

            void bubble_sort(int *arr, int n) {
                for (int i = 0; i < n - 1; i++) {
                    for (int j = 0; j < n - 1 - i; j++) {
                        if (arr[j] > arr[j + 1]) {
                            swap(&arr[j], &arr[j + 1]);
                        }
                    }
                }
            }

            static void assert_array_eq(const int *arr, const int *expected, int n) {
                for (int i = 0; i < n; i++) {
                    assert(arr[i] == expected[i]);
                }
            }

            int main() {
                int a0[] = {5, 1, 4, 2, 8};
                int e0[] = {1, 2, 4, 5, 8};
                bubble_sort(a0, 5);
                assert_array_eq(a0, e0, 5);

                int a1[] = {3, 3, 1, 2};
                int e1[] = {1, 2, 3, 3};
                bubble_sort(a1, 4);
                assert_array_eq(a1, e1, 4);

                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "insertion_sort": block(
            """
            #include <assert.h>
            #include <stdio.h>

            void insertion_sort(int *arr, int n) {
                for (int i = 1; i < n; i++) {
                    int key = arr[i];
                    int j = i - 1;
                    while (j >= 0 && arr[j] > key) {
                        arr[j + 1] = arr[j];
                        j--;
                    }
                    arr[j + 1] = key;
                }
            }

            static void assert_array_eq(const int *arr, const int *expected, int n) {
                for (int i = 0; i < n; i++) {
                    assert(arr[i] == expected[i]);
                }
            }

            int main() {
                int a0[] = {9, 5, 1, 4, 3};
                int e0[] = {1, 3, 4, 5, 9};
                insertion_sort(a0, 5);
                assert_array_eq(a0, e0, 5);

                int a1[] = {2, 2, 2};
                int e1[] = {2, 2, 2};
                insertion_sort(a1, 3);
                assert_array_eq(a1, e1, 3);

                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "selection_sort": block(
            """
            #include <assert.h>
            #include <stdio.h>

            void swap(int *a, int *b) {
                int tmp = *a;
                *a = *b;
                *b = tmp;
            }

            void selection_sort(int *arr, int n) {
                for (int i = 0; i < n - 1; i++) {
                    int min_idx = i;
                    for (int j = i + 1; j < n; j++) {
                        if (arr[j] < arr[min_idx]) {
                            min_idx = j;
                        }
                    }
                    if (min_idx != i) {
                        swap(&arr[i], &arr[min_idx]);
                    }
                }
            }

            static void assert_array_eq(const int *arr, const int *expected, int n) {
                for (int i = 0; i < n; i++) {
                    assert(arr[i] == expected[i]);
                }
            }

            int main() {
                int a0[] = {64, 25, 12, 22, 11};
                int e0[] = {11, 12, 22, 25, 64};
                selection_sort(a0, 5);
                assert_array_eq(a0, e0, 5);

                int a1[] = {4, 1, 4, 0};
                int e1[] = {0, 1, 4, 4};
                selection_sort(a1, 4);
                assert_array_eq(a1, e1, 4);

                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
        "partition": block(
            """
            #include <assert.h>
            #include <stdio.h>

            void swap(int *a, int *b) {
                int tmp = *a;
                *a = *b;
                *b = tmp;
            }

            int partition(int *arr, int lo, int hi) {
                int pivot = arr[hi];
                int i = lo - 1;
                for (int j = lo; j < hi; j++) {
                    if (arr[j] <= pivot) {
                        i++;
                        swap(&arr[i], &arr[j]);
                    }
                }
                swap(&arr[i + 1], &arr[hi]);
                return i + 1;
            }

            static void assert_array_eq(const int *arr, const int *expected, int n) {
                for (int i = 0; i < n; i++) {
                    assert(arr[i] == expected[i]);
                }
            }

            int main() {
                int a0[] = {4, 2, 7, 1, 3};
                int e0[] = {2, 1, 3, 4, 7};
                int p0 = partition(a0, 0, 4);
                assert(p0 == 2);
                assert_array_eq(a0, e0, 5);

                int a1[] = {1, 2, 3};
                int e1[] = {1, 2, 3};
                int p1 = partition(a1, 0, 2);
                assert(p1 == 2);
                assert_array_eq(a1, e1, 3);

                printf("All tests passed!\\n");
                return 0;
            }
            """
        ),
    }
    return tests[name]


def get_py_tests(name: str) -> str:
    tests = {
        "bubble_sort": block(
            """
            def bubble_sort(arr: list[int]) -> list[int]:
                a = arr[:]
                n = len(a)
                for i in range(n - 1):
                    for j in range(n - 1 - i):
                        if a[j] > a[j + 1]:
                            a[j], a[j + 1] = a[j + 1], a[j]
                return a

            assert bubble_sort([5, 1, 4, 2, 8]) == [1, 2, 4, 5, 8]
            assert bubble_sort([3, 3, 1, 2]) == [1, 2, 3, 3]
            print("All tests passed!")
            """
        ),
        "insertion_sort": block(
            """
            def insertion_sort(arr: list[int]) -> list[int]:
                a = arr[:]
                for i in range(1, len(a)):
                    key = a[i]
                    j = i - 1
                    while j >= 0 and a[j] > key:
                        a[j + 1] = a[j]
                        j -= 1
                    a[j + 1] = key
                return a

            assert insertion_sort([9, 5, 1, 4, 3]) == [1, 3, 4, 5, 9]
            assert insertion_sort([2, 2, 2]) == [2, 2, 2]
            print("All tests passed!")
            """
        ),
        "selection_sort": block(
            """
            def selection_sort(arr: list[int]) -> list[int]:
                a = arr[:]
                n = len(a)
                for i in range(n - 1):
                    min_idx = i
                    for j in range(i + 1, n):
                        if a[j] < a[min_idx]:
                            min_idx = j
                    if min_idx != i:
                        a[i], a[min_idx] = a[min_idx], a[i]
                return a

            assert selection_sort([64, 25, 12, 22, 11]) == [11, 12, 22, 25, 64]
            assert selection_sort([4, 1, 4, 0]) == [0, 1, 4, 4]
            print("All tests passed!")
            """
        ),
        "partition": block(
            """
            def partition(arr: list[int], lo: int, hi: int) -> tuple[list[int], int]:
                a = arr[:]
                pivot = a[hi]
                i = lo - 1
                for j in range(lo, hi):
                    if a[j] <= pivot:
                        i += 1
                        a[i], a[j] = a[j], a[i]
                a[i + 1], a[hi] = a[hi], a[i + 1]
                return a, i + 1

            assert partition([4, 2, 7, 1, 3], 0, 4) == ([2, 1, 3, 4, 7], 2)
            assert partition([1, 2, 3], 0, 2) == ([1, 2, 3], 2)
            print("All tests passed!")
            """
        ),
        "merge_sorted": block(
            """
            def merge_sorted(a: list[int], b: list[int]) -> list[int]:
                result = []
                i, j = 0, 0
                while i < len(a) and j < len(b):
                    if a[i] <= b[j]:
                        result.append(a[i])
                        i += 1
                    else:
                        result.append(b[j])
                        j += 1
                result.extend(a[i:])
                result.extend(b[j:])
                return result

            assert merge_sorted([1, 3, 5], [2, 4, 6]) == [1, 2, 3, 4, 5, 6]
            assert merge_sorted([], [7, 8]) == [7, 8]
            assert merge_sorted([1, 1, 4], [1, 2]) == [1, 1, 1, 2, 4]
            print("All tests passed!")
            """
        ),
    }
    return tests[name]


def get_lean_tests(name: str, lang: str) -> str:
    tests = {
        ("C", "swap"): block(
            """
            #eval swap 3 7
            #eval swap (-2) (-2)
            """
        ),
        ("C", "bubble_sort"): block(
            """
            #eval bubble_sort #[5, 1, 4, 2, 8]
            #eval bubble_sort #[3, 3, 1, 2]
            """
        ),
        ("C", "insertion_sort"): block(
            """
            #eval insertion_sort #[9, 5, 1, 4, 3]
            #eval insertion_sort #[2, 2, 2]
            """
        ),
        ("C", "selection_sort"): block(
            """
            #eval selection_sort #[64, 25, 12, 22, 11]
            #eval selection_sort #[4, 1, 4, 0]
            """
        ),
        ("C", "partition"): block(
            """
            #eval partition #[4, 2, 7, 1, 3] 0 4
            #eval partition #[1, 2, 3] 0 2
            """
        ),
        ("Python", "bubble_sort"): block(
            """
            #eval bubble_sort [5, 1, 4, 2, 8]
            #eval bubble_sort [3, 3, 1, 2]
            """
        ),
        ("Python", "insertion_sort"): block(
            """
            #eval insertion_sort [9, 5, 1, 4, 3]
            #eval insertion_sort [2, 2, 2]
            """
        ),
        ("Python", "selection_sort"): block(
            """
            #eval selection_sort [64, 25, 12, 22, 11]
            #eval selection_sort [4, 1, 4, 0]
            """
        ),
        ("Python", "partition"): block(
            """
            #eval partition [4, 2, 7, 1, 3] 0 4
            #eval partition [1, 2, 3] 0 2
            """
        ),
        ("Python", "merge_sorted"): block(
            """
            #eval merge_sorted [1, 3, 5] [2, 4, 6]
            #eval merge_sorted [] [7, 8]
            """
        ),
    }
    return tests[(lang, name)]


def get_theorems(name: str, lang: str) -> list[dict]:
    if lang == "C" and name == "swap":
        return [
            thm(
                "swap_fst",
                "theorem swap_fst (a b : Int) : (swap a b).1 = b",
                "by rfl",
                False,
            ),
            thm(
                "swap_snd",
                "theorem swap_snd (a b : Int) : (swap a b).2 = a",
                "by rfl",
                False,
            ),
            thm(
                "swap_involution",
                "theorem swap_involution (a b : Int) : swap (swap a b).1 (swap a b).2 = (a, b)",
                "by rfl",
                False,
            ),
            thm(
                "swap_sum_preserved",
                "theorem swap_sum_preserved (a b : Int) : (swap a b).1 + (swap a b).2 = a + b",
                "by simpa [swap, add_comm]",
                False,
            ),
        ]

    if name in {"bubble_sort", "insertion_sort", "selection_sort"}:
        container = "Array Int" if lang == "C" else "List Int"
        subject = "arr : Array Int" if lang == "C" else "arr : List Int"
        term = name
        result_term = f"{term} arr" if lang == "Python" else f"{term} arr"
        length_expr = (
            f"({result_term}).toList.length = arr.toList.length"
            if lang == "C"
            else f"({result_term}).length = arr.length"
        )
        sorted_expr = (
            f"is_sorted_ints ({result_term}).toList"
            if lang == "C"
            else f"is_sorted_ints ({result_term})"
        )
        perm_expr = (
            f"List.Perm ({result_term}).toList arr.toList"
            if lang == "C"
            else f"List.Perm ({result_term}) arr"
        )
        idempotent_expr = (
            f"{term} ({term} arr) = {term} arr"
            if lang == "Python"
            else f"{term} ({term} arr) = {term} arr"
        )
        return [
            thm(
                f"{name}_length",
                f"theorem {name}_length ({subject}) : {length_expr}",
                "by sorry",
                True,
            ),
            thm(
                f"{name}_sorted",
                f"theorem {name}_sorted ({subject}) : {sorted_expr}",
                "by sorry",
                True,
            ),
            thm(
                f"{name}_idempotent",
                f"theorem {name}_idempotent ({subject}) : {idempotent_expr}",
                "by sorry",
                True,
            ),
            thm(
                f"{name}_perm",
                f"theorem {name}_perm ({subject}) : {perm_expr}",
                "by sorry",
                True,
            ),
        ]

    if name == "partition":
        if lang == "C":
            return [
                thm(
                    "partition_index_range",
                    "theorem partition_index_range (arr : Array Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : lo ≤ (partition arr lo hi).2 ∧ (partition arr lo hi).2 ≤ hi",
                    "by sorry",
                    True,
                ),
                thm(
                    "partition_places_pivot",
                    "theorem partition_places_pivot (arr : Array Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : (partition arr lo hi).1.get? (partition arr lo hi).2 = some pivot",
                    "by sorry",
                    True,
                ),
                thm(
                    "partition_left_le_pivot",
                    "theorem partition_left_le_pivot (arr : Array Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : ∀ x, x ∈ partition_left arr lo hi → x ≤ pivot",
                    "by sorry",
                    True,
                ),
                thm(
                    "partition_right_gt_pivot",
                    "theorem partition_right_gt_pivot (arr : Array Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : ∀ x, x ∈ partition_right arr lo hi → pivot < x",
                    "by sorry",
                    True,
                ),
            ]
        return [
            thm(
                "partition_index_range",
                "theorem partition_index_range (arr : List Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : lo ≤ (partition arr lo hi).2 ∧ (partition arr lo hi).2 ≤ hi",
                "by sorry",
                True,
            ),
            thm(
                "partition_places_pivot",
                "theorem partition_places_pivot (arr : List Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : (partition arr lo hi).1.get? (partition arr lo hi).2 = some pivot",
                "by sorry",
                True,
            ),
            thm(
                "partition_left_le_pivot",
                "theorem partition_left_le_pivot (arr : List Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : ∀ x, x ∈ partition_left arr lo hi → x ≤ pivot",
                "by sorry",
                True,
            ),
            thm(
                "partition_right_gt_pivot",
                "theorem partition_right_gt_pivot (arr : List Int) (lo hi : Nat) (pivot : Int) (h : arr.get? hi = some pivot) (hlo : lo ≤ hi) : ∀ x, x ∈ partition_right arr lo hi → pivot < x",
                "by sorry",
                True,
            ),
        ]

    if lang == "Python" and name == "merge_sorted":
        return [
            thm(
                "merge_sorted_nil_left",
                "theorem merge_sorted_nil_left (b : List Int) : merge_sorted [] b = b",
                "by cases b <;> simp [merge_sorted, merge_sorted_fuel]",
                False,
            ),
            thm(
                "merge_sorted_length",
                "theorem merge_sorted_length (a b : List Int) : (merge_sorted a b).length = a.length + b.length",
                "by sorry",
                True,
            ),
            thm(
                "merge_sorted_sorted",
                "theorem merge_sorted_sorted (a b : List Int) (ha : is_sorted_ints a) (hb : is_sorted_ints b) : is_sorted_ints (merge_sorted a b)",
                "by sorry",
                True,
            ),
            thm(
                "merge_sorted_perm",
                "theorem merge_sorted_perm (a b : List Int) : List.Perm (merge_sorted a b) (a ++ b)",
                "by sorry",
                True,
            ),
        ]

    raise KeyError((lang, name))


def get_deps(name: str, lang: str) -> list[str]:
    if lang == "C" and name in {"bubble_sort", "selection_sort", "partition"}:
        return ["swap"]
    return []


def build_record(lang: str, name: str) -> dict:
    return {
        "language": lang,
        "source": get_c_source(name) if lang == "C" else get_py_source(name),
        "lean_translation": get_lean_translation(name, lang),
        "tests": get_c_tests(name) if lang == "C" else get_py_tests(name),
        "lean_tests": get_lean_tests(name, lang),
        "theorems": get_theorems(name, lang),
        "deps_fully_translated": get_deps(name, lang),
        "axiomatized_deps": [],
        "skip_reason": None,
    }


def main() -> None:
    c_functions = ["swap", "bubble_sort", "insertion_sort", "selection_sort", "partition"]
    py_functions = ["bubble_sort", "insertion_sort", "selection_sort", "partition", "merge_sorted"]

    output_path = Path("/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/output/batch05_sort.jsonl")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for name in c_functions:
            f.write(json.dumps(build_record("C", name)) + "\n")
        for name in py_functions:
            f.write(json.dumps(build_record("Python", name)) + "\n")


if __name__ == "__main__":
    main()
