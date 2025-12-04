from __future__ import annotations

from datetime import datetime
from typing import Dict
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, SQLModel
from prometheus_fastapi_instrumentator import Instrumentator

from .database import engine
from .dependencies import get_session
from .events import publish_booking_event, start_event_bus, stop_event_bus
from .models import BookingRead, BookingRecord


class BookingRequest(BaseModel):
    event_id: str
    guest_id: str
    seats: int = 1


class BookingUpdate(BaseModel):
    status: str


app = FastAPI(title="Booking Service", version="0.1.0")
Instrumentator().instrument(app).expose(app)


@app.on_event("startup")
async def _startup() -> None:
    SQLModel.metadata.create_all(engine)
    await start_event_bus()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await stop_event_bus()


@app.get("/healthz", response_model=dict)
def health_check() -> Dict[str, str]:
    return {"service": "booking", "status": "ok"}


@app.post("/bookings", response_model=BookingRead, status_code=201)
async def create_booking(payload: BookingRequest, session: Session = Depends(get_session)) -> BookingRead:
    booking = BookingRecord(
        booking_id=str(uuid4()),
        status="pending",
        reserved_at=datetime.utcnow(),
        event_id=payload.event_id,
        guest_id=payload.guest_id,
        seats=payload.seats,
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    await publish_booking_event(
        {
            "booking_id": booking.booking_id,
            "event_id": booking.event_id,
            "guest_id": booking.guest_id,
            "seats": booking.seats,
            "status": booking.status,
            "reserved_at": booking.reserved_at.isoformat(),
        }
    )
    return BookingRead.model_validate(booking)


@app.patch("/bookings/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_id: str,
    payload: BookingUpdate,
    session: Session = Depends(get_session),
) -> BookingRead:
    record = session.get(BookingRecord, booking_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    record.status = payload.status
    session.add(record)
    session.commit()
    session.refresh(record)
    await publish_booking_event(
        {
            "booking_id": record.booking_id,
            "event_id": record.event_id,
            "guest_id": record.guest_id,
            "seats": record.seats,
            "status": record.status,
            "reserved_at": record.reserved_at.isoformat(),
        }
    )
    return BookingRead.model_validate(record)
