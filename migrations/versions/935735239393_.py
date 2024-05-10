"""empty message

Revision ID: 935735239393
Revises: ae8445eb3dfc
Create Date: 2024-05-10 14:08:38.030059

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '935735239393'
down_revision = 'ae8445eb3dfc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Product',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('product_name', sa.String(length=255), nullable=False),
    sa.Column('product_code', sa.String(length=50), nullable=False),
    sa.Column('product_title', sa.String(length=255), nullable=False),
    sa.Column('product_description', sa.String(length=1000), nullable=False),
    sa.Column('product_price', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('product_quantity', sa.Integer(), nullable=False),
    sa.Column('product_main_image', sa.String(length=255), nullable=False),
    sa.Column('product_secondary_image1', sa.String(length=255), nullable=True),
    sa.Column('product_secondary_image2', sa.String(length=255), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['category_id'], ['product_category.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Product')
    # ### end Alembic commands ###
