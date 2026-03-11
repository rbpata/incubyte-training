# syntax difference is only of () and []

square_list = [x**2 for x in range(10)]
square_gen = (x**2 for x in range(10))

print(square_list)
for i in square_gen:
    print(i)


#actual difference

import sys

# List — stores ALL values in memory
numbers_list = [x for x in range(100_000)]
print(sys.getsizeof(numbers_list))   

# Generator — stores NO values, just the recipe
numbers_gen  = (x for x in range(100_000))
print(sys.getsizeof(numbers_gen)) 