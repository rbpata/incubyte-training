from functools import lru_cache


@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


# cache vs lru_cache
from functools import cache


@cache
def fibonacci_cache(n):
    if n < 0:
        raise ValueError("Input must be a non-negative integer.")
    elif n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci_cache(n - 1) + fibonacci_cache(n - 2)


if __name__ == "__main__":
    n = 35
    print(f"Fibonacci({n}) = {fibonacci_cache(n)}")
    print(f"Fibonacci({n}) = {fibonacci(n)}")
    print(f"Cache info: {fibonacci_cache.cache_info()}")
    print(f"LRU Cache info: {fibonacci.cache_info()}")
    lru_cache.cache_clear()
    cache.cache_clear()
