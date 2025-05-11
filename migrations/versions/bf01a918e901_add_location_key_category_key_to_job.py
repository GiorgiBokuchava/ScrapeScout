"""add location_key, category_key to Job

Revision ID: bf01a918e901
Revises: b942729ab118
Create Date: 2025-05-11 01:56:07.152842

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bf01a918e901"
down_revision = "b942729ab118"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "job",
        sa.Column(
            "location_key", sa.String(length=50), nullable=False, server_default="ALL"
        ),
    )
    op.add_column(
        "job",
        sa.Column(
            "category_key", sa.String(length=50), nullable=False, server_default="ALL"
        ),
    )
    pass


def downgrade():
    op.drop_column("job", "category_key")
    op.drop_column("job", "location_key")
    pass
