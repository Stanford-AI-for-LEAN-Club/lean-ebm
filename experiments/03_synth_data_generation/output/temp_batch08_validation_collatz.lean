partial def collatz_steps (n : Nat) : Nat :=
  if n = 0 ∨ n = 1 then
    0
  else if n % 2 = 0 then
    1 + collatz_steps (n / 2)
  else
    1 + collatz_steps (3 * n + 1)

def triangular_number (n : Nat) : Nat :=
  n * (n + 1) / 2

def is_even (n : Int) : Bool :=
  n % 2 == 0

def is_odd (n : Int) : Bool :=
  n % 2 != 0

#eval collatz_steps 0
#eval collatz_steps 1
#eval collatz_steps 3
#eval collatz_steps 6
#eval triangular_number 10
#eval is_even (-2)
#eval is_odd (-3)
