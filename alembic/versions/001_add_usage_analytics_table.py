"""Add usage_analytics table

Revision ID: 001
Revises: 
Create Date: 2026-05-05

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime, timezone


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create usage_analytics table
    op.create_table(
        'usage_analytics',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('license_id', sa.String(), nullable=True),
        sa.Column('feature_name', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(50), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes for performance
    op.create_index('ix_usage_analytics_customer_created', 'usage_analytics', ['customer_id', 'created_at'])
    op.create_index('ix_usage_analytics_feature_created', 'usage_analytics', ['feature_name', 'created_at'])
    op.create_index('ix_usage_analytics_created', 'usage_analytics', ['created_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_usage_analytics_created')
    op.drop_index('ix_usage_analytics_feature_created')
    op.drop_index('ix_usage_analytics_customer_created')
    
    # Drop table
    op.drop_table('usage_analytics')
