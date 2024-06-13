"""Added relationship between ProductCategory and MerchantUser

Revision ID: ca0c839df1f9
Revises: dd53d96513f8
Create Date: 2024-06-13 03:19:17.475220

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ca0c839df1f9'
down_revision = 'dd53d96513f8'
branch_labels = None
depends_on = None


def upgrade():
    # Add the new column with nullable=True
    op.add_column('product_category', sa.Column('merchant_id', sa.Integer(), nullable=True))


def downgrade():
    # Drop the column if needed
    op.drop_column('product_category', 'merchant_id')
    # ### end Alembic commands ###
