"""change len column movie title - string200

Revision ID: ae01df338c6b
Revises: b4ebaa26c78a
Create Date: 2017-02-06 01:09:49.218020

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ae01df338c6b'
down_revision = 'b4ebaa26c78a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('movies', 'title',
                    existing_type=sa.VARCHAR(length=120),
                    type_=sa.String(length=200),
                    existing_nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('movies', 'title',
                    existing_type=sa.String(length=200),
                    type_=sa.VARCHAR(length=120),
                    existing_nullable=True)
    # ### end Alembic commands ###
