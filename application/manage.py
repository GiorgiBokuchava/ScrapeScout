import click
from flask import current_app
from application.scrape import scrape_all_jobs


@click.command("scrape")
def scrape_command():
    """
    Manually trigger a full scrape.

    Usage:
        flask --app run.py scrape
    """
    with current_app.app_context():
        click.echo("⏳  Scraping …")
        scrape_all_jobs()
        click.secho("✅  Done.", fg="green")
