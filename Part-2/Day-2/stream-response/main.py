from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()


async def generator():
    for i in range(5):
        yield f"chunk {i}\n"
        await asyncio.sleep(1)


@app.get("/stream")
async def stream():
    return StreamingResponse(generator(), media_type="text/plain")