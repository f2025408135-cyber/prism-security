"""Tests for the Lifecycle analyzer."""

import pytest

from prism.models.state import StateMachine, State, StateTransition
from prism.statemachine.lifecycle import LifecycleAnalyzer

def test_find_terminal_states() -> None:
    """Test identifying terminal states from a machine."""
    s1 = State(name="created")
    s2 = State(name="active")
    s3 = State(name="deleted")
    
    t1 = StateTransition(from_state="created", to_state="active", endpoint_method="PUT", endpoint_url="/a")
    t2 = StateTransition(from_state="active", to_state="deleted", endpoint_method="DELETE", endpoint_url="/b")
    
    machine = StateMachine(resource_name="doc", states=(s1, s2, s3), transitions=(t1, t2))
    analyzer = LifecycleAnalyzer()
    
    terminal = analyzer.find_terminal_states(machine)
    
    assert len(terminal) == 1
    assert "deleted" in terminal

def test_is_linear_lifecycle() -> None:
    """Test determining if a lifecycle is linear."""
    s1 = State(name="a")
    s2 = State(name="b")
    s3 = State(name="c")
    
    # Linear: a -> b -> c
    t1 = StateTransition(from_state="a", to_state="b", endpoint_method="1", endpoint_url="2")
    t2 = StateTransition(from_state="b", to_state="c", endpoint_method="1", endpoint_url="2")
    
    m_linear = StateMachine(resource_name="r", states=(s1, s2, s3), transitions=(t1, t2))
    
    # Non-linear: a -> b AND a -> c
    t3 = StateTransition(from_state="a", to_state="c", endpoint_method="1", endpoint_url="2")
    
    m_nonlinear = StateMachine(resource_name="r", states=(s1, s2, s3), transitions=(t1, t3))
    
    analyzer = LifecycleAnalyzer()
    
    assert analyzer.is_linear_lifecycle(m_linear) is True
    assert analyzer.is_linear_lifecycle(m_nonlinear) is False
