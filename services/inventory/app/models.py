from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    __tablename__ = "events"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True, index=True)
    title: str
    starts_at: datetime
    slots_total: int
    slots_available: int
    location: str
    host_id: str = Field(index=True)
    price_pln: int = Field(default=0, ge=0)


class EventRead(SQLModel):
    id: str
    title: str
    starts_at: datetime
    slots_total: int
    slots_available: int
    location: str
    host_id: str
    price_pln: int

    model_config = {
        "from_attributes": True,
    }
