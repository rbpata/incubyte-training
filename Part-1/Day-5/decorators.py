# closure example


def multiply_by(n):
    def multiplier(x):
        return x * n

    return multiplier


double = multiply_by(2)
triple = multiply_by(3)
print(double(5))  # Output: 10
print(triple(5))  # Output: 15

print(double.__closure__)
print(f"Double's closure value: {double.__closure__[0].cell_contents}")
print(f"Triple's closure value: {triple.__closure__[0].cell_contents}")


def add_spinkles(func):
    def wrapper():
        print("Adding sprinkles on top of the ice cream")
        func()

    return wrapper


@add_spinkles
def get_ice_cream():
    print("I got the mango ice cream")


get_ice_cream()


# decorator with the argument


def repeat(times):
    def decorator(func):
        print(f"Repeating the function {times} times")

        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)

        return wrapper

    return decorator


@repeat(3)
def sum(a, b):
    print(f"The sum of {a} and {b} is {a + b}")


print(sum(2, 3))

import time
import functools


def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"function took {end-start} time.")
        return result

    return wrapper


@timer
def slow_function():
    import time

    time.sleep(1)
    print("Finished slow function")


slow_function()


# decorator with the arguments


def repeat(n):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                func(*args, **kwargs)

        return wrapper

    return decorator


@repeat(3)
def greet(msg):
    print(msg)


greet("ram")


def validate_positive(func):
    def wrapper(*args, **kwargs):
        for value in list(args) + list(kwargs.values()):
            if isinstance(value, int) and value < 0:
                raise ValueError("Nagative pages can not be allowed")
        return func(*args, **kwargs)

    return wrapper


@validate_positive
def create_book(title, pages):
    return {"title": title, "pages": pages}


print(create_book("TDD", pages=1))


# stack decorator
# def timer(func):
#     def wrapper():
#         start = time.perf_counter
#         func()
#         end = time.perf_counter
#         print(f"get_city took {end - start} time")

#     return wrapper


def shout(func):
    def wrapper():
        result = func()
        result = str.upper(result)
        return result

    return wrapper


@timer
@shout
def get_city():
    import time

    time.sleep(1)
    return "New York"


print(get_city())

import functools


def log_call(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        print(f"Calling {func.__name__}")
        print(f"Args: {args}")
        print(f"Kwargs: {kwargs}")

        result = func(*args, **kwargs)

        print(f"Returned: {result}")

        return result

    return wrapper
