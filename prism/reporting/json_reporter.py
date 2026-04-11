"""Machine-readable JSON reporter."""

import json
import structlog
from typing import Any
from pathlib import Path

from prism.models.finding import Finding

logger = structlog.get_logger(__name__)


class JsonReporter:
    """Generates JSON output for pipeline integrations."""

    def generate(self, findings: tuple[Finding, ...], output_path: str) -> str:
        """Serialize findings to a JSON file.

        Args:
            findings: The tuple of confirmed findings.
            output_path: Where to save the file.

        Returns:
            The path to the generated file.
        """
        logger.info("json_report_generated", path=output_path)
        
        # Convert frozen pydantic models to dicts
        data: list[dict[str, Any]] = [f.model_dump() for f in findings]
        
        report = {
            "version": "1.0",
            "findings_count": len(findings),
            "findings": data
        }

        path = Path(output_path)
        with path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        return str(path)
