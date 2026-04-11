"""Traffic observer tying the builder to the interface."""

import structlog
from typing import Any

from prism.interfaces.statemachine import IStateMachineObserver
from prism.models.state import StateMachine
from prism.statemachine.builder import StateMachineBuilder

logger = structlog.get_logger(__name__)


class TrafficObserver(IStateMachineObserver):
    """Implements IStateMachineObserver by wrapping the StateMachineBuilder."""

    def __init__(self, builder: StateMachineBuilder) -> None:
        self.builder = builder

    def observe(self, traffic_records: list[dict[str, Any]]) -> tuple[StateMachine, ...]:
        """Observe traffic logs and output inferred state machines.

        Args:
            traffic_records: A list of dict records straight from TrafficStorage.

        Returns:
            A tuple of frozen StateMachine models.
        """
        logger.debug("traffic_observer_processing", count=len(traffic_records))
        return self.builder.build(traffic_records)
