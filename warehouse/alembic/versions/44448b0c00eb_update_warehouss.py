"""update warehouss

Revision ID: 44448b0c00eb
Revises: 
Create Date: 2025-04-17 22:46:21.688326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44448b0c00eb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dim_cinema', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('dim_film', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('dim_genre', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('dim_promotion', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('dim_purchase_type', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('dim_showtime', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('dim_ticket', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('dim_time', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('fact_film_genre', sa.Column('point', sa.Integer(), nullable=False))
    op.add_column('fact_film_rating', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('fact_promotion_analysis', sa.Column('point', sa.Integer(), nullable=False))
    op.add_column('fact_revenue', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('fact_showtime_fillrate', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    op.add_column('fact_ticket_analysis', sa.Column('etl_loaded_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fact_ticket_analysis', 'etl_loaded_at')
    op.drop_column('fact_showtime_fillrate', 'etl_loaded_at')
    op.drop_column('fact_revenue', 'etl_loaded_at')
    op.drop_column('fact_promotion_analysis', 'point')
    op.drop_column('fact_film_rating', 'etl_loaded_at')
    op.drop_column('fact_film_genre', 'point')
    op.drop_column('dim_time', 'etl_loaded_at')
    op.drop_column('dim_ticket', 'etl_loaded_at')
    op.drop_column('dim_showtime', 'etl_loaded_at')
    op.drop_column('dim_purchase_type', 'etl_loaded_at')
    op.drop_column('dim_promotion', 'etl_loaded_at')
    op.drop_column('dim_genre', 'etl_loaded_at')
    op.drop_column('dim_film', 'etl_loaded_at')
    op.drop_column('dim_cinema', 'etl_loaded_at')
    # ### end Alembic commands ###
