#include <assert.h>

#include "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/c_src/batch02_gcd_math.c"

int main(void) {
    assert(gcd(0u, 0u) == 0u);
    assert(gcd(1u, 0u) == 1u);
    assert(gcd(48u, 18u) == 6u);

    assert(lcm(0u, 5u) == 0u);
    assert(lcm(1u, 7u) == 7u);
    assert(lcm(12u, 18u) == 36u);

    assert(power(0u, 0u) == 1u);
    assert(power(5u, 0u) == 1u);
    assert(power(2u, 10u) == 1024u);

    assert(is_prime(0u) == 0);
    assert(is_prime(2u) == 1);
    assert(is_prime(97u) == 1);
    assert(is_prime(99u) == 0);

    assert(mod_exp(7u, 3u, 0u) == 0u);
    assert(mod_exp(5u, 0u, 13u) == 1u);
    assert(mod_exp(2u, 10u, 1000u) == 24u);

    assert(sum_digits(0u) == 0u);
    assert(sum_digits(7u) == 7u);
    assert(sum_digits(12345u) == 15u);

    assert(count_digits(0u) == 1u);
    assert(count_digits(7u) == 1u);
    assert(count_digits(1000u) == 4u);

    return 0;
}
