"""State Machine Inference interfaces."""

from typing import Protocol, Any
from prism.models.state import StateMachine

class IStateMachineObserver(Protocol):
    """Observes HTTP traffic to infer valid state machines."""

    def observe(self, traffic_records: list[dict[str, Any]]) -> tuple[StateMachine, ...]:
        """Process traffic logs and return inferred StateMachines per resource."""
        ...
