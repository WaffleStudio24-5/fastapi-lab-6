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
        assert response.json() == {"message": "pong"}

        for path in ("/wait-sync", "/wait-async", "/wait-blocking"):
            start = perf_counter()
            responses = await asyncio.gather(
                *(client.get(path) for _ in range(3))
            )
            elapsed = perf_counter() - start
            for response in responses:
                response.raise_for_status()
                assert response.json() == {"message": "완료"}
            print(f"{path}: {elapsed:.2f}초 / HTTP 200 × 3")


if __name__ == "__main__":
    asyncio.run(main())
