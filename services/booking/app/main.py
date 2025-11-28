from __future__ import annotations

from datetime import datetime
from typing import Dict
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel


class BookingRequest(BaseModel):
    event_id: str
    guest_id: str
    seats: int = 1


class BookingResponse(BaseModel):
    booking_id: str
    status: str
    reserved_at: datetime


app = FastAPI(title="Booking Service", version="0.1.0")


@app.get("/healthz", response_model=dict)
def health_check() -> Dict[str, str]:
    return {"service": "booking", "status": "ok"}


@app.post("/bookings", response_model=BookingResponse, status_code=201)
def create_booking(payload: BookingRequest) -> BookingResponse:
    # TODO: orchestrate inventory, payments, compliance.
    return BookingResponse(
        booking_id=str(uuid4()),
        status="pending",
        reserved_at=datetime.utcnow(),
    )
