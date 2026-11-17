import asyncio
from time import perf_counter

import httpx


async def main():
    async with httpx.AsyncClient(
        base_url="http://127.0.0.1:8006",
        timeout=15.0,
        trust_env=False,
    ) as client:
        response = await client.get("/ping")
        response.raise_for_status()

        for path in ("/wait-sync", "/wait-async", "/wait-blocking"):
            slow = asyncio.create_task(client.get(path))
            try:
                await asyncio.sleep(0.2)
                start = perf_counter()
                response = await client.get("/ping")
                elapsed = perf_counter() - start
                response.raise_for_status()
                assert response.json() == {"message": "pong"}
                print(f"{path} 진행 중 /ping: {elapsed:.2f}초")
            finally:
                response = await slow
                response.raise_for_status()


if __name__ == "__main__":
    asyncio.run(main())
