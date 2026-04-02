import numpy as np

data = list(range(1_000_000))
arr  = np.array(data)

# BAD: Python loop — ~200ms
result = [x ** 2 + 2 * x + 1 for x in data]

# GOOD: vectorised — ~3ms (66× faster)
result = arr ** 2 + 2 * arr + 1


# BAD
result = []
for x in data:
    if x > 0:
        result.append(x * 2)
    else:
        result.append(0)

# GOOD — np.where
result = np.where(arr > 0, arr * 2, 0)



# BAD
totals = []
running = 0
for x in data:
    running += x
    totals.append(running)

# GOOD — cumsum
totals = np.cumsum(arr)

# BAD: nested Python loop — O(n²), very slow
def pairwise_py(points):
    n = len(points)
    dists = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dists[i][j] = (dx**2 + dy**2)**0.5
    return dists

# GOOD: broadcasting — no Python loop
def pairwise_np(points):
    p = np.array(points)             # shape (n, 2)
    diff = p[:, None] - p[None, :]   # shape (n, n, 2)
    return np.sqrt((diff**2).sum(-1)) # shape (n, n)