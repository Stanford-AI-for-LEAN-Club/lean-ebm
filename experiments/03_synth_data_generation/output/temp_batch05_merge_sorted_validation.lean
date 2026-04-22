import Std

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

#eval merge_sorted [1, 3, 5] [2, 4, 6]
#eval merge_sorted [] [7, 8]

theorem merge_sorted_nil_left (b : List Int) : merge_sorted [] b = b := by cases b <;> simp [merge_sorted, merge_sorted_fuel]

theorem merge_sorted_length (a b : List Int) : (merge_sorted a b).length = a.length + b.length := by sorry

theorem merge_sorted_sorted (a b : List Int) (ha : is_sorted_ints a) (hb : is_sorted_ints b) : is_sorted_ints (merge_sorted a b) := by sorry

theorem merge_sorted_perm (a b : List Int) : List.Perm (merge_sorted a b) (a ++ b) := by sorry
