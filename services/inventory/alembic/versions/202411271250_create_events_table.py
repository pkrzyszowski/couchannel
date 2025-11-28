"""create viewing sessions table"""

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy import column, table

revision = "202411271250"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "viewing_sessions",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("slots_total", sa.Integer(), nullable=False),
        sa.Column("slots_available", sa.Integer(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=False),
    )

    now = datetime.now(UTC)
    sample_events = [
        {
            "id": str(uuid4()),
            "title": "Champions League Watch",
            "starts_at": now + timedelta(hours=48),
            "slots_total": 6,
            "slots_available": 4,
            "location": "Warszawa, Śródmieście",
        },
        {
            "id": str(uuid4()),
            "title": "NBA Sunday",
            "starts_at": now + timedelta(hours=72),
            "slots_total": 8,
            "slots_available": 7,
            "location": "Kraków, Kazimierz",
        },
    ]
    events_table = table(
        "viewing_sessions",
        column("id", sa.String()),
        column("title", sa.String()),
        column("starts_at", sa.DateTime(timezone=True)),
        column("slots_total", sa.Integer()),
        column("slots_available", sa.Integer()),
        column("location", sa.String()),
    )
    op.bulk_insert(events_table, sample_events)


def downgrade() -> None:
    op.drop_table("viewing_sessions")
