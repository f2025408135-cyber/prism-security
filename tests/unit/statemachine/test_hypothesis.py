"""Tests for Hypothesis generator."""

import pytest

from prism.models.state import StateMachine, State, StateTransition
from prism.statemachine.hypothesis import HypothesisGenerator, StateViolationHypothesis

def test_generate_hypotheses() -> None:
    """Test creating attack hypotheses from state data."""
    generator = HypothesisGenerator()
    
    t1 = StateTransition(from_state="created", to_state="deleted", endpoint_method="DELETE", endpoint_url="/users/1")
    machine = StateMachine(resource_name="users", states=(), transitions=(t1,))
    
    terminal_states = ("deleted",)
    single_use = ("POST /users",)
    
    hyps = generator.generate(machine, terminal_states, single_use)
    
    assert len(hyps) == 3
    
    types = [h.hypothesis_type for h in hyps]
    assert "FORWARD_SKIP" in types
    assert "BACKWARD_REPLAY" in types
    assert "SINGLE_USE_RACE" in types
    
    # Verify the SINGLE_USE_RACE hypothesis parsed the signature correctly
    race_hyp = next(h for h in hyps if h.hypothesis_type == "SINGLE_USE_RACE")
    assert race_hyp.target_method == "POST"
    assert race_hyp.target_endpoint == "/users"
