"""empty message

Revision ID: ee5337e5de33
Revises: d0296de2e52e
Create Date: 2020-05-20 18:17:28.352571

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee5337e5de33'
down_revision = 'd0296de2e52e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blogreply',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid_of_post', sa.String(length=10), nullable=False),
    sa.Column('fullname', sa.String(length=20), nullable=False),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('read', sa.String(length=1), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('blogreply')
    # ### end Alembic commands ###
