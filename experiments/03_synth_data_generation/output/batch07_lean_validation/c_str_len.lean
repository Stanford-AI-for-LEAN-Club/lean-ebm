import Std

def str_len (s : String) : Nat :=
  s.length

#eval str_len ""
#eval str_len "lean"
#eval str_len "racecar"
#check str_len

theorem str_len_eq_length (s : String) : str_len s = s.length :=
by
  rfl

theorem str_len_append (s t : String) : str_len (s ++ t) = str_len s + str_len t :=
by
  simpa [str_len] using String.length_append s t
