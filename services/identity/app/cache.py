from __future__ import annotations

import redis.asyncio as redis

from .config import settings

_cache: redis.Redis | None = None


def _build_client() -> redis.Redis:
    return redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)


async def get_cache() -> redis.Redis:
    """Return a Redis client, connecting lazily on first use."""

    global _cache
    if _cache is None:
        _cache = _build_client()
    return _cache


async def close_cache() -> None:
    """Close Redis connections during application shutdown."""

    if _cache is not None:
        await _cache.close()
