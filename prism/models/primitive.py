"""Primitive facts and primitive graph models."""

from pydantic import BaseModel, ConfigDict


class Primitive(BaseModel):
    """Represents a confirmed security fact observed by an engine.

    Primitives are the fundamental building blocks used by the synthesis
    engine to prove vulnerabilities.

    Attributes:
        id: Unique identifier for this primitive.
        fact_type: The type of fact (e.g., 'authz_bypass', 'state_transition').
        description: Human-readable explanation of the fact.
        evidence_ids: References to evidence objects supporting this fact.
    """
    model_config = ConfigDict(frozen=True)

    id: str
    fact_type: str
    description: str
    evidence_ids: tuple[str, ...] = ()


class PrimitiveGraph(BaseModel):
    """Represents a collection of all primitive facts forming an attack surface.

    Attributes:
        primitives: A tuple of all primitive facts in the graph.
    """
    model_config = ConfigDict(frozen=True)

    primitives: tuple[Primitive, ...] = ()
