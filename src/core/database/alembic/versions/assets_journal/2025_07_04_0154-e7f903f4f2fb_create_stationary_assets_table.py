"""Create stationary assets table

Revision ID: e7f903f4f2fb
Revises: 18bd4362e19b
Create Date: 2025-07-04 01:54:00.047270

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7f903f4f2fb'
down_revision: Union[str, None] = '18bd4362e19b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('stationary_assets',
    sa.Column('bg_asset_id', sa.String(length=50), nullable=False),
    sa.Column('card_number', sa.String(length=50), nullable=False),
    sa.Column('patient_full_name', sa.String(length=255), nullable=False),
    sa.Column('patient_iin', sa.String(length=12), nullable=False),
    sa.Column('patient_birth_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('patient_sex_code', sa.String(length=10), nullable=False),
    sa.Column('patient_citizen_id_code', sa.String(length=20), nullable=False),
    sa.Column('patient_rpn_id', sa.String(length=50), nullable=True),
    sa.Column('hospital_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('current_plan_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('hospital_plan_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('polyclinic_plan_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('reg_date', sa.DateTime(timezone=True), nullable=False),
    sa.Column('out_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('status', sa.Enum('REGISTERED', 'CONFIRMED', 'REFUSED', 'CANCELLED', name='assetstatusenum'), nullable=False),
    sa.Column('delivery_status', sa.Enum('RECEIVED_AUTOMATICALLY', 'PENDING_DELIVERY', 'DELIVERED', name='assetdeliverystatusenum'), nullable=False),
    sa.Column('hospital_notice_statuses', sa.String(length=10), nullable=True),
    sa.Column('hospital_code', sa.String(length=50), nullable=False),
    sa.Column('bed_profile_code', sa.String(length=10), nullable=False),
    sa.Column('bed_profile_name', sa.String(length=255), nullable=False),
    sa.Column('sick_code', sa.String(length=20), nullable=False),
    sa.Column('sick_name', sa.String(length=255), nullable=False),
    sa.Column('referral_target', sa.Enum('REHABILITATION', 'TREATMENT', 'DIAGNOSIS', 'CONSULTATION', name='referraltargetenum'), nullable=False),
    sa.Column('referral_type', sa.Enum('REHABILITATION_TREATMENT', 'PLANNED_HOSPITALIZATION', 'EMERGENCY_HOSPITALIZATION', name='referraltypeenum'), nullable=False),
    sa.Column('rehabilitation_type', sa.Enum('MEDICAL', 'SOCIAL', name='rehabilitationtypeenum'), nullable=True),
    sa.Column('org_health_care_request_code', sa.String(length=20), nullable=False),
    sa.Column('org_health_care_request_name', sa.String(length=500), nullable=False),
    sa.Column('org_health_care_direct_code', sa.String(length=20), nullable=False),
    sa.Column('org_health_care_direct_name', sa.String(length=500), nullable=False),
    sa.Column('org_health_care_ref_code', sa.String(length=20), nullable=False),
    sa.Column('org_health_care_ref_name', sa.String(length=500), nullable=False),
    sa.Column('direct_doctor', sa.String(length=255), nullable=False),
    sa.Column('patient_address', sa.Text(), nullable=False),
    sa.Column('additional_information', sa.String(length=500), nullable=True),
    sa.Column('benefit_type_code', sa.String(length=20), nullable=True),
    sa.Column('benefit_type_name', sa.String(length=255), nullable=True),
    sa.Column('work_place', sa.String(length=255), nullable=True),
    sa.Column('protocol_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('protocol_number', sa.String(length=50), nullable=True),
    sa.Column('has_confirm', sa.Boolean(), nullable=False),
    sa.Column('has_files', sa.Boolean(), nullable=False),
    sa.Column('has_refusal', sa.Boolean(), nullable=False),
    sa.Column('has_rehabilitation_files', sa.Boolean(), nullable=False),
    sa.Column('refusal_reg_date', sa.DateTime(timezone=True), nullable=True),
    sa.Column('refuse_justification', sa.Text(), nullable=True),
    sa.Column('refuse_reason_code', sa.String(length=20), nullable=True),
    sa.Column('refuse_reason_name', sa.String(length=255), nullable=True),
    sa.Column('area_number', sa.Integer(), nullable=True),
    sa.Column('specialization', sa.String(length=255), nullable=True),
    sa.Column('specialist_name', sa.String(length=255), nullable=True),
    sa.Column('diagnosis_code', sa.String(length=20), nullable=True),
    sa.Column('diagnosis_name', sa.String(length=255), nullable=True),
    sa.Column('treatment_outcome', sa.String(length=255), nullable=True),
    sa.Column('note', sa.Text(), nullable=True),
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
