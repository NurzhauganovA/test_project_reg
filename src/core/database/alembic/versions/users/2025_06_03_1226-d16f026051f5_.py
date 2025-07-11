"""empty message

Revision ID: d16f026051f5
Revises: e06b10759b12
Create Date: 2025-06-03 12:26:42.579502

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d16f026051f5"
down_revision: Union[str, None] = "e06b10759b12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "appointments",
        sa.Column(
            "additional_services",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default="{}",
            nullable=False,
        ),
    )
    op.drop_column("appointments", "office_number")
    op.drop_column("appointments", "paid_services")
    op.drop_column("appointments", "is_patient_info_confirmation_needed")
    op.drop_column("schedules", "specialization_id")
    op.add_column(
        "users",
        sa.Column(
            "specializations",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='{"therapist": true}',
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "served_patient_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='{"adult": true, "child": false}',
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "served_referral_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='{"with_referral": true, "without_referral": true}',
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "served_referral_origins",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='{"from_external_organization": true, "self_registration": true}',
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "served_payment_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='{"GOBMP": true, "DMS": true, "OSMS": true, "paid": true}',
            nullable=False,
        ),
    )
    op.drop_column("users", "referral_types")
    op.drop_column("users", "payment_types")
    op.drop_column("users", "patient_types")
    op.drop_column("users", "referral_origins")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "referral_origins",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text(
                '\'{"self_registration": true, "from_external_organization": true}\'::jsonb'
            ),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "patient_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text('\'{"adult": true, "child": false}\'::jsonb'),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "payment_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text(
                '\'{"DMS": true, "OSMS": true, "paid": true, "GOBMP": true}\'::jsonb'
            ),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "referral_types",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text(
                '\'{"with_referral": true, "without_referral": true}\'::jsonb'
            ),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.drop_column("users", "served_payment_types")
    op.drop_column("users", "served_referral_origins")
    op.drop_column("users", "served_referral_types")
    op.drop_column("users", "served_patient_types")
    op.drop_column("users", "specializations")
    op.add_column(
        "schedules",
        sa.Column(
            "specialization_id", sa.INTEGER(), autoincrement=False, nullable=False
        ),
    )
    op.add_column(
        "appointments",
        sa.Column(
            "is_patient_info_confirmation_needed",
            sa.BOOLEAN(),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "appointments",
        sa.Column(
            "paid_services",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "appointments",
        sa.Column("office_number", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    op.drop_column("appointments", "additional_services")
    # ### end Alembic commands ###
