
"""empty message

Revision ID: 0c8f868980b6
Revises: 18bd4362e19b
Create Date: 2025-07-04 06:57:18.655298

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c8f868980b6'
down_revision: Union[str, None] = '18bd4362e19b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stationary_assets',
    sa.Column('bg_asset_id', sa.String(length=50), nullable=True),
    sa.Column('card_number', sa.String(length=50), nullable=True),
    sa.Column('patient_full_name', sa.String(length=255), nullable=False),
    sa.Column('patient_iin', sa.String(length=12), nullable=False),
    sa.Column('patient_birth_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('patient_address', sa.Text(), nullable=True),
    sa.Column('receive_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('receive_time', sa.Time(), nullable=False),
    sa.Column('actual_datetime', sa.DateTime(timezone=True), nullable=False),
    sa.Column('received_from', sa.String(length=255), nullable=False),
    sa.Column('is_repeat', sa.Boolean(), nullable=False),
    sa.Column('stay_period_start', sa.DateTime(timezone=True), nullable=False),
    sa.Column('stay_period_end', sa.DateTime(timezone=True), nullable=True),
    sa.Column('stay_outcome', sa.String(length=255), nullable=True),
    sa.Column('diagnosis', sa.Text(), nullable=False),
    sa.Column('area', sa.String(length=255), nullable=False),
    sa.Column('specialization', sa.String(length=255), nullable=True),
    sa.Column('specialist', sa.String(length=255), nullable=False),
    sa.Column('note', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('REGISTERED', 'CONFIRMED', 'REFUSED', 'CANCELLED', name='assetstatusenum'), nullable=False),
    sa.Column('delivery_status', sa.Enum('RECEIVED_AUTOMATICALLY', 'PENDING_DELIVERY', 'DELIVERED', name='assetdeliverystatusenum'), nullable=False),
    sa.Column('reg_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('has_confirm', sa.Boolean(), nullable=False),
    sa.Column('has_files', sa.Boolean(), nullable=False),
    sa.Column('has_refusal', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_stationary_assets')),
    sa.UniqueConstraint('bg_asset_id', name=op.f('uq_stationary_assets_bg_asset_id'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('stationary_assets')
    # ### end Alembic commands ###