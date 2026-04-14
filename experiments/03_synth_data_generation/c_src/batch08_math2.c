/* Batch 08: More math functions — pure computation, no pointers */

unsigned int integer_sqrt(unsigned int n) {
    if (n == 0) return 0;
    unsigned int x = n;
    unsigned int y = (x + 1) / 2;
    while (y < x) {
        x = y;
        y = (x + n / x) / 2;
    }
    return x;
}

int is_perfect_square(unsigned int n) {
    unsigned int s = integer_sqrt(n);
    return s * s == n;
}

unsigned int binomial(unsigned int n, unsigned int k) {
    if (k > n) return 0;
    if (k == 0 || k == n) return 1;
    if (k > n - k) k = n - k;
    unsigned int result = 1;
    for (unsigned int i = 0; i < k; i++) {
        result = result * (n - i) / (i + 1);
    }
    return result;
}

int is_even(int n) {
    return n % 2 == 0;
}

int is_odd(int n) {
    return n % 2 != 0;
}

unsigned int triangular_number(unsigned int n) {
    return n * (n + 1) / 2;
}

int collatz_steps(unsigned int n) {
    int steps = 0;
    while (n != 1 && n != 0) {
        if (n % 2 == 0) {
            n = n / 2;
        } else {
            n = 3 * n + 1;
        }
        steps++;
    }
    return steps;
}

unsigned int digital_root(unsigned int n) {
    if (n == 0) return 0;
    return 1 + (n - 1) % 9;
}
