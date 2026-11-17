# 실습 정답

먼저 직접 TODO를 완성한 뒤 비교하세요.

## 블로킹 대기 수정

wait_app.py의 wait_blocking 함수만 다음과 같이 바꿉니다.

```python
@app.get("/wait-blocking")
async def wait_blocking():
    await asyncio.sleep(2)
    return {"message": "완료"}
```

서버를 다시 시작하고 measure.py와 probe.py를 실행합니다.

## 비동기 게시글 조회

이 폴더의 repositories.py, services.py, routers.py가 각 TODO 파일의 전체 정답입니다. imports는 async_lab을 기준으로 작성되어 있습니다.

비교 후 적용하려면 저장소 루트에서 실행합니다.

```bash
cp solutions/repositories.py async_lab/repositories.py
cp solutions/services.py async_lab/services.py
cp solutions/routers.py async_lab/routers.py
```

위 명령은 해당 TODO 파일을 덮어씁니다. 직접 작성한 내용을 보존하려면 먼저 커밋하거나 파일을 비교해 수정합니다.

tests/test_async_exercises.py의 @pytest.mark.skip(...) 한 줄을 삭제한 뒤 uv run pytest -q를 실행하면 14 passed가 나와야 합니다. MySQL과 서버를 실행한 상태에서는 uv run python check_posts.py로 실제 DB 연결도 확인합니다.
