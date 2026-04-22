"""Batch 06: Bit manipulation — pure functions on non-negative integers."""

def is_power_of_two(n: int) -> bool:
    return n != 0 and (n & (n - 1)) == 0

def count_set_bits(n: int) -> int:
    count = 0
    while n:
        count += n & 1
        n >>= 1
    return count

def parity(n: int) -> int:
    p = 0
    while n:
        p ^= (n & 1)
        n >>= 1
    return p

def reverse_bits_32(n: int) -> int:
    result = 0
    for _ in range(32):
        result = (result << 1) | (n & 1)
        n >>= 1
    return result

def next_power_of_two(n: int) -> int:
    if n == 0:
        return 1
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    return n + 1

def lowest_set_bit(n: int) -> int:
    return n & (~n + 1)

def clear_lowest_set_bit(n: int) -> int:
    return n & (n - 1)
