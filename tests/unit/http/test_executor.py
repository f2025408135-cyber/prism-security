"""Tests for the HTTP executor engine."""

import pytest
import respx
import httpx
from pathlib import Path
from unittest.mock import MagicMock

from prism.http.executor import HTTPExecutor
from prism.http.client import AsyncHttpClient
from prism.http.storage import TrafficStorage
from prism.http.scope import ScopeGuard
from prism.http.rate_limiter import RateLimiter
from prism.models.endpoint import Endpoint
from prism.models.principal import Principal

@pytest.fixture
def storage(tmp_path: Path) -> TrafficStorage:
    return TrafficStorage(str(tmp_path))

@pytest.fixture
def client() -> AsyncHttpClient:
    scope = ScopeGuard(("https://api.example.com/*",))
    limiter = RateLimiter(max_rps=100.0)
    return AsyncHttpClient(scope, limiter)

@pytest.mark.asyncio
@respx.mock
async def test_executor_probe_success(client: AsyncHttpClient, storage: TrafficStorage) -> None:
    """Test a successful HTTP probe sets AuthzDecision properly."""
    executor = HTTPExecutor(client, storage)
    
    ep = Endpoint(method="GET", url="https://api.example.com/users")
    principal = Principal(name="user", id="p1")
    
    respx.get(ep.url).mock(return_value=httpx.Response(200))
    
    decision = await executor.probe(ep, principal)
    
    assert decision.endpoint_url == "https://api.example.com/users"
    assert decision.principal_id == "p1"
    assert decision.http_status == 200
    assert decision.is_authorized is True
    
    # Check it was stored
    records = storage.load_all()
    assert len(records) == 1
    assert records[0]["response"]["status_code"] == 200

@pytest.mark.asyncio
@respx.mock
async def test_executor_probe_concurrent(client: AsyncHttpClient, storage: TrafficStorage) -> None:
    """Test N concurrent requests are dispatched."""
    executor = HTTPExecutor(client, storage)
    
    ep = Endpoint(method="GET", url="https://api.example.com/race")
    principal = Principal(name="user", id="p2")
    
    respx.get(ep.url).mock(return_value=httpx.Response(201))
    
    decisions = await executor.probe_concurrent(ep, principal, count=3)
    
    assert len(decisions) == 3
    for d in decisions:
        assert d.http_status == 201
        
    records = storage.load_all()
    assert len(records) == 3
