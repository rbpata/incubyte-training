import asyncio


async def fetch_data(id, sleep_time):
    print(f"Fetching data for function {id}")
    await asyncio.sleep(sleep_time)
    print(f"Data fetched for function {id}")
    return f"Data from function {id}"


# async def main():

#     results = await asyncio.gather(fetch_data(1, 2), fetch_data(2, 1))
#     for result in results:
#         print(f"Result Received: {result}")


async def main():
    tasks = []
    async with asyncio.TaskGroup() as tg:
        for i, sleep_time in enumerate([2, 1, 3], start=1):
            task = tg.create_task(fetch_data(i, sleep_time))
            tasks.append(task)
    results = [task.result() for task in tasks]


asyncio.run(main())
