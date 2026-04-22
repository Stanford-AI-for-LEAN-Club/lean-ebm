"""Batch 08: More math functions — pure computation."""

def integer_sqrt(n: int) -> int:
    if n == 0:
        return 0
    x = n
    y = (x + 1) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x

def is_perfect_square(n: int) -> bool:
    s = integer_sqrt(n)
    return s * s == n

def binomial(n: int, k: int) -> int:
    if k > n:
        return 0
    if k == 0 or k == n:
        return 1
    if k > n - k:
        k = n - k
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result

def is_even(n: int) -> bool:
    return n % 2 == 0

def is_odd(n: int) -> bool:
    return n % 2 != 0

def triangular_number(n: int) -> int:
    return n * (n + 1) // 2

def collatz_steps(n: int) -> int:
    steps = 0
    while n != 1 and n != 0:
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps

def digital_root(n: int) -> int:
    if n == 0:
        return 0
    return 1 + (n - 1) % 9
