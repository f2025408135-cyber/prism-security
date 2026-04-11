"""Standard Markdown reporter."""

import structlog
from pathlib import Path

from prism.models.finding import Finding
from prism.reporting.evidence import EvidenceBuilder

logger = structlog.get_logger(__name__)


class MarkdownReporter:
    """Generates Markdown files for generic reporting."""

    def __init__(self, evidence_builder: EvidenceBuilder) -> None:
        self.evidence_builder = evidence_builder

    def generate(self, findings: tuple[Finding, ...], output_path: str) -> str:
        """Generate a markdown report.

        Args:
            findings: The tuple of confirmed findings.
            output_path: Where to save the file.

        Returns:
            The path to the generated file.
        """
        logger.info("markdown_report_generated", path=output_path)

        lines = ["# PRISM Security Scan Report\n"]
        lines.append(f"**Total Findings:** {len(findings)}\n\n---\n")

        for f in findings:
            lines.append(f"## {f.title}")
            lines.append(f"**ID:** `{f.id}` | **CWE:** `{f.cwe_id}` | **CVSS:** `{f.cvss_vector}`\n")
            lines.append(f"### Description\n{f.description}\n")
            
            if f.poc and f.poc.steps:
                lines.append("### Proof of Concept")
                for step in f.poc.steps:
                    lines.append(f"{step}\n")
                    
            lines.append(self.evidence_builder.format_evidence_chain(f.evidence))
            lines.append("---\n")

        path = Path(output_path)
        with path.open("w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        return str(path)
