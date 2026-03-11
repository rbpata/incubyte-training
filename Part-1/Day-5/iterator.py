# iterator protocol


class BookSelf:
    def __init__(self, books):
        self._books = books

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self._books):
            raise StopIteration
        book = self._books[self._index]
        self._index = self._index + 1
        return book

    def __reversed__(self):

        self._index = len(self._books) - 1
        book = self._books[self._index]
        return self


result = BookSelf(["Book1", "Book2"])
result2 = BookSelf(["Book1", "Book2"])

for i in result:
    print(i)

for i in reversed(result2):
    print(i)


# ITERABLE   — has __iter__, produces iterators
#              can be looped over multiple times
# ITERATOR   — has __iter__ + __next__, tracks position
#              exhausted after one pass

numbers = [1, 2, 3]  # iterable — loop it infinite times

it = iter(numbers)  # iterator — one-time use
print(list(it))  # [1, 2, 3]
print(list(it))  # []  ← exhausted!

# Generators are iterators — one-time use
gen = (x**2 for x in range(3))
print(list(gen))  # [0, 1, 4]
print(list(gen))  # []  ← exhausted!


# custom myrange iterator
class MyRange:
    def __init__(self, start, end, step):
        self.start = start
        self.end = end
        self.step = step

    def __iter__(self):
        self.current = self.start
        return self

    def __next__(self):
        if self.current >= self.end:
            raise StopIteration
        current = self.current
        self.current += self.step
        return current


for i in MyRange(0, 10, 2):
    print(i)
