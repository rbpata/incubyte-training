# working with the list
from collections import deque


list = [1, 2, 3, 4, 3]
print(list)
list.append(39)
print(list)
print(list.index(39))
print(list.count(3))
print(list.pop())
print(list)

print(list.reverse())
print(list.sort())


queue = deque([1, 2, 3, 4, 3])

queue.append(2)
print(queue)
print(queue.popleft())
print(queue.pop())


# list comprehension

square = []
for i in range(10):
    square.append(i**2)
print(square)

# or

square = [i**2 for i in range(10)]
print(square)

# or
square = list(map(lambda x: x**2, range(10)))
print(square)

pairs = [(x, y) for x in [2, 3, 4] for y in [1, 2, 3] if x != y]
print(pairs)
