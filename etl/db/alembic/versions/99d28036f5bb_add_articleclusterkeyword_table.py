"""add ArticleClusterKeyword table

Revision ID: 99d28036f5bb
Revises: 
Create Date: 2021-10-29 14:23:41.090411

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision = '99d28036f5bb'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('articleclusterkeyword',
    sa.Column('article_cluster_id', sqlmodel.sql.sqltypes.GUID(), nullable=False),
    sa.Column('term', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('weight', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['article_cluster_id'], ['articlecluster.id'], ),
    sa.PrimaryKeyConstraint('article_cluster_id', 'term')
    )
    op.create_index(op.f('ix_articleclusterkeyword_article_cluster_id'), 'articleclusterkeyword', ['article_cluster_id'], unique=False)
    op.create_index(op.f('ix_articleclusterkeyword_term'), 'articleclusterkeyword', ['term'], unique=False)
    op.create_index(op.f('ix_articleclusterkeyword_weight'), 'articleclusterkeyword', ['weight'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_articleclusterkeyword_weight'), table_name='articleclusterkeyword')
    op.drop_index(op.f('ix_articleclusterkeyword_term'), table_name='articleclusterkeyword')
    op.drop_index(op.f('ix_articleclusterkeyword_article_cluster_id'), table_name='articleclusterkeyword')
    op.drop_table('articleclusterkeyword')
    # ### end Alembic commands ###