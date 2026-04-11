"""Tests for authorization data models."""

import pytest
from prism.models.authz import AuthzDecision, AuthzMatrix

def test_authz_decision_creation() -> None:
    """Test creation of an AuthzDecision model."""
    decision = AuthzDecision(
        endpoint_url="https://api.example.com/admin",
        endpoint_method="DELETE",
        principal_id="user_123",
        http_status=403,
        is_authorized=False,
        timing_ms=12.5
    )
    
    assert decision.endpoint_url == "https://api.example.com/admin"
    assert decision.http_status == 403
    assert decision.is_authorized is False

def test_authz_matrix_creation() -> None:
    """Test creation of an AuthzMatrix model."""
    d1 = AuthzDecision(
        endpoint_url="/public",
        endpoint_method="GET",
        principal_id="user_1",
        http_status=200,
        is_authorized=True,
        timing_ms=5.0
    )
    d2 = AuthzDecision(
        endpoint_url="/private",
        endpoint_method="GET",
        principal_id="user_1",
        http_status=401,
        is_authorized=False,
        timing_ms=3.0
    )
    
    matrix = AuthzMatrix(decisions=(d1, d2))
    
    assert len(matrix.decisions) == 2
    assert matrix.decisions[0].http_status == 200
    assert matrix.decisions[1].http_status == 401

def test_authz_decision_is_frozen() -> None:
    """Test that the AuthzDecision model is immutable."""
    decision = AuthzDecision(
        endpoint_url="/test",
        endpoint_method="GET",
        principal_id="p1",
        http_status=200,
        is_authorized=True,
        timing_ms=1.0
    )
    
    with pytest.raises(Exception):
        decision.is_authorized = False  # type: ignore
