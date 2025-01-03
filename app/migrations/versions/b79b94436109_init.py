"""init

Revision ID: b79b94436109
Revises:
Create Date: 2024-12-22 14:55:10.479669

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'b79b94436109'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    from sqlalchemy.sql import text
    conn = op.get_bind()
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
