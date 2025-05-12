"""convert job dates to datetime

Revision ID: convert_job_dates
Revises: d24b98c5dbcd
Create Date: 2024-05-12 17:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime
from pytz import utc
from sqlalchemy.sql import table, column
from sqlalchemy import String, DateTime, update
from application.jobs_ge import parse_jobs_ge_date

# revision identifiers, used by Alembic.
revision = "convert_job_dates"
down_revision = "d24b98c5dbcd"
branch_labels = None
depends_on = None


def upgrade():
    # Create a temporary table with the new datetime column
    op.add_column(
        "job", sa.Column("date_posted_new", sa.DateTime(timezone=True), nullable=True)
    )

    # Get all existing jobs
    job = table(
        "job",
        column("id"),
        column("date_posted", String),  # old type
        column("date_posted_new", DateTime),  # new type
    )

    conn = op.get_bind()
    rows = conn.execute(job.select()).fetchall()

    def safe_parse(s):
        try:
            return parse_jobs_ge_date(s)
        except Exception:
            return None

    # Convert each date
    for r in rows:
        dt = safe_parse(r.date_posted)
        if dt:
            conn.execute(update(job).where(job.c.id == r.id).values(date_posted_new=dt))

    # Set a default value for null entries
    conn.execute(
        update(job)
        .where(job.c.date_posted_new == None)
        .values(date_posted_new=datetime.now(utc))
    )

    # Drop the old column and rename the new one
    op.drop_column("job", "date_posted")
    op.alter_column(
        "job", "date_posted_new", new_column_name="date_posted", nullable=False
    )


def downgrade():
    # Convert back to string format
    job = table(
        "job",
        column("id"),
        column("date_posted", DateTime),
    )

    conn = op.get_bind()
    rows = conn.execute(job.select()).fetchall()

    # Add temporary string column
    op.add_column("job", sa.Column("date_posted_str", sa.String(20), nullable=True))

    # Convert each datetime to string
    for r in rows:
        if r.date_posted:
            date_str = r.date_posted.strftime("%d %B %Y")
            conn.execute(
                update(job).where(job.c.id == r.id).values(date_posted_str=date_str)
            )

    # Drop datetime column and rename string column
    op.drop_column("job", "date_posted")
    op.alter_column(
        "job", "date_posted_str", new_column_name="date_posted", nullable=False
    )
