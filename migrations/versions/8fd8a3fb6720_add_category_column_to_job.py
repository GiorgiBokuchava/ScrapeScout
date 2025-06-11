"""add category column to job

Revision ID: 8fd8a3fb6720
Revises: 5df869f8deb3
Create Date: 2024-03-15 12:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "8fd8a3fb6720"
down_revision = "5df869f8deb3"
branch_labels = None
depends_on = None


def upgrade():
    # --- simple Postgres ALTER; no batch mode ---
    op.add_column("job", sa.Column("category", sa.String(length=50), nullable=True))
    op.create_foreign_key(
        "fk_job_category",  # constraint name
        "job",              # source table
        "category",         # target table
        ["category"],       # local cols
        ["name"],           # remote cols
    )


def downgrade():
    op.drop_constraint("fk_job_category", "job", type_="foreignkey")
    op.drop_column("job", "category")
