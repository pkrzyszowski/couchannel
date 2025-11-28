from __future__ import annotations

import httpx

_client: httpx.AsyncClient | None = None


async def get_http_client() -> httpx.AsyncClient:
    """Return a shared AsyncClient instance."""

    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=10.0)
    return _client


async def close_http_client() -> None:
    if _client is not None:
        await _client.aclose()
