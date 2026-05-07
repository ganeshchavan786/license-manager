"""Add pause/resume columns to licenses table

Revision ID: 007
Revises: 006
Create Date: 2026-05-07 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    # licenses table मध्ये pause/resume columns add करा
    with op.batch_alter_table('licenses') as batch_op:
        batch_op.add_column(sa.Column('is_paused', sa.Boolean(), nullable=True, server_default='0'))
        batch_op.add_column(sa.Column('paused_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('pause_days_remaining', sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table('licenses') as batch_op:
        batch_op.drop_column('pause_days_remaining')
        batch_op.drop_column('paused_at')
        batch_op.drop_column('is_paused')
