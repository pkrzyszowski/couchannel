from __future__ import annotations

from datetime import datetime

from sqlmodel import Field, SQLModel


class BookingRecord(SQLModel, table=True):
    __tablename__ = "booking_records"

    booking_id: str = Field(primary_key=True)
    event_id: str
    guest_id: str
    seats: int = 1
    status: str = Field(default="pending")
    reserved_at: datetime


class BookingRead(SQLModel):
    booking_id: str
    event_id: str
    guest_id: str
    seats: int
    status: str
    reserved_at: datetime

    model_config = {"from_attributes": True}
