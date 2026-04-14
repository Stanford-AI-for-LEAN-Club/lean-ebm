import Std

namespace Batch06PyCountBits

def count_set_bits_go (m acc : Nat) : Nat -> Nat
  | 0 => acc
  | fuel + 1 =>
      if m == 0 then acc
      else count_set_bits_go (m / 2) (acc + (m % 2)) fuel

def count_set_bits (n : Nat) : Nat :=
  count_set_bits_go n 0 (n + 1)

#eval count_set_bits 0
#eval count_set_bits 7
#eval count_set_bits 61680

theorem count_set_bits_eq_go (n : Nat) :
    count_set_bits n = count_set_bits_go n 0 (n + 1) := by
  rfl

theorem count_set_bits_zero_iff (n : Nat) :
    Iff (count_set_bits n = 0) (n = 0) := by
  sorry

theorem count_set_bits_even (n : Nat) :
    count_set_bits (2 * n) = count_set_bits n := by
  sorry

theorem count_set_bits_odd (n : Nat) :
    count_set_bits (2 * n + 1) = count_set_bits n + 1 := by
  sorry

end Batch06PyCountBits
