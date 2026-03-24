import asyncio
import json
import urllib.request


def _blocking_get(url: str) -> dict:
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


async def fetch(name: str, url: str) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _blocking_get, url)


async def main():
    urls = [
        ("Post", "https://jsonplaceholder.typicode.com/posts/1"),
        ("User", "https://jsonplaceholder.typicode.com/users/1"),
        ("Todo", "https://jsonplaceholder.typicode.com/todos/1"),
    ]

    result = await asyncio.gather(*[fetch(name, url) for name, url in urls])
    for item in result:
        print(item)


asyncio.run(main())
