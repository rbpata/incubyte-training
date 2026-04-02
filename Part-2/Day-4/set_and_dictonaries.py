items = list(range(1_000_000))

# Scans up to 1M elements
if 999_999 in items:  # slow
    ...

# Typical: ~50ms for 1M items
# Every lookup is the same cost

items = set(range(1_000_000))

# Hash jump — ignores 999,999 items
if 999_999 in items:  # fast
    ...

# Typical: ~0.05ms regardless of size
# 1000× faster on large collections


users = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}, ...]


# BAD: O(n) per lookup — n lookups = O(n²) total
def get_user(user_id):
    for u in users:  # scans every time
        if u["id"] == user_id:
            return u


# GOOD: build index once O(n), then O(1) per lookup
user_index = {u["id"]: u for u in users}  # build once


def get_user(user_id):
    return user_index.get(user_id)  # O(1) every time




