import asyncio


class CustomContextManager:
    def __enter__(self):
        print("entering the context")
        return self

    def __exit__(self, exc_type, exc, tb):
        print("exiting the context")


# with CustomContextManager() as cm:
#     pass


class AsyncContextManager:
    async def __aenter__(self):
        print("entering the async context")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        print("exiting the async context")


async def main():
    async with AsyncContextManager():
        print("async development")


asyncio.run(main())
