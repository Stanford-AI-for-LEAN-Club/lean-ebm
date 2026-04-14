import Std

def is_palindrome (s : String) (len : Nat) : Bool :=
  let xs := s.toList.take len
  xs == xs.reverse

#eval is_palindrome "racecar" 7
#eval is_palindrome "abc" 3
#eval is_palindrome "abbaXYZ" 4
#check is_palindrome

theorem is_palindrome_prefix_iff (s : String) (len : Nat) :
    is_palindrome s len = true ↔ s.toList.take len = (s.toList.take len).reverse :=
by
  simp [is_palindrome]

theorem is_palindrome_full_length_iff (s : String) :
    is_palindrome s s.length = true ↔ s.toList = s.toList.reverse :=
by
  sorry

theorem is_palindrome_zero_len (s : String) : is_palindrome s 0 = true :=
by
  simp [is_palindrome]
