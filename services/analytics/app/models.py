from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class BookingStat(SQLModel, table=True):
    __tablename__ = "booking_stats"

    event_id: str = Field(primary_key=True)
    total_seats: int = Field(default=0)
    total_bookings: int = Field(default=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class BookingStatRead(SQLModel):
    event_id: str
    total_seats: int
    total_bookings: int
    updated_at: datetime

    model_config = {"from_attributes": True}
