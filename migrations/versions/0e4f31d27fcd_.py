"""empty message

Revision ID: 0e4f31d27fcd
Revises: ee5337e5de33
Create Date: 2020-06-04 13:42:31.754847

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e4f31d27fcd'
down_revision = 'ee5337e5de33'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('referred_plan_3', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'referred_plan_3')
    # ### end Alembic commands ###
