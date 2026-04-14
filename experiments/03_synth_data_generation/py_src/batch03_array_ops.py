"""Batch 03: Array/list operations — pure functions."""

def sum_array(arr: list[int]) -> int:
    s = 0
    for x in arr:
        s += x
    return s

def product_array(arr: list[int]) -> int:
    p = 1
    for x in arr:
        p *= x
    return p

def max_element(arr: list[int]) -> int:
    m = arr[0]
    for i in range(1, len(arr)):
        if arr[i] > m:
            m = arr[i]
    return m

def min_element(arr: list[int]) -> int:
    m = arr[0]
    for i in range(1, len(arr)):
        if arr[i] < m:
            m = arr[i]
    return m

def reverse_array(arr: list[int]) -> list[int]:
    result = arr[:]
    n = len(result)
    for i in range(n // 2):
        result[i], result[n - 1 - i] = result[n - 1 - i], result[i]
    return result

def is_sorted(arr: list[int]) -> bool:
    for i in range(len(arr) - 1):
        if arr[i] > arr[i + 1]:
            return False
    return True

def count_occurrences(arr: list[int], val: int) -> int:
    c = 0
    for x in arr:
        if x == val:
            c += 1
    return c
