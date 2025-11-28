from __future__ import annotations

from typing import Dict, List

from fastapi import Depends, FastAPI
from sqlmodel import Session

from . import crud
from .dependencies import get_session
from .events import start_event_consumer, stop_event_consumer
from .models import ViewingSessionRead

app = FastAPI(title="Inventory Service", version="0.1.0")


@app.on_event("startup")
async def _startup() -> None:
    await start_event_consumer()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await stop_event_consumer()


@app.get("/healthz", response_model=dict)
def health_check() -> Dict[str, str]:
    return {"service": "inventory", "status": "ok"}


@app.get("/events", response_model=List[ViewingSessionRead])
def list_events(session: Session = Depends(get_session)) -> List[ViewingSessionRead]:
    return crud.list_events(session)
