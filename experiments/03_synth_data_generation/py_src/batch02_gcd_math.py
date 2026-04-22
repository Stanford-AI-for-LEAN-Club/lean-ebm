"""Batch 02: Number theory and math functions — pure computation."""

def gcd(a: int, b: int) -> int:
    while b != 0:
        a, b = b, a % b
    return a

def lcm(a: int, b: int) -> int:
    if a == 0 or b == 0:
        return 0
    return (a // gcd(a, b)) * b

def power(base: int, exp: int) -> int:
    result = 1
    while exp > 0:
        if exp % 2 == 1:
            result *= base
        base *= base
        exp //= 2
    return result

def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

def mod_exp(base: int, exp: int, mod: int) -> int:
    if mod == 0:
        return 0
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    return result

def sum_digits(n: int) -> int:
    s = 0
    while n > 0:
        s += n % 10
        n //= 10
    return s

def count_digits(n: int) -> int:
    if n == 0:
        return 1
    c = 0
    while n > 0:
        c += 1
        n //= 10
    return c
