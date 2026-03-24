import asyncio


# coroutine function doesnt get executed directly
# coroutine
async def main():
    await asyncio.sleep(2)
    print("Hello, World!")


async def first():
    print("start coroutine")
    result = main()
    print("end coroutine")
    result = await result


asyncio.run(first())
