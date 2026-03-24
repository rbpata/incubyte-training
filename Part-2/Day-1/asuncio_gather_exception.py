import asyncio


async def task_ok():
    await asyncio.sleep(1)
    return "ok"


async def task_fail():
    await asyncio.sleep(1)
    raise RuntimeError("failed")


async def main():
    results = await asyncio.gather(
        task_ok(),
        task_fail(),
        return_exceptions=True,
    )

    for result in results:
        if isinstance(result, Exception):
            print(f"Task error: {result}")
        else:
            print(f"Task result: {result}")


asyncio.run(main())
