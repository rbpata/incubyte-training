import asyncio
import time
from collections import deque


class RateLimiter:
    def __init__(self, limit: int, interval: float):
        self.limit = limit
        self.interval = interval
        self.calls = deque()
        self.lock = asyncio.Lock()

    async def acquire(self):
        while True:
            async with self.lock:
                now = time.monotonic()
                while self.calls and now - self.calls[0] >= self.interval:
                    self.calls.popleft()
                if len(self.calls) < self.limit:
                    self.calls.append(now)
                    return
                wait_for = self.interval - (now - self.calls[0])
            await asyncio.sleep(wait_for)


async def fetch_data(task_id: int, limiter: RateLimiter):
    await limiter.acquire()
    start = time.strftime("%H:%M:%S")
    print(f"start task={task_id} at {start}")
    await asyncio.sleep(0.3)
    end = time.strftime("%H:%M:%S")
    print(f"done  task={task_id} at {end}")


async def main():
    limiter = RateLimiter(limit=3, interval=1.0)
    tasks = [fetch_data(i, limiter) for i in range(1, 11)]
    await asyncio.gather(*tasks)


asyncio.run(main())