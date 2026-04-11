"""Tests for the endpoint prober."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from prism.interfaces.http import IHTTPExecutor
from prism.models.endpoint import Endpoint
from prism.models.principal import Principal
from prism.models.authz import AuthzDecision
from prism.mapper.prober import EndpointProber

@pytest.mark.asyncio
async def test_endpoint_prober_maps_principals() -> None:
    """Test concurrent execution of probes across multiple principals."""
    
    # Mock HTTP Executor
    executor = AsyncMock(spec=IHTTPExecutor)
    
    ep = Endpoint(method="GET", url="https://api.example.com/admin")
    
    p1 = Principal(id="u1", name="alice")
    p2 = Principal(id="u2", name="bob")
    
    # Fake decisions returning
    d1 = AuthzDecision(
        endpoint_url=ep.url, endpoint_method=ep.method, principal_id=p1.id,
        http_status=200, is_authorized=True, timing_ms=10.0
    )
    d2 = AuthzDecision(
        endpoint_url=ep.url, endpoint_method=ep.method, principal_id=p2.id,
        http_status=403, is_authorized=False, timing_ms=5.0
    )
    
    # Sequential return mock based on call count
    executor.probe.side_effect = [d1, d2]
    
    prober = EndpointProber(executor)
    profile = await prober.map_endpoint(ep, (p1, p2))
    
    assert len(profile) == 2
    assert executor.probe.call_count == 2
    
    # Check that decisions are preserved correctly
    assert profile[0].principal_id == "u1"
    assert profile[0].http_status == 200
    assert profile[1].principal_id == "u2"
    assert profile[1].http_status == 403
