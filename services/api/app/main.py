from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException
from httpx import AsyncClient, HTTPError
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator

from .auth import UserClaims, require_user
from .config import settings
from .http_client import close_http_client, get_http_client


class HealthResponse(BaseModel):
    service: str
    status: str


class HostProfile(BaseModel):
    user_id: str
    display_name: str
    reputation: float
    views: int = 0


class ViewingSessionDTO(BaseModel):
    id: str
    title: str
    starts_at: datetime
    slots_total: int
    slots_available: int
    location: str
    price_pln: int
    host: HostProfile

class TokenRequest(BaseModel):
    user_id: str
    scope: List[str] | None = None


app = FastAPI(title="couchannel API", version="0.1.0")
Instrumentator().instrument(app).expose(app)


@app.on_event("shutdown")
async def _shutdown() -> None:
    await close_http_client()


@app.get("/healthz", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse(service="api", status="ok")


@app.get("/", tags=["root"])
def root() -> Dict[str, str]:
    return {"message": "couchannel API online"}


@app.get("/events/aggregated", response_model=List[ViewingSessionDTO], tags=["events"])
async def aggregated_events(
    user: UserClaims = Depends(require_user),
    client: AsyncClient = Depends(get_http_client),
) -> List[ViewingSessionDTO]:
    if settings.auth_enabled and "read:events" not in user.scope:
        raise HTTPException(status_code=403, detail="Missing read:events scope")
    try:
        inventory_resp = await client.get(f"{settings.inventory_url}/events")
        inventory_resp.raise_for_status()
        events = inventory_resp.json()
        aggregated: List[ViewingSessionDTO] = []
        for event in events:
            host_resp = await client.get(f"{settings.identity_url}/profiles/{event['host_id']}")
            host_resp.raise_for_status()
            host_payload = host_resp.json()
            aggregated.append(
                ViewingSessionDTO(
                    id=event["id"],
                    title=event["title"],
                    starts_at=event["starts_at"],
                    slots_total=event["slots_total"],
                    slots_available=event["slots_available"],
                    location=event["location"],
                    price_pln=event["price_pln"],
                    host=HostProfile(**host_payload),
                )
            )
        return aggregated
    except HTTPError as exc:  # pragma: no cover - exercised via tests
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.post("/auth/token", tags=["auth"])
async def service_token(
    payload: TokenRequest,
    client: AsyncClient = Depends(get_http_client),
) -> Dict[str, object]:
    response = await client.post(
        f"{settings.identity_url}/auth/token", json=payload.model_dump()
    )
    response.raise_for_status()
    return response.json()
