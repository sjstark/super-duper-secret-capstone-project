"""add picture boolean

Revision ID: 2e83b1df0956
Revises: 44078d0d3f38
Create Date: 2021-01-14 16:39:28.953750

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e83b1df0956'
down_revision = '44078d0d3f38'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('booths', sa.Column('has_picture', sa.Boolean(), nullable=True))
    op.add_column('shows', sa.Column('has_picture', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('has_picture', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'has_picture')
    op.drop_column('shows', 'has_picture')
    op.drop_column('booths', 'has_picture')
    # ### end Alembic commands ###
