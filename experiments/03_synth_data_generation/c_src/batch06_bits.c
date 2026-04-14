/* Batch 06: Bit manipulation — pure functions on unsigned integers */

int is_power_of_two(unsigned int n) {
    return n != 0 && (n & (n - 1)) == 0;
}

unsigned int count_set_bits(unsigned int n) {
    unsigned int count = 0;
    while (n) {
        count += n & 1;
        n >>= 1;
    }
    return count;
}

unsigned int parity(unsigned int n) {
    unsigned int p = 0;
    while (n) {
        p ^= (n & 1);
        n >>= 1;
    }
    return p;
}

unsigned int reverse_bits(unsigned int n) {
    unsigned int result = 0;
    for (int i = 0; i < 32; i++) {
        result = (result << 1) | (n & 1);
        n >>= 1;
    }
    return result;
}

unsigned int next_power_of_two(unsigned int n) {
    if (n == 0) return 1;
    n--;
    n |= n >> 1;
    n |= n >> 2;
    n |= n >> 4;
    n |= n >> 8;
    n |= n >> 16;
    return n + 1;
}

unsigned int lowest_set_bit(unsigned int n) {
    return n & (~n + 1);
}

unsigned int clear_lowest_set_bit(unsigned int n) {
    return n & (n - 1);
}
