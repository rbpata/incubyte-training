import asyncio
import pytest


@pytest.mark.asyncio
async def test_asyncio():
    await asyncio.sleep(1)
    assert True
