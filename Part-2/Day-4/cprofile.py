import cProfile
import time
from pstats import SortKey


def add(a, b):
    return a + b


def fact(n):
    if n == 0:
        return 1
    else:
        return n * fact(n - 1)


def do_something():
    time.sleep(5)
    for i in range(1000):
        add(i, i)
    fact(10)


if __name__ == "__main__":
    with cProfile.Profile() as pr:
        r1 = add(1, 2)
        r2 = fact(50)
        print(f"add(1, 2) = {r1}")
        print(f"fact(5) = {r2}")
        do_something()
    # pr.print_stats()
    ps = Stats(pr)
    ps.sort_stats("cumulative").print_stats()
