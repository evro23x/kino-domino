"""add migrate create log table(io)

Revision ID: 465b11daf417
Revises: 1248a759e98e
Create Date: 2017-03-09 23:41:29.916321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '465b11daf417'
down_revision = '1248a759e98e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('bot_logger', sa.Column('msg_in', sa.String(length=500), nullable=True))
    op.add_column('bot_logger', sa.Column('msg_out', sa.String(length=500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('bot_logger', 'msg_out')
    op.drop_column('bot_logger', 'msg_in')
    # ### end Alembic commands ###