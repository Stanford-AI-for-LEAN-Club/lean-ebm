/* Batch 02: Number theory and math functions — pure computation */

unsigned int gcd(unsigned int a, unsigned int b) {
    while (b != 0) {
        unsigned int t = b;
        b = a % b;
        a = t;
    }
    return a;
}

unsigned int lcm(unsigned int a, unsigned int b) {
    if (a == 0 || b == 0) return 0;
    return (a / gcd(a, b)) * b;
}

unsigned int power(unsigned int base, unsigned int exp) {
    unsigned int result = 1;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result *= base;
        }
        base *= base;
        exp /= 2;
    }
    return result;
}

int is_prime(unsigned int n) {
    if (n < 2) return 0;
    if (n == 2) return 1;
    if (n % 2 == 0) return 0;
    for (unsigned int i = 3; i * i <= n; i += 2) {
        if (n % i == 0) return 0;
    }
    return 1;
}

unsigned int mod_exp(unsigned int base, unsigned int exp, unsigned int mod) {
    if (mod == 0) return 0;
    unsigned int result = 1;
    base = base % mod;
    while (exp > 0) {
        if (exp % 2 == 1) {
            result = (result * base) % mod;
        }
        exp /= 2;
        base = (base * base) % mod;
    }
    return result;
}

unsigned int sum_digits(unsigned int n) {
    unsigned int s = 0;
    while (n > 0) {
        s += n % 10;
        n /= 10;
    }
    return s;
}

unsigned int count_digits(unsigned int n) {
    if (n == 0) return 1;
    unsigned int c = 0;
    while (n > 0) {
        c++;
        n /= 10;
    }
    return c;
}
