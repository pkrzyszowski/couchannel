from __future__ import annotations

from typing import Dict

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from redis.asyncio import Redis

from .cache import close_cache, get_cache


class Profile(BaseModel):
    user_id: str
    display_name: str
    reputation: float
    views: int = 0


app = FastAPI(title="Identity Service", version="0.1.0")


@app.on_event("shutdown")
async def _shutdown() -> None:
    await close_cache()


@app.get("/healthz", response_model=dict)
async def health_check() -> Dict[str, str]:
    return {"service": "identity", "status": "ok"}


def _profile_views_key(user_id: str) -> str:
    return f"profile:{user_id}:views"


@app.get("/profiles/{user_id}", response_model=Profile)
async def get_profile(user_id: str, cache: Redis = Depends(get_cache)) -> Profile:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
    key = _profile_views_key(user_id)
    views = int(await cache.get(key) or 0)
    return Profile(user_id=user_id, display_name=f"User {user_id}", reputation=4.85, views=views)


@app.post("/profiles/{user_id}/touch", response_model=Profile)
async def touch_profile(user_id: str, cache: Redis = Depends(get_cache)) -> Profile:
    key = _profile_views_key(user_id)
    views = int(await cache.incr(key))
    return Profile(user_id=user_id, display_name=f"User {user_id}", reputation=4.85, views=views)
