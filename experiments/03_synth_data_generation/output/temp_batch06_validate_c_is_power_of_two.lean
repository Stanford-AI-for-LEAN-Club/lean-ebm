import Std

namespace Batch06CIsPower

def is_power_of_two (n : UInt32) : Bool :=
  n != 0 && (n &&& (n - 1)) == 0

#eval is_power_of_two 0
#eval is_power_of_two 16
#eval is_power_of_two 18

theorem is_power_of_two_eq_bit_test (n : UInt32) :
    is_power_of_two n = (n != 0 && (n &&& (n - 1)) == 0) := by
  rfl

theorem is_power_of_two_true_iff_single_bit (n : UInt32) :
    Iff (is_power_of_two n = true) (And (n != 0) ((n &&& (n - 1)) = 0)) := by
  sorry

theorem is_power_of_two_shifted_one (k : Nat) (hk : k < 32) :
    is_power_of_two (UInt32.ofNat (2 ^ k)) = true := by
  sorry

end Batch06CIsPower
