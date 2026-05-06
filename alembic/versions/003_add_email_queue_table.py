"""Add email_queue table

Revision ID: 003
Revises: 002
Create Date: 2026-05-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create email_queue table
    op.create_table(
        'email_queue',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('to_email', sa.String(200), nullable=False),
        sa.Column('subject', sa.String(500), nullable=False),
        sa.Column('body_html', sa.Text(), nullable=False),
        sa.Column('body_text', sa.Text(), nullable=True),
        sa.Column('attachments', sa.Text(), nullable=True),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('retry_count', sa.Integer(), server_default='0'),
        sa.Column('max_retries', sa.Integer(), server_default='3'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('ix_email_queue_status_scheduled', 'email_queue', ['status', 'scheduled_at'])
    op.create_index('ix_email_queue_to_email', 'email_queue', ['to_email'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_email_queue_to_email')
    op.drop_index('ix_email_queue_status_scheduled')
    
    # Drop table
    op.drop_table('email_queue')
