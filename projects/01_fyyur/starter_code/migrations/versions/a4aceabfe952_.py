"""empty message

Revision ID: a4aceabfe952
Revises: 591d3b235af9
Create Date: 2021-05-17 00:23:57.748856

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4aceabfe952'
down_revision = '591d3b235af9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'venue_name')
    op.drop_column('Show', 'artist_name')
    op.drop_column('Show', 'artist_image_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_image_link', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('artist_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('Show', sa.Column('venue_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
