"""Tests for the Replay engine."""

import pytest
import respx
import httpx
from pathlib import Path

from prism.http.client import AsyncHttpClient
from prism.http.storage import TrafficStorage
from prism.http.scope import ScopeGuard
from prism.http.rate_limiter import RateLimiter
from prism.http.replay import ReplayEngine
from prism.exceptions import NetworkError

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
async def test_replay_success(client: AsyncHttpClient, storage: TrafficStorage) -> None:
    """Test replaying a stored exchange ID."""
    
    # Pre-populate a fake exchange
    exchange_id = storage.store(
        principal_id="user_1",
        request_kwargs={
            "method": "POST", 
            "url": "https://api.example.com/replay_test",
            "json": {"foo": "bar"}
        },
        status_code=500,
        response_headers=(),
        response_body="Internal error",
        timing_ms=50.0
    )
    
    # Mock the new request with a 200 response
    url = "https://api.example.com/replay_test"
    respx.post(url).mock(return_value=httpx.Response(200, json={"foo": "bar"}))
    
    engine = ReplayEngine(client, storage)
    response = await engine.replay_by_id(exchange_id)
    
    assert response is not None
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_replay_not_found(client: AsyncHttpClient, storage: TrafficStorage) -> None:
    """Test replaying an ID that doesn't exist."""
    engine = ReplayEngine(client, storage)
    response = await engine.replay_by_id("nonexistent_id")
    
    assert response is None
