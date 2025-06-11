"""add category column to job

Revision ID: 8fd8a3fb6720
Revises: 5df869f8deb3
Create Date: 2024-03-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fd8a3fb6720'
down_revision = '5df869f8deb3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('job', schema=None, recreate='always') as batch_op:
        batch_op.add_column(sa.Column('category', sa.String(length=50), nullable=True))
        batch_op.create_foreign_key('fk_job_category', 'category', ['category'], ['name'])


def downgrade():
    with op.batch_alter_table('job', schema=None, recreate='always') as batch_op:
        batch_op.drop_constraint('fk_job_category', type_='foreignkey')
        batch_op.drop_column('category')
