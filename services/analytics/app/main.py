from __future__ import annotations

from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlmodel import Session, SQLModel, select

from .database import engine
from .dependencies import get_session
from .events import start_event_consumer, stop_event_consumer
from .models import BookingStat, BookingStatRead

app = FastAPI(title="Analytics Service", version="0.1.0")
Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def _startup() -> None:
    SQLModel.metadata.create_all(engine)
    await start_event_consumer()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await stop_event_consumer()


@app.get("/healthz", response_model=dict)
def health_check() -> Dict[str, str]:
    return {"service": "analytics", "status": "ok"}


@app.get("/stats", response_model=List[BookingStatRead])
def list_stats(session: Session = Depends(get_session)) -> List[BookingStatRead]:
    results = session.exec(select(BookingStat).order_by(BookingStat.updated_at.desc()))
    return [BookingStatRead.model_validate(row) for row in results]


@app.get("/stats/{event_id}", response_model=BookingStatRead)
def stat_detail(event_id: str, session: Session = Depends(get_session)) -> BookingStatRead:
    stat = session.get(BookingStat, event_id)
    if stat is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return BookingStatRead.model_validate(stat)
