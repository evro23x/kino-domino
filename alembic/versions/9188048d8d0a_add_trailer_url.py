"""add trailer url

Revision ID: 9188048d8d0a
Revises: 87dbba7785d6
Create Date: 2017-03-19 22:20:21.004564

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9188048d8d0a'
down_revision = '87dbba7785d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('movies', sa.Column('trailer_url', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('movies', 'trailer_url')
    # ### end Alembic commands ###
