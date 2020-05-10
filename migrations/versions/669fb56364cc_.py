"""empty message

Revision ID: 669fb56364cc
Revises: 2ddce84ec6eb
Create Date: 2020-05-10 10:04:34.867675

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '669fb56364cc'
down_revision = '2ddce84ec6eb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('can_post', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'can_post')
    # ### end Alembic commands ###