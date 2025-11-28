from __future__ import annotations

from typing import Dict, List

from fastapi import Depends, FastAPI
from sqlmodel import Session

from . import crud
from .dependencies import get_session
from .models import EventRead

app = FastAPI(title="Inventory Service", version="0.1.0")


@app.get("/healthz", response_model=dict)
def health_check() -> Dict[str, str]:
    return {"service": "inventory", "status": "ok"}


@app.get("/events", response_model=List[EventRead])
def list_events(session: Session = Depends(get_session)) -> List[EventRead]:
    return crud.list_events(session)
