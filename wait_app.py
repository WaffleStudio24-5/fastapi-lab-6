import asyncio
import time

from fastapi import FastAPI

app = FastAPI(title="6주차 — 대기 방식 비교")


@app.get("/ping")
async def ping():
    return {"message": "pong"}


@app.get("/wait-sync")
def wait_sync():
    time.sleep(2)
    return {"message": "완료"}


@app.get("/wait-async")
async def wait_async():
    await asyncio.sleep(2)
    return {"message": "완료"}


@app.get("/wait-blocking")
async def wait_blocking():
    # 실습에서 관찰한 뒤 수정할 블로킹 코드다.
    time.sleep(2)
    return {"message": "완료"}
