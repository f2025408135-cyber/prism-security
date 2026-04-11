"""False Positive/True Positive finding classification."""

import structlog

from prism.dialectic.verdict import DebateVerdict
from prism.models.finding import Finding

logger = structlog.get_logger(__name__)


class FalsePositiveClassifier:
    """Updates original finding objects based on dialectic verdicts."""

    def __init__(self, confidence_threshold: float = 0.8) -> None:
        """Initialize the classifier.

        Args:
            confidence_threshold: Minimum confidence required to auto-close a finding as an FP.
        """
        self.confidence_threshold = confidence_threshold

    def classify(self, finding: Finding, verdict: DebateVerdict) -> Finding | None:
        """Process the finding and the verdict.

        If the verdict is a FALSE POSITIVE with high confidence, the finding
        is dropped (returns None). Otherwise, it returns the finding, optionally
        appending the debate rationale to its description.

        Args:
            finding: The original Finding.
            verdict: The verdict from the dialectic engine.

        Returns:
            The Finding if it survives, else None.
        """
        logger.debug("classifying_finding", finding_id=finding.id, is_tp=verdict.is_true_positive)

        # If it's a False Positive and confidence is high enough, we kill the finding
        if not verdict.is_true_positive and verdict.confidence >= self.confidence_threshold:
            logger.info("finding_killed_as_false_positive", finding_id=finding.id)
            return None

        # Otherwise, the finding survives. We append the rationale so the human
        # researcher has context on why the AI thinks it's real.
        updated_description = f"{finding.description}\n\n[Dialectic Rationale]: {verdict.rationale}"
        
        # Create a new updated finding (since it is frozen)
        surviving_finding = Finding(
            id=finding.id,
            title=finding.title,
            description=updated_description,
            cwe_id=finding.cwe_id,
            cvss_vector=finding.cvss_vector,
            evidence=finding.evidence,
            poc=finding.poc
        )

        logger.info("finding_survived_dialectic", finding_id=finding.id)
        return surviving_finding
