"""Tests for the Idempotency detector."""

import pytest
from typing import Any

from prism.models.state import StateMachine, State, StateTransition
from prism.statemachine.idempotency import IdempotencyDetector

def test_identify_single_use_operations() -> None:
    """Test detecting endpoints that succeed only once per resource."""
    detector = IdempotencyDetector()
    
    machine = StateMachine(
        resource_name="users",
        states=(),
        transitions=()
    )
    
    # Simulate a POST that creates, then 409s
    # And a DELETE that succeeds, then 404s
    traffic: list[dict[str, Any]] = [
        {"request": {"method": "POST", "url": "https://api.com/users/new"}, "response": {"status_code": 201}},
        {"request": {"method": "POST", "url": "https://api.com/users/new"}, "response": {"status_code": 409}},
        {"request": {"method": "DELETE", "url": "https://api.com/users/123"}, "response": {"status_code": 204}},
        {"request": {"method": "DELETE", "url": "https://api.com/users/123"}, "response": {"status_code": 404}},
        {"request": {"method": "PUT", "url": "https://api.com/users/123"}, "response": {"status_code": 200}},
        {"request": {"method": "PUT", "url": "https://api.com/users/123"}, "response": {"status_code": 200}},
    ]
    
    single_use = detector.identify_single_use_operations(machine, traffic)
    
    assert len(single_use) == 2
    assert "POST https://api.com/users/new" in single_use
    assert "DELETE https://api.com/users/123" in single_use
    assert "PUT https://api.com/users/123" not in single_use
