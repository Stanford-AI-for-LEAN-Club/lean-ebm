import Std

def upperChar (c : Char) : Char :=
  if 'a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat then
    Char.ofNat (c.toNat - 'a'.toNat + 'A'.toNat)
  else
    c

def to_upper (s : String) : String :=
  String.mk (s.toList.map upperChar)

#eval to_upper "Lean42!"
#eval to_upper "already UPPER"
#eval to_upper ""
#check to_upper

theorem to_upper_toList (s : String) : (to_upper s).toList = s.toList.map upperChar :=
by
  simp [to_upper]

theorem to_upper_length (s : String) : (to_upper s).toList.length = s.toList.length :=
by
  simp [to_upper]

theorem to_upper_idempotent (s : String) : to_upper (to_upper s) = to_upper s :=
by
  sorry
