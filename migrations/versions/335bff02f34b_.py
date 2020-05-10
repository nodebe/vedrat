"""empty message

Revision ID: 335bff02f34b
Revises: 50ffb1db8957
Create Date: 2020-05-10 11:39:19.787257

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '335bff02f34b'
down_revision = '50ffb1db8957'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('picked_post', sa.Column('uuid', sa.String(length=10), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('picked_post', 'uuid')
    # ### end Alembic commands ###