"""State machine graph construction."""

import structlog
from typing import Any
from collections import defaultdict

from prism.models.state import State, StateTransition, StateMachine
from prism.statemachine.detector import StateChangeDetector

logger = structlog.get_logger(__name__)


class StateMachineBuilder:
    """Constructs StateMachine models from observed mutations."""

    def __init__(self, detector: StateChangeDetector) -> None:
        self.detector = detector

    def build(self, traffic_records: list[dict[str, Any]]) -> tuple[StateMachine, ...]:
        """Process traffic logs and return inferred StateMachines per resource.

        Args:
            traffic_records: Raw traffic logs from storage.

        Returns:
            A tuple of inferred StateMachines for each identified resource.
        """
        logger.info("statemachine_build_started", records=len(traffic_records))

        # 1. Isolate only the operations that actually changed state
        mutations = self.detector.detect_mutations(traffic_records)

        # 2. Group mutations by inferred Resource Name
        resource_mutations: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for record in mutations:
            url = record.get("request", {}).get("url", "")
            resource = self.detector.identify_resource_name(url)
            resource_mutations[resource].append(record)

        machines: list[StateMachine] = []

        # 3. Build a simple StateMachine for each resource
        for resource, records in resource_mutations.items():
            states: set[State] = set()
            transitions: set[StateTransition] = set()

            # We use basic heuristic states based on HTTP methods
            # In a true dynamic system, we'd look at response body changes
            for record in records:
                method = record.get("request", {}).get("method", "").upper()
                url = record.get("request", {}).get("url", "")

                if method == "POST":
                    from_st = "non_existent"
                    to_st = "created"
                elif method in ("PUT", "PATCH"):
                    from_st = "created"
                    to_st = "updated"
                elif method == "DELETE":
                    from_st = "updated" # or created
                    to_st = "deleted"
                else:
                    continue

                states.add(State(name=from_st, description=f"State inferred from {method}"))
                states.add(State(name=to_st, description=f"State inferred from {method}"))
                
                transitions.add(StateTransition(
                    from_state=from_st,
                    to_state=to_st,
                    endpoint_method=method,
                    endpoint_url=url
                ))

            if states and transitions:
                machines.append(
                    StateMachine(
                        resource_name=resource,
                        states=tuple(states),
                        transitions=tuple(transitions)
                    )
                )

        logger.info("statemachine_build_completed", resources_mapped=len(machines))
        return tuple(machines)
