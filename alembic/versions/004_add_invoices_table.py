"""Add invoices table

Revision ID: 004
Revises: 003
Create Date: 2026-05-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('payment_id', sa.String(), nullable=False),
        sa.Column('plan', sa.String(50), nullable=False),
        sa.Column('base_amount', sa.BigInteger(), nullable=False),
        sa.Column('gst_rate', sa.Float(), nullable=False),
        sa.Column('gst_amount', sa.BigInteger(), nullable=False),
        sa.Column('total_amount', sa.BigInteger(), nullable=False),
        sa.Column('discount_amount', sa.BigInteger(), server_default='0'),
        sa.Column('promo_code_id', sa.String(), nullable=True),
        sa.Column('invoice_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('pdf_path', sa.String(500), nullable=True),
        sa.Column('is_emailed', sa.Boolean(), server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('invoice_number')
    )
    
    # Add indexes
    op.create_index('ix_invoices_number', 'invoices', ['invoice_number'], unique=True)
    op.create_index('ix_invoices_customer', 'invoices', ['customer_id'])
    op.create_index('ix_invoices_payment', 'invoices', ['payment_id'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_invoices_payment')
    op.drop_index('ix_invoices_customer')
    op.drop_index('ix_invoices_number')
    
    # Drop table
    op.drop_table('invoices')
