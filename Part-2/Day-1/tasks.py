import asyncio


async def create_func(id, sleep_time):
    print("Funtion Started")
    await asyncio.sleep(sleep_time)
    print(f"Function {id} completed")


async def main():
    task1 = asyncio.create_task(create_func(1, 2))
    task2 = asyncio.create_task(create_func(2, 1))
    await task1
    await task2
    print("All functions completed")


asyncio.run(main())
