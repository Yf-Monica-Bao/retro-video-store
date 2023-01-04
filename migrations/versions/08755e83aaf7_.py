"""empty message

Revision ID: 08755e83aaf7
Revises: 48784f087bfd
Create Date: 2023-01-03 21:01:26.366368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '08755e83aaf7'
down_revision = '48784f087bfd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('video', sa.Column('release_date', sa.DateTime(), nullable=True))
    op.add_column('video', sa.Column('title', sa.String(), nullable=True))
    op.add_column('video', sa.Column('total_inventory', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('video', 'total_inventory')
    op.drop_column('video', 'title')
    op.drop_column('video', 'release_date')
    # ### end Alembic commands ###
