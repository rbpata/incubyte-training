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

empty = ()
singleton = (1,)
print(type(empty))
print(type(singleton))


set_a = {1, 2, 3, 4, 5}
set_b = {4, 5, 6, 7, 8}

print(set_a.union(set_b))
print(set_a.intersection(set_b))
print(set_a.difference(set_b))

dict_a = {'a': 1, 'b': 2, 'c': 3}
print(dict_a)
print(dict_a['a'])
dict_a['d'] = 4
print(dict_a)
print(dict_a.keys())
print(dict_a.values())
print(dict_a.items())

dict_b = {k: v**2 for k,v in dict_a.items()}
print(dict_b)

dict_a['dict2'] = dict_b
print(dict_a)


# string formatting
print("Hello, {}".format("Ram"))
print("The value of pi is approximately {:.2f}".format(3.14159))

name = "Ram"
print(f"Hello, {name}")


l2 = [1,2,3,4,5]

even = [x if x%2==0 else 0 for x in l2]
print(even)