"""Tests for inconsistency detection."""

import pytest
import networkx as nx

from prism.mapper.inconsistency import InconsistencyDetector, AuthzInconsistency
from prism.models.authz import AuthzDecision, AuthzMatrix

def test_find_inconsistencies() -> None:
    """Test detecting logic gaps between endpoints."""
    detector = InconsistencyDetector()
    graph = nx.DiGraph()
    
    # Source generated ID 123
    # Target consumed ID 123
    graph.add_edge("GET /users", "GET /users/123", identifier="123")
    
    # Principal u1 can see the collection (source) but cannot see the item (target)
    d1 = AuthzDecision(
        endpoint_url="/users", endpoint_method="GET", principal_id="u1",
        http_status=200, is_authorized=True, timing_ms=10.0
    )
    d2 = AuthzDecision(
        endpoint_url="/users/123", endpoint_method="GET", principal_id="u1",
        http_status=403, is_authorized=False, timing_ms=5.0
    )
    
    # Principal u2 cannot see the collection (source) but CAN see the item (target) - BOLA
    d3 = AuthzDecision(
        endpoint_url="/users", endpoint_method="GET", principal_id="u2",
        http_status=403, is_authorized=False, timing_ms=10.0
    )
    d4 = AuthzDecision(
        endpoint_url="/users/123", endpoint_method="GET", principal_id="u2",
        http_status=200, is_authorized=True, timing_ms=5.0
    )
    
    matrix = AuthzMatrix(decisions=(d1, d2, d3, d4))
    
    inconsistencies = detector.find_inconsistencies(graph, matrix)
    
    assert len(inconsistencies) == 2
    
    u1_inc = next(i for i in inconsistencies if i.principal_id == "u1")
    assert u1_inc.accessible_endpoint == "GET /users"
    assert u1_inc.denied_endpoint == "GET /users/123"
    
    u2_inc = next(i for i in inconsistencies if i.principal_id == "u2")
    assert u2_inc.accessible_endpoint == "GET /users/123"
    assert u2_inc.denied_endpoint == "GET /users"
    assert "BOLA" in u2_inc.reason
