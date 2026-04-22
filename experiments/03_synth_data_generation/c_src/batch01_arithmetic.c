/* Batch 01: Basic arithmetic functions — no pointers, no I/O, pure computation */

int abs_val(int x) {
    if (x < 0) return -x;
    return x;
}

int max_of_two(int a, int b) {
    if (a >= b) return a;
    return b;
}

int min_of_two(int a, int b) {
    if (a <= b) return a;
    return b;
}

int clamp(int x, int lo, int hi) {
    if (x < lo) return lo;
    if (x > hi) return hi;
    return x;
}

unsigned int factorial(unsigned int n) {
    unsigned int result = 1;
    for (unsigned int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

unsigned int fibonacci(unsigned int n) {
    if (n <= 1) return n;
    unsigned int a = 0, b = 1;
    for (unsigned int i = 2; i <= n; i++) {
        unsigned int tmp = a + b;
        a = b;
        b = tmp;
    }
    return b;
}

int sign(int x) {
    if (x > 0) return 1;
    if (x < 0) return -1;
    return 0;
}
