"""add host metadata to viewing sessions"""

import sqlalchemy as sa
from alembic import op

revision = "202411271330"
down_revision = "202411271250"
branch_labels = None
depends_on = None

HOST_DEFAULT = "host-001"
PRICE_DEFAULT = 80


def upgrade() -> None:
    op.add_column("viewing_sessions", sa.Column("host_id", sa.String(length=64), nullable=False, server_default=HOST_DEFAULT))
    op.add_column("viewing_sessions", sa.Column("price_pln", sa.Integer(), nullable=False, server_default=str(PRICE_DEFAULT)))

    # Example enrichment for existing rows
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE viewing_sessions SET host_id = :host_id, price_pln = :price"
        ),
        {"host_id": HOST_DEFAULT, "price": PRICE_DEFAULT},
    )

    op.alter_column("viewing_sessions", "host_id", server_default=None)
    op.alter_column("viewing_sessions", "price_pln", server_default=None)


def downgrade() -> None:
    op.drop_column("viewing_sessions", "price_pln")
    op.drop_column("viewing_sessions", "host_id")
