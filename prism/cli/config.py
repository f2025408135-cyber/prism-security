"""CLI commands for configuration management."""

import typer
import structlog

logger = structlog.get_logger(__name__)
app = typer.Typer(no_args_is_help=True)


@app.command()
def init(
    workspace_dir: str = typer.Option(".prism", help="Workspace directory to initialize.")
) -> None:
    """Initialize a new PRISM workspace configuration."""
    # STUB — replace with full implementation
    logger.info("config_initialized", workspace_dir=workspace_dir)
    typer.echo(f"Initialized workspace at {workspace_dir}")
