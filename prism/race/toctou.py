"""Time-Of-Check to Time-Of-Use (TOCTOU) pattern detector."""

import structlog
from pydantic import BaseModel, ConfigDict

from prism.models.state import StateMachine

logger = structlog.get_logger(__name__)


class ToctouPattern(BaseModel):
    """Represents a potential TOCTOU vulnerability sequence.

    Attributes:
        resource_name: The target resource.
        check_endpoint: The endpoint acting as the "Check" (usually a GET).
        act_endpoint: The endpoint acting as the "Act" (usually a mutative method).
        description: Reasoning for this pattern.
    """
    model_config = ConfigDict(frozen=True)

    resource_name: str
    check_endpoint: str
    act_endpoint: str
    description: str


class ToctouDetector:
    """Identifies sequences representing a Check-Then-Act vulnerability."""

    def find_patterns(self, machine: StateMachine) -> tuple[ToctouPattern, ...]:
        """Analyze a state machine for potential TOCTOU relationships.

        A classic REST TOCTOU occurs when a state-changing operation (Act)
        implicitly relies on a precondition (Check). 

        Args:
            machine: The StateMachine to analyze.

        Returns:
            A tuple of frozen ToctouPattern models.
        """
        logger.info("finding_toctou_patterns", resource=machine.resource_name)

        patterns: list[ToctouPattern] = []

        # In a generic API, we look for transitions that modify state
        # The "Check" is conceptually the current state, and the "Act" is the transition.
        # We model this by finding a mutative transition and assuming the "Check" is
        # the GET request to that resource, or the precondition of the transition.

        for trans in machine.transitions:
            if trans.endpoint_method.upper() in ("POST", "PUT", "PATCH", "DELETE"):
                
                # Derive a generic GET for the same resource
                # (Assuming the transition URL is roughly the resource URL)
                check_url = trans.endpoint_url.split("?")[0]
                
                pattern = ToctouPattern(
                    resource_name=machine.resource_name,
                    check_endpoint=f"GET {check_url}",
                    act_endpoint=f"{trans.endpoint_method} {trans.endpoint_url}",
                    description=f"Potential TOCTOU: Mutating from '{trans.from_state}' to '{trans.to_state}'."
                )
                patterns.append(pattern)

        # Deduplicate
        unique_patterns = tuple(set(patterns))
        logger.info("toctou_patterns_found", count=len(unique_patterns))
        return unique_patterns
