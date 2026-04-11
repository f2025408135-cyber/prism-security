"""Rich terminal reporter."""

import structlog
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from prism.models.finding import Finding

logger = structlog.get_logger(__name__)


class TerminalReporter:
    """Generates Rich terminal output for scan results."""

    def __init__(self) -> None:
        self.console = Console()

    def print_summary(self, findings: tuple[Finding, ...], target: str) -> None:
        """Print a summary table of all findings.

        Args:
            findings: The tuple of confirmed findings.
            target: The target URL scanned.
        """
        logger.info("terminal_report_generated", findings=len(findings))

        self.console.print(f"\n[bold green]PRISM Security Scan Complete[/bold green] -> [blue]{target}[/blue]\n")

        if not findings:
            self.console.print("[bold green]✓ No vulnerabilities detected.[/bold green]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("ID", style="dim", width=8)
        table.add_column("Vulnerability", min_width=20)
        table.add_column("CWE", justify="center")
        table.add_column("CVSS Vector", style="blue")

        for f in findings:
            table.add_row(
                f.id[:8],
                f.title,
                f.cwe_id,
                f.cvss_vector
            )

        self.console.print(table)
        self.console.print(f"\n[bold red]Total Confirmed Findings: {len(findings)}[/bold red]\n")

    def print_finding_details(self, finding: Finding) -> None:
        """Print detailed information for a specific finding.

        Args:
            finding: The finding to print.
        """
        details = (
            f"[bold]Description:[/bold]\n{finding.description}\n\n"
            f"[bold]CWE:[/bold] {finding.cwe_id}\n"
            f"[bold]CVSS:[/bold] {finding.cvss_vector}\n"
        )
        
        self.console.print(Panel(details, title=f"[red]{finding.title}[/red]", expand=False))
