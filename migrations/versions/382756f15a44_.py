"""empty message

Revision ID: 382756f15a44
Revises: 36eae714f662
Create Date: 2025-04-03 17:06:04.771156

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '382756f15a44'
down_revision = '36eae714f662'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.drop_column('rating')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('quotes', schema=None) as batch_op:
        batch_op.add_column(sa.Column('rating', sa.INTEGER(), nullable=False))

    # ### end Alembic commands ###
