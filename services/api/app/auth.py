from __future__ import annotations

import time
from typing import Any, Dict

from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from httpx import AsyncClient
from jose import jwt
from jose.exceptions import JWTError
from pydantic import BaseModel, Field

from .config import settings
from .http_client import get_http_client

security = HTTPBearer(auto_error=False)

_jwks_cache: Dict[str, Any] | None = None
_jwks_fetched_at: float = 0.0
_JWKS_TTL_SECONDS = 300


class UserClaims(BaseModel):
    sub: str
    scope: list[str] = Field(default_factory=list)


async def _fetch_jwks(client: AsyncClient) -> Dict[str, Any]:
    global _jwks_cache, _jwks_fetched_at
    now = time.time()
    if _jwks_cache and (now - _jwks_fetched_at) < _JWKS_TTL_SECONDS:
        return _jwks_cache
    response = await client.get(settings.oidc_jwks_url)
    response.raise_for_status()
    data = response.json()
    _jwks_cache = data
    _jwks_fetched_at = now
    return data


def _find_key(jwks: Dict[str, Any], kid: str) -> Dict[str, Any]:
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    raise HTTPException(status_code=401, detail="Unknown signing key")


async def require_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
    client: AsyncClient = Depends(get_http_client),
) -> UserClaims:
    if not settings.auth_enabled:
        return UserClaims(sub="anonymous", scope=["read:events"])
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = credentials.credentials
    jwks = await _fetch_jwks(client)
    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Invalid token header")
    key = _find_key(jwks, kid)
    try:
        payload = jwt.decode(
            token,
            key,
            algorithms=[settings.oidc_algorithm],
            audience=settings.oidc_audience,
            issuer=settings.oidc_issuer,
        )
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    scope = payload.get("scope")
    if isinstance(scope, str):
        scopes = scope.split()
    elif isinstance(scope, list):
        scopes = scope
    else:
        scopes = []
    return UserClaims(sub=str(payload.get("sub")), scope=scopes)
