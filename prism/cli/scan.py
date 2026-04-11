"""CLI commands for scanning."""

import typer
import structlog

logger = structlog.get_logger(__name__)
app = typer.Typer(no_args_is_help=True)


@app.command()
def start(
    target_url: str = typer.Argument(..., help="The base URL of the target API."),
    workspace_dir: str = typer.Option(".prism", help="Workspace directory.")
) -> None:
    """Start a new PRISM scan against a target URL."""
    # STUB — replace with full implementation
    logger.info("scan_started", target_url=target_url, workspace_dir=workspace_dir)
    typer.echo(f"Starting scan for {target_url} in workspace {workspace_dir}...")
