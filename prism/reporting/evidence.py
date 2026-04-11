"""Evidence chain construction and formatting."""

import structlog

from prism.models.finding import Evidence

logger = structlog.get_logger(__name__)


class EvidenceBuilder:
    """Constructs formal evidence blocks for reports."""

    def format_evidence_chain(self, evidence: tuple[Evidence, ...]) -> str:
        """Format a sequence of evidence into a Markdown-friendly citation block.

        Args:
            evidence: The tuple of Evidence objects.

        Returns:
            A formatted string ready for inclusion in a report.
        """
        logger.debug("formatting_evidence_chain", count=len(evidence))

        if not evidence:
            return "No concrete HTTP evidence provided."

        output = "### Evidence Chain\n\n"

        for i, ev in enumerate(evidence, 1):
            output += f"#### [{i}] {ev.description}\n"
            
            output += "**Request:**\n```http\n"
            output += f"{ev.request_excerpt}\n```\n\n"
            
            output += "**Response Excerpt:**\n```http\n"
            output += f"{ev.response_excerpt}\n```\n\n"
            
            output += "---\n"

        return output
