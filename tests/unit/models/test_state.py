"""Tests for state machine data models."""

import pytest
from prism.models.state import State, StateTransition, StateMachine

def test_state_creation() -> None:
    """Test creation of a State model."""
    state = State(name="active", description="The resource is available.")
    
    assert state.name == "active"
    assert state.description == "The resource is available."

def test_state_transition_creation() -> None:
    """Test creation of a StateTransition model."""
    transition = StateTransition(
        from_state="created",
        to_state="active",
        endpoint_method="PUT",
        endpoint_url="/resource/activate"
    )
    
    assert transition.from_state == "created"
    assert transition.to_state == "active"
    assert transition.endpoint_method == "PUT"

def test_state_machine_creation() -> None:
    """Test creation of a StateMachine model."""
    s1 = State(name="created")
    s2 = State(name="deleted")
    t1 = StateTransition(
        from_state="created",
        to_state="deleted",
        endpoint_method="DELETE",
        endpoint_url="/resource/1"
    )
    
    machine = StateMachine(
        resource_name="document",
        states=(s1, s2),
        transitions=(t1,)
    )
    
    assert machine.resource_name == "document"
    assert len(machine.states) == 2
    assert len(machine.transitions) == 1

def test_state_is_frozen() -> None:
    """Test that the State model is immutable."""
    state = State(name="init")
    with pytest.raises(Exception):
        state.name = "done"  # type: ignore
