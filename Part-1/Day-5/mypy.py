from typing import Callable, Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def my_decorator(func: F) -> F:
    def wrapper(*args, **kwargs):
        print("Before the function call")
        result = func(*args, **kwargs)
        print("After the function call")
        return result

    return wrapper


@my_decorator
def greet(name: str) -> None:
    print(f"Hello, {name}!")


greet("Alice")
