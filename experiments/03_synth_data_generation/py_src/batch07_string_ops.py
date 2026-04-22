"""Batch 07: String operations — pure functions on strings/byte arrays."""

def str_len(s: str) -> int:
    count = 0
    for _ in s:
        count += 1
    return count

def str_equal(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    for i in range(len(a)):
        if a[i] != b[i]:
            return False
    return True

def is_palindrome(s: str) -> bool:
    n = len(s)
    for i in range(n // 2):
        if s[i] != s[n - 1 - i]:
            return False
    return True

def count_char(s: str, c: str) -> int:
    count = 0
    for ch in s:
        if ch == c:
            count += 1
    return count

def to_upper(s: str) -> str:
    result = []
    for c in s:
        if 'a' <= c <= 'z':
            result.append(chr(ord(c) - ord('a') + ord('A')))
        else:
            result.append(c)
    return ''.join(result)

def to_lower(s: str) -> str:
    result = []
    for c in s:
        if 'A' <= c <= 'Z':
            result.append(chr(ord(c) - ord('A') + ord('a')))
        else:
            result.append(c)
    return ''.join(result)

def char_is_digit(c: str) -> bool:
    return '0' <= c <= '9'

def char_is_alpha(c: str) -> bool:
    return ('a' <= c <= 'z') or ('A' <= c <= 'Z')
