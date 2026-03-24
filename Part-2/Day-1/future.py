import asyncio


async def set_future_result(future, value):
    await asyncio.sleep(2)

    future.set_result(value)
    print("set the future's result to:", value)


async def main():
    loop = asyncio.get_event_loop()
    future = loop.create_future()

    asyncio.create_task(set_future_result(future, "Hello, Future!"))
    await future


asyncio.run(main())

