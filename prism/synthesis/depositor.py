"""Cross-engine primitive deposition."""

import uuid
import structlog
from typing import Any

from prism.synthesis.primitive import PrimitiveFact, VALID_FACT_TYPES
from prism.synthesis.graph import PrimitiveGraphManager

logger = structlog.get_logger(__name__)


class PrimitiveDepositor:
    """Central funnel for all engines to deposit findings into the graph."""

    def __init__(self, graph_manager: PrimitiveGraphManager) -> None:
        """Initialize the depositor.

        Args:
            graph_manager: The graph manager to deposit facts into.
        """
        self.graph_manager = graph_manager

    def deposit(
        self, 
        fact_type: str, 
        actor: str, 
        target_resource: str, 
        evidence_id: str,
        precondition: str = "True",
        postcondition: str = "True"
    ) -> str:
        """Create a PrimitiveFact and deposit it into the graph.

        Args:
            fact_type: Must be in VALID_FACT_TYPES.
            actor: The principal executing the action.
            target_resource: The resource being targeted.
            evidence_id: UUID referencing TrafficStorage.
            precondition: Required starting state.
            postcondition: Resulting state.

        Returns:
            The generated ID of the deposited primitive.

        Raises:
            ValueError: If fact_type is invalid.
        """
        if fact_type not in VALID_FACT_TYPES:
            logger.error("invalid_primitive_type_rejected", type=fact_type)
            raise ValueError(f"Invalid fact_type: {fact_type}")

        fact_id = str(uuid.uuid4())
        
        fact = PrimitiveFact(
            id=fact_id,
            fact_type=fact_type,
            actor=actor,
            target_resource=target_resource,
            precondition=precondition,
            postcondition=postcondition,
            evidence_id=evidence_id
        )

        self.graph_manager.add_primitive(fact)
        logger.info("primitive_deposited", fact_id=fact_id, type=fact_type, resource=target_resource)
        
        return fact_id
