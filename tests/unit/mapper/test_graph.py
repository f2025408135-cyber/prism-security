"""Tests for NetworkX graph builder."""

import pytest
from prism.mapper.identifier import IdentifierExtractor
from prism.mapper.graph import GraphBuilder
from prism.models.authz import AuthzMatrix, AuthzDecision

def test_build_topology_graph() -> None:
    """Test mapping object flows between endpoints."""
    extractor = IdentifierExtractor()
    builder = GraphBuilder(extractor)
    
    # Endpoint A returns ID '555'
    d1 = AuthzDecision(
        endpoint_url="/api/users", endpoint_method="POST", principal_id="u1",
        http_status=201, is_authorized=True, timing_ms=10.0
    )
    # Endpoint B consumes ID '555'
    d2 = AuthzDecision(
        endpoint_url="/api/users/555", endpoint_method="GET", principal_id="u1",
        http_status=200, is_authorized=True, timing_ms=5.0
    )
    
    matrix = AuthzMatrix(decisions=(d1, d2))
    
    response_bodies = {
        "/api/users": '{"id": 555, "name": "Bob"}',
        "/api/users/555": '{"id": 555, "name": "Bob"}'
    }
    
    graph = builder.build_topology_graph(matrix, response_bodies)
    
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 1
    
    # Edge flows from POST /users -> GET /users/555
    edges = list(graph.edges(data=True))
    source, target, data = edges[0]
    
    assert source == "POST /api/users"
    assert target == "GET /api/users/555"
    assert data["identifier"] == "555"
