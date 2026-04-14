"""Batch 01: Basic arithmetic functions — pure computation."""

def abs_val(x: int) -> int:
    if x < 0:
        return -x
    return x

def max_of_two(a: int, b: int) -> int:
    if a >= b:
        return a
    return b

def min_of_two(a: int, b: int) -> int:
    if a <= b:
        return a
    return b

def clamp(x: int, lo: int, hi: int) -> int:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x

def factorial(n: int) -> int:
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result

def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

def sign(x: int) -> int:
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0
