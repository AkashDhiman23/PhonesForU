"""empty message

Revision ID: 15de47640167
Revises: dd53d96513f8
Create Date: 2024-06-13 12:45:00.610610

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '15de47640167'
down_revision = 'dd53d96513f8'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('cart', sa.Column('product_name', sa.String(length=255), nullable=True))
    op.add_column('cart', sa.Column('product_price', sa.Numeric(precision=10, scale=2), nullable=True))
    op.add_column('cart', sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=True))


def downgrade():
    op.drop_column('cart', 'product_name')
    op.drop_column('cart', 'product_price')
    op.drop_column('cart', 'total_price')
