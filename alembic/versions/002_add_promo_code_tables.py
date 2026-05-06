"""Add promo_codes and promo_code_usage tables

Revision ID: 002
Revises: 001
Create Date: 2026-05-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create promo_codes table
    op.create_table(
        'promo_codes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('code', sa.String(50), nullable=False),
        sa.Column('discount_type', sa.String(20), nullable=False),
        sa.Column('discount_value', sa.Integer(), nullable=False),
        sa.Column('expiry_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_limit', sa.Integer(), nullable=True),
        sa.Column('usage_count', sa.Integer(), server_default='0'),
        sa.Column('is_multi_use', sa.Boolean(), server_default='false'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('applicable_plans', sa.Text(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create promo_code_usage table
    op.create_table(
        'promo_code_usage',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('promo_code_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('payment_id', sa.String(), nullable=True),
        sa.Column('discount_amount', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('ix_promo_codes_code', 'promo_codes', ['code'], unique=True)
    op.create_index('ix_promo_codes_active_expiry', 'promo_codes', ['is_active', 'expiry_date'])
    op.create_index('ix_promo_usage_code_customer', 'promo_code_usage', ['promo_code_id', 'customer_id'])
    op.create_index('ix_promo_usage_payment', 'promo_code_usage', ['payment_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_promo_usage_payment')
    op.drop_index('ix_promo_usage_code_customer')
    op.drop_index('ix_promo_codes_active_expiry')
    op.drop_index('ix_promo_codes_code')
    
    # Drop tables
    op.drop_table('promo_code_usage')
    op.drop_table('promo_codes')
