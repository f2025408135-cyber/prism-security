"""Main CLI entry point for the PRISM framework."""

import typer
from prism.cli import scan, report, config

app = typer.Typer(
    name="prism",
    help="PRISM: A production-grade open source Python security research framework.",
    no_args_is_help=True,
)

app.add_typer(scan.app, name="scan", help="Commands related to scanning APIs.")
app.add_typer(report.app, name="report", help="Commands for generating reports.")
app.add_typer(config.app, name="config", help="Commands for managing configuration.")


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
