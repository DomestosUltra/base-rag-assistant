"""create dialogue records table

Revision ID: 20260311_0001
Revises:
Create Date: 2026-03-11
"""

from alembic import op
import sqlalchemy as sa


revision = "20260311_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dialogue_records",
        sa.Column("id", sa.Uuid(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("request_text", sa.Text(), nullable=False),
        sa.Column("response_text", sa.Text(), nullable=False),
        sa.Column("request_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_dialogue_records_user_id", "dialogue_records", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_dialogue_records_user_id", table_name="dialogue_records")
    op.drop_table("dialogue_records")
