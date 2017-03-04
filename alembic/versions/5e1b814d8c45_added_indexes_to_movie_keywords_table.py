"""Added indexes to movie_keywords table

Revision ID: 5e1b814d8c45
Revises: 3caa079a6a77
Create Date: 2017-03-04 19:14:59.665939

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5e1b814d8c45'
down_revision = '3caa079a6a77'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('ix_tmdb_plot_keywords_connecction_keyword_id'), 'tmdb_plot_keywords_connecction', ['keyword_id'], unique=False)
    op.create_index(op.f('ix_tmdb_plot_keywords_connecction_movie_id'), 'tmdb_plot_keywords_connecction', ['movie_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tmdb_plot_keywords_connecction_movie_id'), table_name='tmdb_plot_keywords_connecction')
    op.drop_index(op.f('ix_tmdb_plot_keywords_connecction_keyword_id'), table_name='tmdb_plot_keywords_connecction')
    # ### end Alembic commands ###