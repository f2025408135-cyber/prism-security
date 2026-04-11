"""Primitive schema and type system for synthesis."""

import structlog
from pydantic import BaseModel, ConfigDict

logger = structlog.get_logger(__name__)

# Valid fact types that the synthesis engine understands
VALID_FACT_TYPES = frozenset({
    "authz_bypass", 
    "state_transition", 
    "id_leak", 
    "race_condition",
    "scope_gap"
})


class PrimitiveFact(BaseModel):
    """Represents a strictly typed, confirmed security fact.

    Unlike the base Primitive in models/primitive.py which is just data,
    this adds validation and metadata required for Z3 SMT solving.

    Attributes:
        id: Unique identifier for this primitive.
        fact_type: The category of fact (e.g., 'authz_bypass').
        actor: The principal or role that executed the action.
        target_resource: The resource affected.
        precondition: What must be true BEFORE this fact occurs (e.g., 'state==created').
        postcondition: What is true AFTER this fact occurs (e.g., 'state==deleted').
        evidence_id: Reference to the underlying HTTP log proving this.
    """
    model_config = ConfigDict(frozen=True)

    id: str
    fact_type: str
    actor: str
    target_resource: str
    precondition: str = "True"
    postcondition: str = "True"
    evidence_id: str

    def __post_init__(self) -> None:
        """Validate the fact type."""
        if self.fact_type not in VALID_FACT_TYPES:
            raise ValueError(f"Invalid fact_type: {self.fact_type}")
