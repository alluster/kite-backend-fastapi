"""migration

Revision ID: d52c18cbd514
Revises: 5fed0fa7d39e
Create Date: 2024-10-31 14:08:13.411948

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd52c18cbd514'
down_revision: Union[str, None] = '5fed0fa7d39e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('suppliers', sa.Column('logo_url', sa.String(), nullable=True))
    op.create_index(op.f('ix_suppliers_logo_url'), 'suppliers', ['logo_url'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_suppliers_logo_url'), table_name='suppliers')
    op.drop_column('suppliers', 'logo_url')
    # ### end Alembic commands ###
