my_list = [1, 2, 3, 4, 5]

# BAD: len() called every iteration

for i in range(len(my_list)):  # len() is O(1) but called n times
    ...

# GOOD: compute once
n = len(my_list)
for i in range(n):
    ...

# BAD: attribute lookup inside tight loop
import math

data = [1, 4, 9, 16, 25]
for x in data:
    result = math.sqrt(x)  # Python looks up math, then sqrt, every time

# GOOD: bind the function once
sqrt = math.sqrt
for x in data:
    result = sqrt(x)  # one lookup


# BAD: append in loop
result = []
for x in data:
    if x > 0:
        result.append(x * 2)

# GOOD: list comprehension
# ~30% faster — interpreted as
# a single C-level operation
result = [x * 2 for x in data if x > 0]


# BAD: global lookup every iteration
THRESHOLD = 100


def process(data):
    return [x for x in data if x > THRESHOLD]  # global lookup


# GOOD: copy to local variable
def process(data):
    threshold = THRESHOLD  # local — faster lookup
    return [x for x in data if x > threshold]


words = ["hello", "world", "this", "is", "a", "test"]

# BAD: O(n²) — creates a new string object every iteration
result = ""
for word in words:
    result += word + " "

# GOOD: O(n) — join builds it all at once
result = " ".join(words)
