"""Batch 04: Search algorithms — pure functions on lists."""

def linear_search(arr: list[int], target: int) -> int:
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1

def binary_search(arr: list[int], target: int) -> int:
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

def find_first(arr: list[int], target: int) -> int:
    lo, hi, result = 0, len(arr) - 1, -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            hi = mid - 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result

def find_last(arr: list[int], target: int) -> int:
    lo, hi, result = 0, len(arr) - 1, -1
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if arr[mid] == target:
            result = mid
            lo = mid + 1
        elif arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return result

def contains(arr: list[int], val: int) -> bool:
    for x in arr:
        if x == val:
            return True
    return False

def index_of_max(arr: list[int]) -> int:
    idx = 0
    for i in range(1, len(arr)):
        if arr[i] > arr[idx]:
            idx = i
    return idx
