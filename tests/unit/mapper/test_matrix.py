"""Tests for the Matrix builder."""

import pytest
from prism.mapper.matrix import MatrixBuilder
from prism.models.authz import AuthzDecision, AuthzMatrix

def test_matrix_builder_aggregates_profiles() -> None:
    """Test that multiple EndpointAuthzProfiles are merged correctly."""
    builder = MatrixBuilder()
    
    p1 = (
        AuthzDecision(
            endpoint_url="/api/1", endpoint_method="GET", principal_id="u1",
            http_status=200, is_authorized=True, timing_ms=10.0
        ),
        AuthzDecision(
            endpoint_url="/api/1", endpoint_method="GET", principal_id="u2",
            http_status=403, is_authorized=False, timing_ms=5.0
        )
    )
    
    p2 = (
        AuthzDecision(
            endpoint_url="/api/2", endpoint_method="POST", principal_id="u1",
            http_status=201, is_authorized=True, timing_ms=15.0
        ),
    )
    
    builder.add_profile(p1)
    builder.add_profile(p2)
    
    matrix = builder.build_matrix()
    
    assert isinstance(matrix, AuthzMatrix)
    assert len(matrix.decisions) == 3
    
    urls = [d.endpoint_url for d in matrix.decisions]
    assert urls.count("/api/1") == 2
    assert urls.count("/api/2") == 1
