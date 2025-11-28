import asyncio

from fakeredis import FakeServer, aioredis
from fastapi.testclient import TestClient

from services.identity.app.cache import get_cache
from services.identity.app.main import app

SERVER = FakeServer()


async def override_get_cache():
    return aioredis.FakeRedis(server=SERVER, decode_responses=True)


app.dependency_overrides[get_cache] = override_get_cache


def _reset_cache() -> None:
    asyncio.run(aioredis.FakeRedis(server=SERVER, decode_responses=True).flushall())


def test_touch_profile_increments_views() -> None:
    _reset_cache()
    client = TestClient(app)

    touch_resp = client.post("/profiles/alice/touch")
    assert touch_resp.status_code == 200
    assert touch_resp.json()["views"] == 1

    profile_resp = client.get("/profiles/alice")
    assert profile_resp.status_code == 200
    assert profile_resp.json()["views"] == 1
