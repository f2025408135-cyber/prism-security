"""Security invariant and result models."""

from pydantic import BaseModel, ConfigDict


class Invariant(BaseModel):
    """Represents a security property that must hold true.

    Attributes:
        id: Unique identifier for this invariant.
        description: Description of the security property.
        severity: The potential severity if this invariant is violated.
    """
    model_config = ConfigDict(frozen=True)

    id: str
    description: str
    severity: str = "HIGH"


class InvariantResult(BaseModel):
    """Represents the outcome of checking an invariant.

    Attributes:
        invariant_id: The ID of the invariant checked.
        is_violated: True if the invariant was proven false.
        proof_chain: A list of primitive IDs that, combined, prove the violation.
    """
    model_config = ConfigDict(frozen=True)

    invariant_id: str
    is_violated: bool
    proof_chain: tuple[str, ...] = ()
