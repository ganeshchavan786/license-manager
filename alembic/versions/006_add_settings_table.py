"""Add settings table for SMTP configuration

Revision ID: 006
Revises: 005
Create Date: 2026-05-05 18:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'settings',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('key', sa.String(100), nullable=False, unique=True),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('is_encrypted', sa.Boolean(), default=False),
        sa.Column('category', sa.String(50), nullable=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('updated_by', sa.String(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), default=datetime.now(timezone.utc)),
        sa.Column('created_at', sa.DateTime(), default=datetime.now(timezone.utc)),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on key for faster lookups
    op.create_index('ix_settings_key', 'settings', ['key'])
    op.create_index('ix_settings_category', 'settings', ['category'])


def downgrade():
    op.drop_index('ix_settings_category')
    op.drop_index('ix_settings_key')
    op.drop_table('settings')
