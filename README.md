# FastAPI 6주차 실습

5주차를 마친 동기 CRUD가 출발 코드입니다. 학생이 직접 다음 두 작업을 합니다.

1. `/health`와 게시글 CRUD 5개를 Router → Service → Repository → DB I/O까지 비동기로 전환합니다.
2. 같은 작성자의 동시 작성 요청에도 게시글이 3개를 넘지 않도록 트랜잭션과 MySQL 행 잠금을 적용합니다.

단계별 설명과 힌트: [6주차 실습 노션](https://app.notion.com/p/41adf97f0257816b8403c67aabd2d567)

## 시작

저장소 루트에서 실행합니다. Python 3.12, uv, Docker가 필요합니다.

```bash
uv sync --locked
cp -n .env.example .env
unset DATABASE_URL
```

기본 DB는 `127.0.0.1:3308/seminar_lab6`입니다. 기존 `.env`가 있으면 **아래 명령을 실행하기 전에** `.env.example`과 비교해 DB 주소를 맞춥니다.

```bash
docker compose up -d --wait
uv run alembic upgrade head
uv run python seed.py
uv run pytest -q tests validation
uv run uvicorn app.main:app --reload
```

초기 데이터를 이미 넣었다면 `seed.py`는 건너뜁니다. Swagger는 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)에서 확인합니다. 출발 코드의 회귀 테스트 기준은 **18 passed**입니다.

`.env`의 `DATABASE_URL`은 `mysql+pymysql://...`을 유지합니다. 준비 스크립트와 Alembic이 사용하는 동기 연결입니다. 앱의 비동기 URL은 `make_url(...).set(drivername="mysql+asyncmy")`로 파생합니다.

## 비동기 전환 확인

앱 전환 후, 제공된 비동기 DB fixture로 교체합니다. 기존 테스트의 요청과 응답 검증은 유지합니다.

```bash
cp scripts/async_conftest.py tests/conftest.py
uv run python scripts/check_async.py
uv run pytest -q tests validation
```

구조 검사는 출발 코드에서 실패하는 것이 정상입니다. `check_async.py`는 함수와 세션 구성을 확인하며, 실제 SQL의 비동기 실행 여부는 코드와 CRUD 테스트로 함께 확인합니다.

## 동시 작성 확인

MySQL과 서버를 켜 둔 채 다른 터미널에서 실행합니다.

```bash
uv run python scripts/check_concurrency.py --expect race
```

락이 없으면 두 요청이 모두 201을 받고 최종 글 수가 4개가 될 수 있습니다. 관측되지 않으면 노션의 재현용 대기 안내를 따릅니다.

작성자 행을 먼저 잠그고, 같은 트랜잭션에서 COUNT와 INSERT를 수행한 뒤 확인합니다.

```bash
uv run python scripts/check_concurrency.py --expect locked --attempts 10
```

매회 응답은 `[201, 409]`, 최종 글 수는 3개여야 합니다. 도구는 매회 임시 작성자와 글 2개를 만들고, 종료할 때 해당 데이터만 지웁니다. 서버와 도구가 같은 DB에 연결되어 있는지도 확인합니다. SQLite 테스트로는 MySQL의 행 잠금 동작을 검증할 수 없습니다.

실습을 마치면 재현용 `asyncio.sleep`을 지웁니다. DB를 종료할 때는 `docker compose down`을 사용합니다. `-v`를 붙이면 실습 데이터가 삭제됩니다.
