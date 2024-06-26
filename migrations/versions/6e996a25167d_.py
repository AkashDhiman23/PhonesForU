"""empty message

Revision ID: 6e996a25167d
Revises: 8a612a371925
Create Date: 2024-06-17 08:00:22.529420

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6e996a25167d'
down_revision = '8a612a371925'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_first_name', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('user_last_name', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('user_email_address', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('user_mobile', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('shipping_address', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('shipping_city', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('shipping_state', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('shipping_zip', sa.String(), nullable=False))
        batch_op.add_column(sa.Column('shipping_country', sa.String(), nullable=False))
        batch_op.drop_column('last_name')
        batch_op.drop_column('first_name')
        batch_op.drop_column('mobile_no')
        batch_op.drop_column('email_address')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('payment_record', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_address', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('mobile_no', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.drop_column('shipping_country')
        batch_op.drop_column('shipping_zip')
        batch_op.drop_column('shipping_state')
        batch_op.drop_column('shipping_city')
        batch_op.drop_column('shipping_address')
        batch_op.drop_column('user_mobile')
        batch_op.drop_column('user_email_address')
        batch_op.drop_column('user_last_name')
        batch_op.drop_column('user_first_name')

    # ### end Alembic commands ###
