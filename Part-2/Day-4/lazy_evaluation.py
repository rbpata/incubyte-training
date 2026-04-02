# Eager — builds full list immediately
from multiprocessing import process


squares = [x**2 for x in range(1_000_000)]
# ~8 MB in memory

# Lazy — produces one value at a time
squares = (x**2 for x in range(1_000_000))
# ~128 bytes (just the generator object)

# Both work identically with sum(), for loops
total = sum(squares)

# Rule: if you only iterate once → use ()
# Rule: if you need random access  → use []


def read_chunks(path, size=8192):
    """Read a large file in chunks — never
    loads the whole file into memory."""
    with open(path, 'rb') as f:
        while chunk := f.read(size):
            yield chunk          # one chunk at a time

# Process a 10 GB file with constant memory
for chunk in read_chunks('big.log'):
    process(chunk)    # only one chunk in RAM at a time
    