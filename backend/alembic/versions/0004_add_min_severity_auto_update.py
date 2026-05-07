"""add min_severity to auto_update_settings

Revision ID: 0004
Revises: 0003
Create Date: 2026-05-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'auto_update_settings',
        sa.Column('min_severity', sa.String(length=20), nullable=False, server_default='high'),
    )


def downgrade() -> None:
    op.drop_column('auto_update_settings', 'min_severity')
