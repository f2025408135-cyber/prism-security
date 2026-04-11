"""Violation hypothesis generator for state machines."""

import structlog
from pydantic import BaseModel, ConfigDict

from prism.models.state import StateMachine

logger = structlog.get_logger(__name__)


class StateViolationHypothesis(BaseModel):
    """Represents a hypothesized flaw in the state machine logic to be tested.

    Attributes:
        hypothesis_type: E.g., 'FORWARD_SKIP', 'BACKWARD_REPLAY', 'SINGLE_USE_RACE'.
        resource_name: The resource targeted.
        target_endpoint: The endpoint URL to attack.
        target_method: The HTTP method to use.
        description: Why this hypothesis was generated.
    """
    model_config = ConfigDict(frozen=True)

    hypothesis_type: str
    resource_name: str
    target_endpoint: str
    target_method: str
    description: str


class HypothesisGenerator:
    """Generates testable security hypotheses from a StateMachine model."""

    def generate(
        self, 
        machine: StateMachine, 
        terminal_states: tuple[str, ...],
        single_use_endpoints: tuple[str, ...]
    ) -> tuple[StateViolationHypothesis, ...]:
        """Generate attack hypotheses based on the machine topology.

        Args:
            machine: The StateMachine to analyze.
            terminal_states: States identified as terminal.
            single_use_endpoints: Endpoints identified as single-use.

        Returns:
            A tuple of frozen StateViolationHypothesis models.
        """
        logger.info("generating_hypotheses", resource=machine.resource_name)

        hypotheses: list[StateViolationHypothesis] = []

        # 1. Forward Skip Hypothesis (Bypassing workflow steps)
        # If we must go A -> B -> C. Can we jump A -> C directly?
        # We look for transitions that skip the 'created'/'updated' phases
        for trans in machine.transitions:
            if trans.to_state in terminal_states and trans.from_state != "updated":
                hypotheses.append(
                    StateViolationHypothesis(
                        hypothesis_type="FORWARD_SKIP",
                        resource_name=machine.resource_name,
                        target_endpoint=trans.endpoint_url,
                        target_method=trans.endpoint_method,
                        description=f"Attempt to skip to terminal state '{trans.to_state}' from '{trans.from_state}'."
                    )
                )

        # 2. Backward Replay Hypothesis
        # Can we execute a creation/mutation on a resource that is already terminal?
        for trans in machine.transitions:
            if trans.to_state in terminal_states:
                # We hypothesize calling PUT/PATCH on an item that just went to terminal
                hypotheses.append(
                    StateViolationHypothesis(
                        hypothesis_type="BACKWARD_REPLAY",
                        resource_name=machine.resource_name,
                        target_endpoint=trans.endpoint_url,
                        target_method="PUT", # Generic mutation attempt
                        description=f"Attempt to mutate resource after it reached terminal state '{trans.to_state}'."
                    )
                )

        # 3. Single-Use Race Condition Hypothesis
        # If an endpoint is single-use, it is a prime candidate for TOCTOU concurrency attacks
        for sig in single_use_endpoints:
            parts = sig.split(" ", 1)
            if len(parts) == 2:
                method, url = parts
                hypotheses.append(
                    StateViolationHypothesis(
                        hypothesis_type="SINGLE_USE_RACE",
                        resource_name=machine.resource_name,
                        target_endpoint=url,
                        target_method=method,
                        description=f"Concurrent execution race condition test against single-use endpoint."
                    )
                )

        # Deduplicate
        unique_hypotheses = tuple(set(hypotheses))
        logger.info("hypotheses_generated", count=len(unique_hypotheses))
        return unique_hypotheses
