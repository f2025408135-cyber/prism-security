"""HackerOne and Bugcrowd template generator."""

import structlog
from pathlib import Path

from prism.models.finding import Finding

logger = structlog.get_logger(__name__)


class H1TemplateGenerator:
    """Generates HackerOne specific markdown templates."""

    def generate(self, finding: Finding, output_path: str) -> str:
        """Format a single finding into the HackerOne format.

        Args:
            finding: The finding to report.
            output_path: Where to save the template file.

        Returns:
            The path to the generated file.
        """
        logger.info("h1_template_generated", finding_id=finding.id, path=output_path)

        poc_text = ""
        if finding.poc and finding.poc.steps:
            poc_text = "\n".join(finding.poc.steps)
        else:
            poc_text = "N/A"

        template = f"""## Summary
{finding.description}

## Steps To Reproduce
{poc_text}

## Supporting Evidence
Please refer to the raw HTTP logs attached.

## Impact
By exploiting this vulnerability, an attacker can bypass standard authorization controls, leading to potential data exfiltration or integrity corruption (See CVSS: {finding.cvss_vector}).
"""

        path = Path(output_path)
        with path.open("w", encoding="utf-8") as file:
            file.write(template)

        return str(path)
