from __future__ import annotations

from typing import List

from sqlmodel import Session, select

from .models import ViewingSession


def list_events(session: Session) -> List[ViewingSession]:
    statement = select(ViewingSession).order_by(ViewingSession.starts_at)
    return list(session.exec(statement))
