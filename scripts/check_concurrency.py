"""실행 중인 로컬 서버에 같은 작성자의 글 작성 요청 두 개를 보낸다."""

import argparse
import asyncio
import sys
from pathlib import Path
from uuid import uuid4

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.settings import settings


async def send_pair(client, user_id, marker):
    barrier = asyncio.Barrier(3)

    async def send(label):
        await barrier.wait()
        return await client.post(
            "/posts", json={"title": f"{marker}-{label}", "user_id": user_id}
        )

    tasks = [asyncio.create_task(send(label)) for label in ("A", "B")]
    await barrier.wait()
    # 두 요청이 모두 끝난 뒤 정리한다. 한쪽 실패로 다른 요청을 남기지 않는다.
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    for response in responses:
        if isinstance(response, BaseException):
            raise response
    return responses


async def check(engine, base_url, attempts, expect):
    races = 0
    async with httpx.AsyncClient(base_url=base_url, timeout=60) as client:
        (await client.get("/health")).raise_for_status()
        for trial in range(1, attempts + 1):
            marker = "lab6-check-" + uuid4().hex
            user_id = None
            try:
                with engine.begin() as db:
                    result = db.execute(
                        text("INSERT INTO users (name, age) VALUES (:name, 23)"),
                        {"name": marker},
                    )
                    user_id = result.lastrowid
                    initial_titles = [f"{marker}-initial-{i}" for i in (1, 2)]
                    db.execute(
                        text("INSERT INTO posts (title, user_id) VALUES (:title, :user_id)"),
                        [{"title": title, "user_id": user_id} for title in initial_titles],
                    )

                # 다른 DB를 쓰는 서버에는 POST를 보내지 않는다.
                response = await client.get("/posts")
                response.raise_for_status()
                visible = [p for p in response.json() if p["user_id"] == user_id]
                if sorted(p["title"] for p in visible) != sorted(initial_titles):
                    raise RuntimeError(
                        "서버와 확인 도구가 같은 DB를 사용하는지 확인하세요. POST는 보내지 않았습니다."
                    )

                responses = await send_pair(client, user_id, marker)
                codes = sorted(r.status_code for r in responses)
                with engine.connect() as db:
                    count = db.scalar(
                        text("SELECT COUNT(*) FROM posts WHERE user_id = :user_id"),
                        {"user_id": user_id},
                    )
                print(f"{trial}/{attempts}: 응답 {codes}, 최종 글 {count}개")
                if codes == [201, 201] and count == 4:
                    races += 1
                elif codes != [201, 409] or count != 3:
                    raise AssertionError(
                        f"예상하지 못한 결과입니다: {[r.text for r in responses]}, 글 {count}개"
                    )
                if expect == "locked" and (codes != [201, 409] or count != 3):
                    raise AssertionError("동시 작성으로 글 3개 제한이 깨졌습니다.")
            finally:
                if user_id is not None:
                    with engine.begin() as db:
                        owner = db.scalar(
                            text("SELECT name FROM users WHERE id = :id FOR UPDATE"),
                            {"id": user_id},
                        )
                        if owner == marker:
                            db.execute(
                                text("DELETE FROM posts WHERE user_id = :id"), {"id": user_id}
                            )
                            db.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})

    if expect == "race":
        if not races:
            raise AssertionError(
                "경쟁 조건을 관측하지 못했습니다. 통과했다는 뜻은 아닙니다. "
                "시도 횟수를 늘리거나 실습 안내의 재현용 대기를 잠시 추가하세요."
            )
        print(f"경쟁 조건 관측: {races}/{attempts}회")
    else:
        print(f"PASS: {attempts}회 모두 한 요청만 성공하고 글은 3개입니다.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--attempts", type=int, default=5)
    parser.add_argument("--expect", choices=("race", "locked"), default="locked")
    args = parser.parse_args()
    if args.attempts < 1:
        parser.error("--attempts는 1 이상이어야 합니다.")
    url = make_url(settings.database_url)
    if url.get_backend_name() != "mysql":
        parser.error("행 잠금은 MySQL에서 확인합니다. DATABASE_URL을 확인하세요.")
    engine = create_engine(url.set(drivername="mysql+pymysql"))
    try:
        asyncio.run(check(engine, args.base_url, args.attempts, args.expect))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
