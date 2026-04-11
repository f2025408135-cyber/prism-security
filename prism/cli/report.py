"""CLI commands for reporting."""

import typer
import structlog

logger = structlog.get_logger(__name__)
app = typer.Typer(no_args_is_help=True)


@app.command()
def generate(
    format: str = typer.Option("terminal", help="Report format (terminal, html, json, markdown)."),
    output: str = typer.Option("report.json", help="Output file path.")
) -> None:
    """Generate a report from the current workspace data."""
    # STUB — replace with full implementation
    logger.info("report_generated", format=format, output=output)
    typer.echo(f"Generating {format} report to {output}...")
