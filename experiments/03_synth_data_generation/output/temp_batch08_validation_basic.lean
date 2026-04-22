partial def integer_sqrt (n : Nat) : Nat :=
  if n = 0 then
    0
  else
    let rec loop (x : Nat) : Nat :=
      if (x + 1) * (x + 1) ≤ n then
        loop (x + 1)
      else
        x
    loop 0

partial def binomial (n k : Nat) : Nat :=
  if k > n then
    0
  else if k = 0 || k = n then
    1
  else
    let k' := if k > n - k then n - k else k
    let rec loop (i result : Nat) : Nat :=
      if i < k' then
        loop (i + 1) (result * (n - i) / (i + 1))
      else
        result
    loop 0 1

def digital_root (n : Nat) : Nat :=
  if n = 0 then
    0
  else
    1 + (n - 1) % 9

#eval integer_sqrt 17
#eval integer_sqrt 49
#eval binomial 5 2
#eval binomial 4 5
#eval digital_root 38
#eval digital_root 9999
