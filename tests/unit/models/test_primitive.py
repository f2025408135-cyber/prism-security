"""Tests for primitive data models."""

import pytest
from prism.models.primitive import Primitive, PrimitiveGraph

def test_primitive_creation() -> None:
    """Test creation of a Primitive model."""
    prim = Primitive(
        id="prim_1",
        fact_type="bola_bypass",
        description="User A can read User B's document.",
        evidence_ids=("ev_1", "ev_2")
    )
    
    assert prim.id == "prim_1"
    assert prim.fact_type == "bola_bypass"
    assert len(prim.evidence_ids) == 2

def test_primitive_graph_creation() -> None:
    """Test creation of a PrimitiveGraph model."""
    p1 = Primitive(id="p1", fact_type="x", description="y")
    graph = PrimitiveGraph(primitives=(p1,))
    
    assert len(graph.primitives) == 1
    assert graph.primitives[0].id == "p1"

def test_primitive_is_frozen() -> None:
    """Test that the Primitive model is immutable."""
    prim = Primitive(id="p", fact_type="t", description="d")
    with pytest.raises(Exception):
        prim.fact_type = "new"  # type: ignore
