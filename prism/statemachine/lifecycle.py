"""Resource lifecycle modeling."""

import structlog
from typing import Any

from prism.models.state import StateMachine

logger = structlog.get_logger(__name__)


class LifecycleAnalyzer:
    """Analyzes a StateMachine to determine terminal states and general lifecycles."""

    def find_terminal_states(self, machine: StateMachine) -> tuple[str, ...]:
        """Identify states from which no further transitions are possible.

        Args:
            machine: The StateMachine to analyze.

        Returns:
            A tuple of state names that have incoming edges but no outgoing edges.
        """
        logger.debug("finding_terminal_states", resource=machine.resource_name)

        outgoing_edges: set[str] = set()
        incoming_edges: set[str] = set()

        for transition in machine.transitions:
            outgoing_edges.add(transition.from_state)
            incoming_edges.add(transition.to_state)

        # A terminal state is one that we can transition TO, but never transition FROM
        terminal_states = incoming_edges - outgoing_edges

        # Special fallback: 'deleted' is inherently terminal in REST unless there's an 'undelete'
        if "deleted" in incoming_edges and "deleted" not in outgoing_edges:
            terminal_states.add("deleted")

        return tuple(terminal_states)

    def is_linear_lifecycle(self, machine: StateMachine) -> bool:
        """Determine if the resource follows a simple linear lifecycle.

        Linear: non_existent -> created -> updated -> deleted
        Non-linear: Multiple paths out of a single state (e.g., created -> active OR created -> suspended)

        Args:
            machine: The StateMachine to analyze.

        Returns:
            True if no state has more than one unique outgoing transition destination.
        """
        outgoing_counts: dict[str, set[str]] = {}

        for transition in machine.transitions:
            if transition.from_state not in outgoing_counts:
                outgoing_counts[transition.from_state] = set()
            outgoing_counts[transition.from_state].add(transition.to_state)

        # If any state can branch to multiple DIFFERENT states, it's non-linear
        for to_states in outgoing_counts.values():
            if len(to_states) > 1:
                return False

        return True
