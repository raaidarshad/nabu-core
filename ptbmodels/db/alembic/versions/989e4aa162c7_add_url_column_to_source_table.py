"""add url column to source table

Revision ID: 989e4aa162c7
Revises: 99d28036f5bb
Create Date: 2022-02-11 14:34:47.538331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '989e4aa162c7'
down_revision = '99d28036f5bb'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('source', sa.Column('url', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'source', ['url'])


def downgrade():
    op.drop_constraint(None, 'source', type_='unique')
    op.drop_column('source', 'url')
