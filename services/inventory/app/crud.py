from __future__ import annotations

from typing import List

from sqlmodel import Session, select

from .models import Event


def list_events(session: Session) -> List[Event]:
    statement = select(Event).order_by(Event.starts_at)
    return list(session.exec(statement))
