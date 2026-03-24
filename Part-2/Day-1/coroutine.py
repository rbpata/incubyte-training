import asyncio
import json
import time
import urllib.request


def blocking_get(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=8) as resp:
        return json.loads(resp.read())


class RunWindow:
    async def __aenter__(self):
        self.start = time.perf_counter()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        elapsed = time.perf_counter() - self.start
        print(f"completed in {elapsed:.2f}s")


async def api_jobs():
    sources = [
        ("post", "https://jsonplaceholder.typicode.com/posts/1"),
        ("user", "https://jsonplaceholder.typicode.com/users/1"),
        ("todo", "https://jsonplaceholder.typicode.com/todos/1"),
        ("bad", "https://jsonplaceholder.typicode.com/invalid/1"),
    ]
    for source in sources:
        await asyncio.sleep(0)
        yield source


async def fetch_one(name: str, url: str, limiter: asyncio.Semaphore) -> dict:
    async with limiter:
        data = await asyncio.to_thread(blocking_get, url)
        return {"name": name, "id": data.get("id"), "keys": len(data)}


def runtime_choice(workload: str) -> str:
    options = {
        "io": "asyncio",
        "blocking_io": "threading",
        "cpu": "multiprocessing",
    }
    return options.get(workload, "asyncio")


async def main():
    limiter = asyncio.Semaphore(2)
    coroutines = [fetch_one(name, url, limiter) async for name, url in api_jobs()]
    async with RunWindow():
        results = await asyncio.gather(*coroutines, return_exceptions=True)
    ok = [item for item in results if not isinstance(item, Exception)]
    err = [str(item) for item in results if isinstance(item, Exception)]
    print("successful:", ok)
    print("failed:", err)
    print("use for io:", runtime_choice("io"))
    print("use for blocking io:", runtime_choice("blocking_io"))
    print("use for cpu:", runtime_choice("cpu"))


if __name__ == "__main__":
    asyncio.run(main())
