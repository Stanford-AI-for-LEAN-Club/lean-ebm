import Std

def char_is_alpha (c : Char) : Bool :=
  decide (('a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat) ∨ ('A'.toNat ≤ c.toNat ∧ c.toNat ≤ 'Z'.toNat))

#eval char_is_alpha 'a'
#eval char_is_alpha 'Z'
#eval char_is_alpha '5'
#check char_is_alpha

theorem char_is_alpha_iff (c : Char) :
    char_is_alpha c = true ↔ (('a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat) ∨ ('A'.toNat ≤ c.toNat ∧ c.toNat ≤ 'Z'.toNat)) :=
by
  simp [char_is_alpha]

theorem char_is_alpha_false_outside_ranges (c : Char)
    (h : ('a'.toNat ≤ c.toNat ∧ c.toNat ≤ 'z'.toNat) = False)
    (h' : ('A'.toNat ≤ c.toNat ∧ c.toNat ≤ 'Z'.toNat) = False) :
    char_is_alpha c = false :=
by
  sorry
