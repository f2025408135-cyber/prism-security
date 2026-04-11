"""Tests for TOCTOU pattern detection."""

import pytest

from prism.models.state import StateMachine, StateTransition
from prism.race.toctou import ToctouDetector, ToctouPattern

def test_find_toctou_patterns() -> None:
    """Test analyzing a state machine for Check-Then-Act sequences."""
    detector = ToctouDetector()
    
    # Example: User can only delete if state == active.
    # The "Check" is a generic GET, the "Act" is the DELETE.
    t1 = StateTransition(
        from_state="active", to_state="deleted", 
        endpoint_method="DELETE", endpoint_url="https://api.com/doc/1"
    )
    
    machine = StateMachine(resource_name="doc", states=(), transitions=(t1,))
    patterns = detector.find_patterns(machine)
    
    assert len(patterns) == 1
    assert patterns[0].resource_name == "doc"
    assert patterns[0].check_endpoint == "GET https://api.com/doc/1"
    assert patterns[0].act_endpoint == "DELETE https://api.com/doc/1"
    assert "active" in patterns[0].description
