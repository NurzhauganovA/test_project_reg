"""empty message

Revision ID: d6c2f189ae73
Revises: 49a8a76ea79f
Create Date: 2025-06-27 17:14:46.940751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd6c2f189ae73'
down_revision: Union[str, None] = '49a8a76ea79f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patients', sa.Column('attachment_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True, comment="Patient's attachment data. The optional field."))
    op.drop_constraint('fk_patients_attached_clinic_id_cat_medical_organizations', 'patients', type_='foreignkey')
    op.drop_column('patients', 'attached_clinic_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('patients', sa.Column('attached_clinic_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('fk_patients_attached_clinic_id_cat_medical_organizations', 'patients', 'cat_medical_organizations', ['attached_clinic_id'], ['id'])
    op.drop_column('patients', 'attachment_data')
    # ### end Alembic commands ###
