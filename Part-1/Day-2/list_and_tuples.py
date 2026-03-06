# working with the list
from collections import deque


l = [1, 2, 3, 4, 3]
print(l)
l.append(39)
print(l)
print(l.index(39))
print(l.count(3))
print(l.pop())
print(l)

print(l.reverse())
print(l.sort())


queue = deque([1, 2, 3, 4, 3])

queue.append(2)
print(queue)
print(queue.popleft())
print(queue.pop())


# l comprehension

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


#transpose of a matrix
matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
transpose = [[ row[i] for row in matrix] for i in range(3)]
print(transpose)