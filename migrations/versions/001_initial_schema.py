"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-25 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "chats",
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("username", sa.String(length=32), nullable=True),
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("users")
    op.drop_table("chats")
