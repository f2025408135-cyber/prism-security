"""Tests for Primitive Depositor."""

import pytest
from prism.synthesis.graph import PrimitiveGraphManager
from prism.synthesis.depositor import PrimitiveDepositor

def test_primitive_depositor() -> None:
    """Test depositing valid facts into the graph."""
    manager = PrimitiveGraphManager()
    depositor = PrimitiveDepositor(manager)
    
    fact_id = depositor.deposit(
        fact_type="scope_gap",
        actor="u1",
        target_resource="invoice",
        evidence_id="ev_abc",
        precondition="init",
        postcondition="viewed"
    )
    
    assert fact_id is not None
    assert manager.graph.number_of_edges() == 1
    
    # Retrieve the fact
    facts = manager.get_facts_by_type("scope_gap")
    assert len(facts) == 1
    assert facts[0].id == fact_id

def test_primitive_depositor_invalid() -> None:
    """Test depositing invalid facts raises ValueError."""
    manager = PrimitiveGraphManager()
    depositor = PrimitiveDepositor(manager)
    
    with pytest.raises(ValueError, match="Invalid fact_type"):
        depositor.deposit(
            fact_type="not_a_real_type",
            actor="u1",
            target_resource="res",
            evidence_id="e1"
        )
