"""Tests for Primitive Graph Manager."""

import pytest
import networkx as nx
from prism.synthesis.primitive import PrimitiveFact
from prism.synthesis.graph import PrimitiveGraphManager

def test_graph_manager_add_and_retrieve() -> None:
    """Test adding primitives and retrieving them by type."""
    manager = PrimitiveGraphManager()
    
    f1 = PrimitiveFact(id="1", fact_type="authz_bypass", actor="u1", target_resource="doc", precondition="a", postcondition="b", evidence_id="e1")
    f2 = PrimitiveFact(id="2", fact_type="state_transition", actor="u1", target_resource="doc", precondition="b", postcondition="c", evidence_id="e2")
    
    manager.add_primitive(f1)
    manager.add_primitive(f2)
    
    assert manager.graph.number_of_nodes() == 3
    assert manager.graph.number_of_edges() == 2
    
    # Retrieve by type
    authz_facts = manager.get_facts_by_type("authz_bypass")
    assert len(authz_facts) == 1
    assert authz_facts[0].id == "1"
    assert authz_facts[0].fact_type == "authz_bypass"
    
    state_facts = manager.get_facts_by_type("state_transition")
    assert len(state_facts) == 1
    assert state_facts[0].id == "2"

def test_graph_manager_paths() -> None:
    """Test pathfinding between preconditions and postconditions."""
    manager = PrimitiveGraphManager()
    
    f1 = PrimitiveFact(id="1", fact_type="authz_bypass", actor="u1", target_resource="res", precondition="start", postcondition="mid", evidence_id="e1")
    f2 = PrimitiveFact(id="2", fact_type="authz_bypass", actor="u1", target_resource="res", precondition="mid", postcondition="end", evidence_id="e2")
    
    manager.add_primitive(f1)
    manager.add_primitive(f2)
    
    paths = manager.get_all_paths("res:start", "res:end")
    assert len(paths) == 1
    assert paths[0] == ["res:start", "res:mid", "res:end"]
