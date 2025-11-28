from __future__ import annotations

from datetime import datetime
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

from .events import publish_booking_event, start_event_bus, stop_event_bus


class BookingRequest(BaseModel):
    event_id: str
    guest_id: str
    seats: int = 1


class BookingResponse(BaseModel):
    booking_id: str
    status: str
    reserved_at: datetime


app = FastAPI(title="Booking Service", version="0.1.0")


@app.on_event("startup")
async def _startup() -> None:
    await start_event_bus()


@app.on_event("shutdown")
async def _shutdown() -> None:
    await stop_event_bus()


@app.get("/healthz", response_model=dict)
def health_check() -> Dict[str, str]:
    return {"service": "booking", "status": "ok"}


@app.post("/bookings", response_model=BookingResponse, status_code=201)
async def create_booking(payload: BookingRequest) -> BookingResponse:
    booking = BookingResponse(
        booking_id=str(uuid4()),
        status="pending",
        reserved_at=datetime.utcnow(),
    )
    await publish_booking_event(
        {
            "booking_id": booking.booking_id,
            "event_id": payload.event_id,
            "guest_id": payload.guest_id,
            "seats": payload.seats,
            "status": booking.status,
            "reserved_at": booking.reserved_at.isoformat(),
        }
    )
    return booking
