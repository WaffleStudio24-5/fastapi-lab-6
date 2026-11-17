import asyncio

import httpx


async def main():
    async with httpx.AsyncClient(
        base_url="http://127.0.0.1:8007",
        timeout=10.0,
        trust_env=False,
    ) as client:
        response = await client.get("/posts/1")
        response.raise_for_status()
        expected = response.json()
        assert expected["id"] == 1
        assert isinstance(expected["title"], str)
        assert isinstance(expected["user_id"], int)

        responses = await asyncio.gather(
            *(client.get("/posts/1") for _ in range(3))
        )
        for response in responses:
            assert response.status_code == 200
            assert response.json() == expected

        response = await client.get("/posts/999999999")
        assert response.status_code == 404
        assert response.json() == {"detail": "게시글을 찾을 수 없습니다."}

        for value in ("abc", "0", "-1"):
            response = await client.get(f"/posts/{value}")
            assert response.status_code == 422

        print("성공 · 동시 조회 · 404 · 422 확인 완료")


if __name__ == "__main__":
    asyncio.run(main())
