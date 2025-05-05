import click
import time
from flask import current_app
from application.scrape import index_all_jobs


@click.command("scrape")
def scrape_command():
    """
    Manually trigger a full scrape.

    Usage:
        flask --app run.py scrape
        docker compose exec app flask scrape
    """
    with current_app.app_context():
        click.echo("⏳  Scraping …")
        start_time = time.time()
        index_all_jobs()
        elapsed_time = time.time() - start_time
        min = elapsed_time // 60
        sec = elapsed_time % 60
        click.secho(
            f"✅  Done. Time taken: {int(min)} minutes and {sec:.2f} seconds.",
            fg="green",
        )
