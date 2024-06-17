"""empty message

Revision ID: dd53d96513f8
Revises: 
Create Date: 2024-06-10 18:13:28.437172

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dd53d96513f8'
down_revision = None
branch_labels = None
depends_on = None

# Check if the table exists before creating it
def upgrade():
    conn = op.get_bind()
    if not conn.dialect.has_table(conn, 'payment_record'):
        op.create_table(
            'payment_record',
            sa.Column('transaction_id', sa.String(length=255), nullable=False),
            sa.Column('First_name', sa.String, nullable=False),
            sa.Column('Last_name', sa.String, nullable=False),
            sa.Column('email_address', sa.String, nullable=False),
            sa.Column('mobile', sa.Integer, nullable=False),
            sa.Column('user_id', sa.Integer, nullable=False),
            sa.Column('product_id', sa.Integer, nullable=False),
            sa.Column('product_name', sa.String, nullable=False),
            sa.Column('product_price', sa.String, nullable=False),
            sa.Column('shipping_address', sa.String, nullable=False),
            sa.Column('shipping_city', sa.String, nullable=False),
            sa.Column('shipping_state', sa.String, nullable=False),
            sa.Column('shipping_zip', sa.String, nullable=False),
            sa.Column('shipping_country', sa.String, nullable=False),
            sa.Column('product_quantity', sa.Integer, nullable=False),
            sa.Column('total_amount', sa.Numeric(10, 2), nullable=False),
            sa.Column('transaction_date', sa.DateTime, nullable=False),
            sa.PrimaryKeyConstraint('transaction_id'),
            sa.ForeignKeyConstraint(['First_name'], ['user.user_firstname']),
            sa.ForeignKeyConstraint(['Last_name'], ['user.user_lastname']),
            sa.ForeignKeyConstraint(['email_address'], ['user.email_address']),
            sa.ForeignKeyConstraint(['mobile'], ['user.mobile']),
            sa.ForeignKeyConstraint(['user_id'], ['user.user_id']),
            sa.ForeignKeyConstraint(['product_id'], ['product.id']),
            sa.ForeignKeyConstraint(['product_name'], ['product.product_name']),
            sa.ForeignKeyConstraint(['product_price'], ['product.product_price']),
            sa.ForeignKeyConstraint(['product_quantity'], ['cart.quantity'])
        )

def downgrade():
    op.drop_table('payment_record')