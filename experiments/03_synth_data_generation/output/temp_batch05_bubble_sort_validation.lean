import Std

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

#eval bubble_sort #[5, 1, 4, 2, 8]
#eval bubble_sort #[3, 3, 1, 2]

theorem bubble_sort_length (arr : Array Int) : (bubble_sort arr).toList.length = arr.toList.length := by sorry

theorem bubble_sort_sorted (arr : Array Int) : is_sorted_ints (bubble_sort arr).toList := by sorry

theorem bubble_sort_idempotent (arr : Array Int) : bubble_sort (bubble_sort arr) = bubble_sort arr := by sorry

theorem bubble_sort_perm (arr : Array Int) : List.Perm (bubble_sort arr).toList arr.toList := by sorry
