# FastAPI 6주차 실습

5주차 실습을 끝내지 않았어도 이 저장소만 받아서 시작할 수 있습니다.

**완성된 동기 CRUD·Router/Service/Repository·사용자당 글 3개 제한·테스트·모델·migration·초기 데이터**가 포함되어 있습니다. 5주차 파일이나 DB를 복사하지 않습니다.

이번 실습에서는 다음 두 가지를 직접 수정합니다.

1. `wait_app.py`의 블로킹 대기 수정
2. `async_lab/`의 TODO 1~3 — 게시글 단건 조회를 비동기로 연결

[6주차 이론](https://app.notion.com/p/409df97f025780138f87e5c5853145f8) · [실습 자료](https://app.notion.com/p/41adf97f0257816b8403c67aabd2d567)

## 0. 준비

macOS 또는 WSL, Python 3.12, uv를 사용합니다. 1~2단계에는 Docker와 DB가 필요하지 않습니다.

```bash
git clone https://github.com/WaffleStudio24-5/fastapi-lab-6.git
cd fastapi-lab-6
uv sync --locked
uv run pytest -q
```

초기 예상 결과는 **13 passed, 1 skipped**입니다. skip 1개는 TODO 1~3을 마친 뒤 실행할 테스트입니다. 이전 주차 진행 상태는 이 결과에 영향을 주지 않습니다.

### 파일 안내

| 경로 | 역할 | 학생이 수정할 곳 |
| --- | --- | --- |
| `app/` | 완성된 동기 CRUD와 공통 모델·설정·스키마 | 수정할 필요 없음 |
| `wait_app.py` | 세 가지 대기 방식 비교 | wait_blocking |
| `measure.py` | 요청 3개 동시 전송 | 제공 코드 |
| `probe.py` | 느린 요청 중 /ping 지연 확인 | 제공 코드 |
| `async_lab/database.py`, `main.py` | 비동기 세션 주입과 앱 실행 | 제공 코드 |
| `async_lab/repositories.py` | DB 조회 | TODO 1 |
| `async_lab/services.py` | Repository 호출 | TODO 2 |
| `async_lab/routers.py` | Service 호출과 HTTP 응답 | TODO 3 |
| `check_posts.py` | 실행 중인 비동기 API 확인 | 제공 코드 |
| `tests/` | 임시 SQLite를 사용하는 테스트 | 마지막에 skip 줄 하나 삭제 |
| `solutions/` | TODO 1~3 정답과 대기 수정 해설 | 막히면 참고 |

## 1. 세 가지 대기 방식 비교

첫 번째 터미널에서 다음 서버를 실행합니다.

```bash
uv run uvicorn wait_app:app --host 127.0.0.1 --port 8006 --workers 1
```

[문서](http://127.0.0.1:8006/docs)와 [ping](http://127.0.0.1:8006/ping)을 확인합니다.

서버를 켜 둔 채 **두 번째 터미널**을 열고, 같은 저장소 폴더에서 실행합니다.

```bash
uv run python measure.py
```

실행 전에 각 경로에 요청 3개를 동시에 보냈을 때 전체 시간을 예상해보세요.

| 경로 | 구현 | 초기 예상 시간 |
| --- | --- | --- |
| /wait-sync | def + time.sleep(2) | 약 2초 |
| /wait-async | async def + await asyncio.sleep(2) | 약 2초 |
| /wait-blocking | async def + time.sleep(2) | 약 6초 |

worker를 1개로 두고 reload 없이 비교합니다. 여러 worker를 쓰면 블로킹 현상이 가려질 수 있습니다. 시간은 로컬 시연의 예상값이며 벤치마크 기준이 아닙니다.

## 2. /ping 지연을 확인하고 수정

서버가 처음 제공한 코드로 실행 중인 상태에서 다음을 실행합니다.

```bash
uv run python probe.py
```

/wait-sync와 /wait-async가 진행 중일 때는 /ping이 거의 즉시 응답하고, /wait-blocking 중에는 약 1.8초 지연될 수 있습니다. 클라이언트가 느린 요청을 시작한 뒤 0.2초 기다려 /ping을 보내기 때문입니다. 실제 요청 도착 순서는 실행 환경에 따라 달라질 수 있습니다.

**할 일:** `wait_blocking`의 async def, 경로, 응답 JSON을 유지하면서 2초 대기 중 다른 요청을 처리하도록 고쳐보세요.

수정 후 서버를 Ctrl+C로 종료하고 같은 명령으로 다시 실행합니다. reload를 사용하지 않아 저장만으로 반영되지는 않습니다. measure.py와 probe.py를 다시 실행해 확인합니다.

완료 후에는 /wait-blocking의 동시 요청 3개도 약 2초에 끝나고 /ping이 거의 즉시 응답해야 합니다.

## 3. 이 저장소의 MySQL 준비

이제 Docker를 실행합니다. 6주차 MySQL은 **호스트 포트 3308, DB seminar_lab6, 별도 Docker 볼륨**을 사용합니다. 4·5주차 컨테이너나 데이터를 지우지 않아도 됩니다.

저장소 루트에서 실행합니다.

```bash
cp -n .env.example .env
unset DATABASE_URL
docker compose up -d --wait
uv run alembic upgrade head
uv run alembic check
uv run seed.py
```

- .env의 주소는 기존 앱과 migration이 함께 사용하는 동기 MySQL 주소입니다. async_lab이 같은 주소에서 드라이버를 asyncmy로 바꿔 별도 비동기 엔진을 만듭니다.
- `seed.py`는 **빈 DB에 한 번만** 실행합니다. 사용자 3명과 게시글 3개를 준비하며, 게시글 ID 1이 만들어집니다. 이미 사용자가 있으면 기존 데이터를 보존하고 오류를 내므로 이후에는 seed 명령을 건너뜁니다.
- 3308 포트를 다른 서비스가 쓴다면 `MYSQL_PORT=3309 docker compose up -d --wait`로 실행하고, .env 주소의 포트도 3309로 바꿉니다.
- 터미널에 DATABASE_URL을 export해 둔 경우 .env보다 우선합니다. 새 터미널에서도 확인하고, 필요한 경우 unset합니다.
- .env는 커밋하지 않습니다. 기본 비밀번호는 로컬 실습 전용입니다.

### 완성된 동기 앱 확인 — 선택

```bash
uv run uvicorn app.main:app --host 127.0.0.1 --port 8005
```

[동기 앱 문서](http://127.0.0.1:8005/docs)에서 /health와 게시글 CRUD를 확인할 수 있습니다. 이 앱은 5주차를 끝내지 못한 학생도 참고할 수 있는 완성 코드입니다. 추가 작성·삭제를 했다면 게시글 ID 1은 지우지 않고 다음 실습을 진행합니다.

## 4. 비동기 게시글 조회 완성

다음 세 파일의 TODO를 채웁니다. 공통 설정·모델·응답 스키마와 비동기 엔진 코드는 이미 들어 있습니다.

### TODO 1 — async_lab/repositories.py

- get_post를 async def로 바꿉니다.
- `select(Post).where(Post.id == post_id)`로 조회문을 만듭니다.
- `await self.db.scalars(...)`로 결과를 기다립니다.
- 받은 결과에서 one_or_none()으로 Post 또는 None을 반환합니다. 이 메서드에는 await를 붙이지 않습니다.

### TODO 2 — async_lab/services.py

get_post를 async def로 바꾸고, Repository의 결과를 await하여 반환합니다.

### TODO 3 — async_lab/routers.py

get_post를 async def로 바꾸고, Service의 결과를 await합니다. 없는 게시글의 404와 양수 ID 검증은 유지합니다.

다음 명령으로 실행합니다. TODO를 끝내기 전에도 서버는 시작되지만, 유효한 ID 조회는 NotImplementedError로 실패합니다.

```bash
uv run uvicorn async_lab.main:app --host 127.0.0.1 --port 8007 --workers 1
```

[비동기 앱 문서](http://127.0.0.1:8007/docs)에서 확인합니다. 이 앱에는 단건 조회만 등록되어 있습니다. 모든 CRUD를 비동기로 바꾸는 것은 필수 실습 범위가 아닙니다.

| 요청 | 기대 결과 |
| --- | --- |
| GET /posts/1 | 200, id·title·user_id |
| GET /posts/999999999 | 404, 게시글을 찾을 수 없습니다. |
| GET /posts/abc, /posts/0, /posts/-1 | 422 |

서버 코드를 수정했으면 재시작합니다.

### 완료 확인

`tests/test_async_exercises.py`의 **@pytest.mark.skip(...) 한 줄을 삭제**하고 실행합니다.

```bash
uv run pytest -q
```

완료 예상 결과는 **14 passed**, skip 없음입니다. 테스트는 임시 SQLite에서 실행되며 Docker나 .env가 없어도 됩니다. 일반 테스트와 비동기 조회 테스트 모두 실제 개발 DB 대신 별도 테스트 세션을 주입합니다.

MySQL에 연결해 실행한 비동기 서버도 별도로 확인합니다. 서버를 켜 둔 채 다른 터미널에서 실행하세요.

```bash
uv run python check_posts.py
```

예상 출력은 `성공 · 동시 조회 · 404 · 422 확인 완료`입니다. 이 제공 스크립트는 seed 데이터의 ID 1과 존재하지 않는 ID 999999999를 전제로 하며 읽기 요청만 보냅니다. 동시 응답 성공만으로 내부 DB 호출이 비동기임을 증명하지는 않으므로 코드의 호출 흐름도 확인합니다.

## 마치며

- [ ] def 엔드포인트도 동시 요청을 처리하는 이유를 설명할 수 있습니다.
- [ ] async def 안의 블로킹 대기가 /ping에 영향을 주는 것을 확인했습니다.
- [ ] 대기를 수정하고 서버를 재시작해 다시 비교했습니다.
- [ ] Router → Service → Repository → AsyncSession의 호출을 연결했습니다.
- [ ] await가 필요한 호출과 필요 없는 호출을 구분할 수 있습니다.
- [ ] pytest에서 14 passed를 확인하고 MySQL에서도 check_posts.py를 실행했습니다.

DB를 종료할 때는 `docker compose down`을 사용합니다. `docker compose down -v`는 6주차 DB 볼륨의 데이터를 삭제하므로 일반 종료에 사용하지 않습니다.

## 참고

동기 완성 코드는 [fastapi-lab-5](https://github.com/WaffleStudio24-5/fastapi-lab-5)의 모델·설정·migration과 5주차 수업의 계층 분리·작성 제한 예제를 바탕으로 구성했습니다. 작성 제한은 순차 요청 기준이며 동시 작성의 한도 보장은 이번 실습 범위가 아닙니다.

[FastAPI async/await](https://fastapi.tiangolo.com/async/) · [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
