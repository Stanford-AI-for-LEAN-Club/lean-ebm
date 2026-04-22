import importlib.util


spec = importlib.util.spec_from_file_location(
    "batch02_gcd_math",
    "/Users/brandomiranda/lean-ebm/experiments/03_synth_data_generation/py_src/batch02_gcd_math.py",
)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

assert module.gcd(0, 0) == 0
assert module.gcd(1, 0) == 1
assert module.gcd(48, 18) == 6

assert module.lcm(0, 5) == 0
assert module.lcm(1, 7) == 7
assert module.lcm(12, 18) == 36

assert module.power(0, 0) == 1
assert module.power(5, 0) == 1
assert module.power(2, 10) == 1024

assert module.is_prime(0) is False
assert module.is_prime(2) is True
assert module.is_prime(97) is True
assert module.is_prime(99) is False

assert module.mod_exp(7, 3, 0) == 0
assert module.mod_exp(5, 0, 13) == 1
assert module.mod_exp(2, 10, 1000) == 24

assert module.sum_digits(0) == 0
assert module.sum_digits(7) == 7
assert module.sum_digits(12345) == 15

assert module.count_digits(0) == 1
assert module.count_digits(7) == 1
assert module.count_digits(1000) == 4
