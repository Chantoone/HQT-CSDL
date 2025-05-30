"""xóa nullable trong staffid trong pro

Revision ID: 75f839e4e836
Revises: 2780d7d5e1bc
Create Date: 2025-04-10 19:23:09.842201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '75f839e4e836'
down_revision: Union[str, None] = '2780d7d5e1bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('promotions', 'staff_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('seats', 'is_booked')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('seats', sa.Column('is_booked', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.alter_column('promotions', 'staff_id',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
