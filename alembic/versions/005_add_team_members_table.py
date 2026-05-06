"""Add team_members table

Revision ID: 005
Revises: 004
Create Date: 2026-05-05

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create team_members table
    op.create_table(
        'team_members',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('license_id', sa.String(), nullable=False),
        sa.Column('customer_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(200), nullable=False),
        sa.Column('full_name', sa.String(200), nullable=True),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permissions', sa.Text(), nullable=False),
        sa.Column('invitation_token', sa.String(100), nullable=True),
        sa.Column('invitation_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='false'),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes
    op.create_index('ix_team_members_license_email', 'team_members', ['license_id', 'email'])
    op.create_index('ix_team_members_token', 'team_members', ['invitation_token'], unique=True)
    op.create_index('ix_team_members_license_active', 'team_members', ['license_id', 'is_active'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_team_members_license_active')
    op.drop_index('ix_team_members_token')
    op.drop_index('ix_team_members_license_email')
    
    # Drop table
    op.drop_table('team_members')
