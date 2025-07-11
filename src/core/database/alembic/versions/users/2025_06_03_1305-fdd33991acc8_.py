"""empty message

Revision ID: fdd33991acc8
Revises: d16f026051f5
Create Date: 2025-06-03 13:05:59.802287

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "fdd33991acc8"
down_revision: Union[str, None] = "d16f026051f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "attachment_data",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default='{"specialization_name": "", "area_number": 0, "organization_name": "", '
            '"attachment_date": "", "detachment_date": "", "department_name": ""}',
            nullable=False,
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "attachment_data")
    # ### end Alembic commands ###
