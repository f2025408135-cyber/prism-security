"""Tests for State Machine Inference Engine."""

import pytest
from typing import Any

from prism.statemachine.detector import StateChangeDetector
from prism.statemachine.builder import StateMachineBuilder
from prism.statemachine.observer import TrafficObserver
from prism.models.state import StateMachine

@pytest.fixture
def mock_traffic() -> list[dict[str, Any]]:
    return [
        # GET shouldn't trigger state transition
        {"request": {"method": "GET", "url": "https://api.example.com/users"}, "response": {"status_code": 200}},
        # POST triggers non_existent -> created
        {"request": {"method": "POST", "url": "https://api.example.com/users"}, "response": {"status_code": 201}},
        # Failed POST shouldn't trigger state transition
        {"request": {"method": "POST", "url": "https://api.example.com/users"}, "response": {"status_code": 400}},
        # PUT triggers created -> updated
        {"request": {"method": "PUT", "url": "https://api.example.com/users/123"}, "response": {"status_code": 200}},
        # DELETE triggers updated -> deleted
        {"request": {"method": "DELETE", "url": "https://api.example.com/users/123"}, "response": {"status_code": 204}},
        # Another resource POST
        {"request": {"method": "POST", "url": "https://api.example.com/invoices"}, "response": {"status_code": 201}},
    ]

def test_detector_identifies_mutations(mock_traffic: list[dict[str, Any]]) -> None:
    """Test filtering of state-mutating requests."""
    detector = StateChangeDetector()
    mutations = detector.detect_mutations(mock_traffic)
    
    assert len(mutations) == 4
    methods = [m["request"]["method"] for m in mutations]
    assert "GET" not in methods
    assert methods.count("POST") == 2
    assert methods.count("PUT") == 1
    assert methods.count("DELETE") == 1

def test_detector_identifies_resource_name() -> None:
    """Test extraction of logical resource names from URLs."""
    detector = StateChangeDetector()
    
    assert detector.identify_resource_name("https://api.com/users") == "users"
    assert detector.identify_resource_name("https://api.com/v1/invoices/99") == "invoices"
    assert detector.identify_resource_name("https://api.com/docs/abcdef-1234-xyz") == "docs"

def test_builder_constructs_state_machines(mock_traffic: list[dict[str, Any]]) -> None:
    """Test mapping of raw traffic into state machine models per resource."""
    detector = StateChangeDetector()
    builder = StateMachineBuilder(detector)
    
    machines = builder.build(mock_traffic)
    
    # We expect 2 resources: 'users' and 'invoices'
    assert len(machines) == 2
    
    users_sm = next(m for m in machines if m.resource_name == "users")
    assert isinstance(users_sm, StateMachine)
    
    # States should be: non_existent, created, updated, deleted
    state_names = [s.name for s in users_sm.states]
    assert "non_existent" in state_names
    assert "created" in state_names
    assert "updated" in state_names
    assert "deleted" in state_names
    
    # Transitions:
    # POST -> non_existent to created
    # PUT -> created to updated
    # DELETE -> updated to deleted
    assert len(users_sm.transitions) == 3
    post_trans = next(t for t in users_sm.transitions if t.endpoint_method == "POST")
    assert post_trans.from_state == "non_existent"
    assert post_trans.to_state == "created"

def test_observer_interface_compliance(mock_traffic: list[dict[str, Any]]) -> None:
    """Test the traffic observer properly wraps the builder."""
    detector = StateChangeDetector()
    builder = StateMachineBuilder(detector)
    observer = TrafficObserver(builder)
    
    machines = observer.observe(mock_traffic)
    assert len(machines) == 2
