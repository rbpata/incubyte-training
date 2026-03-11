from typing import Optional, Callable, TypeVar, ParamSpec, Generator
import functools
import time


def fizzbuzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    return str(n)


for i in range(1, 21):
    print(fizzbuzz(i), end=" ")
print()


def calculate_grade(score: float) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    return "F"


grades: list[str] = [calculate_grade(s) for s in [95, 82, 67, 55, 91]]
print(f"Grades: {grades}")


def parse_student_record(raw: dict[str, str]) -> dict[str, str | int | float]:
    return {
        "name": raw["name"],
        "age": int(raw["age"]),
        "gpa": float(raw["gpa"]),
    }


sample_records: list[dict[str, str]] = [
    {"name": "Ram", "age": "22", "gpa": "3.8"},
    {"name": "Sahil", "age": "24", "gpa": "3.2"},
]
parsed: list[dict[str, str | int | float]] = [
    parse_student_record(r) for r in sample_records
]
print(f"Parsed: {parsed}")


class LibraryItem:
    def __init__(self, title: str, item_id: int) -> None:
        self.title: str = title
        self.item_id: int = item_id
        self._checked_out: bool = False

    def checkout(self) -> bool:
        if self._checked_out:
            return False
        self._checked_out = True
        return True

    def return_item(self) -> bool:
        if not self._checked_out:
            return False
        self._checked_out = False
        return True

    def __str__(self) -> str:
        status: str = "checked out" if self._checked_out else "available"
        return f"[{self.item_id}] {self.title} ({status})"


class Library:
    def __init__(self) -> None:
        self._items: list[LibraryItem] = []

    def add_item(self, item: LibraryItem) -> None:
        self._items.append(item)

    def find_by_title(self, title: str) -> Optional[LibraryItem]:
        for item in self._items:
            if item.title.lower() == title.lower():
                return item
        return None

    def available_items(self) -> list[LibraryItem]:
        return [item for item in self._items if not item._checked_out]


lib = Library()
lib.add_item(LibraryItem("Dune", 1))
lib.add_item(LibraryItem("1984", 2))
lib.add_item(LibraryItem("Sapiens", 3))

lib.find_by_title("Dune").checkout()  # type: ignore[union-attr]

print("\nLibrary items:")
for item in lib.available_items():
    print(f"  {item}")


P = ParamSpec("P")
R = TypeVar("R")


def timer(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start: float = time.perf_counter()
        result: R = func(*args, **kwargs)
        elapsed: float = time.perf_counter() - start
        print(f"[timer] {func.__name__} took {elapsed:.4f}s")
        return result

    return wrapper


@timer
def slow_sum(n: int) -> int:
    return sum(range(n))


print(f"\nSum: {slow_sum(1_000_000)}")


def fibonacci(limit: int) -> Generator[int, None, None]:
    a: int = 0
    b: int = 1
    while a < limit:
        yield a
        a, b = b, a + b


fib_numbers: list[int] = list(fibonacci(100))
print(f"\nFibonacci < 100: {fib_numbers}")
