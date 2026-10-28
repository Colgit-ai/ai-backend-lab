"""add conversation id

Revision ID: 37fc8b7d9d05
Revises: 071baddba380
Create Date: 2026-10-23 21:51:50.604527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37fc8b7d9d05'
down_revision: Union[str, Sequence[str], None] = '071baddba380'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    # 1. Add the column as nullable so existing rows remain valid.
    op.add_column(
        "conversations",
        sa.Column("conversation_id", sa.String(length=36), nullable=True),
    )

    # 2. Give each existing row its own conversation ID.
    # Existing records remain accessible and are treated as separate conversations.
    op.execute(
        """
        UPDATE conversations
        SET conversation_id = gen_random_uuid()::text
        WHERE conversation_id IS NULL
        """
    )

    # 3. Enforce the NOT NULL constraint after backfilling.
    op.alter_column(
        "conversations",
        "conversation_id",
        existing_type=sa.String(length=36),
        nullable=False,
    )

    # 4. Index conversation IDs for efficient retrieval.
    op.create_index(
        op.f("ix_conversations_conversation_id"),
        "conversations",
        ["conversation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_conversations_conversation_id"),
        table_name="conversations",
    )
    op.drop_column("conversations", "conversation_id")
