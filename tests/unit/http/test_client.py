"""Tests for Async HTTP Client wrapper."""

import pytest
import respx
import httpx
from unittest.mock import AsyncMock

from prism.http.client import AsyncHttpClient
from prism.http.scope import ScopeGuard
from prism.http.rate_limiter import RateLimiter
from prism.exceptions import NetworkError, ScopeViolationError

@pytest.fixture
def scope_guard() -> ScopeGuard:
    return ScopeGuard(initial_patterns=("https://api.example.com/*",))

@pytest.fixture
def rate_limiter() -> RateLimiter:
    return RateLimiter(max_rps=100.0)

@pytest.mark.asyncio
@respx.mock
async def test_client_request_success(scope_guard: ScopeGuard, rate_limiter: RateLimiter) -> None:
    """Test successful HTTP request via wrapper."""
    client = AsyncHttpClient(scope_guard, rate_limiter)
    
    url = "https://api.example.com/users"
    respx.get(url).mock(return_value=httpx.Response(200, json={"status": "ok"}))
    
    response, duration = await client.request("GET", url, headers={"X-Test": "1"})
    
    assert response.status_code == 200
    assert duration > 0.0
    await client.close()

@pytest.mark.asyncio
async def test_client_request_out_of_scope(scope_guard: ScopeGuard, rate_limiter: RateLimiter) -> None:
    """Test that out of scope requests are blocked."""
    client = AsyncHttpClient(scope_guard, rate_limiter)
    
    with pytest.raises(ScopeViolationError, match="out of scope"):
        await client.request("GET", "https://evil.com/data")
        
    await client.close()

@pytest.mark.asyncio
@respx.mock
async def test_client_request_timeout(scope_guard: ScopeGuard, rate_limiter: RateLimiter) -> None:
    """Test timeout translation to NetworkError."""
    client = AsyncHttpClient(scope_guard, rate_limiter)
    
    url = "https://api.example.com/timeout"
    respx.get(url).mock(side_effect=httpx.TimeoutException("mock timeout"))
    
    with pytest.raises(NetworkError, match="Timeout after"):
        await client.request("GET", url)
        
    await client.close()

@pytest.mark.asyncio
@respx.mock
async def test_client_request_connect_error(scope_guard: ScopeGuard, rate_limiter: RateLimiter) -> None:
    """Test connect error translation to NetworkError."""
    client = AsyncHttpClient(scope_guard, rate_limiter)
    
    url = "https://api.example.com/error"
    respx.get(url).mock(side_effect=httpx.ConnectError("mock connect err"))
    
    with pytest.raises(NetworkError, match="Connection failed"):
        await client.request("GET", url)
        
    await client.close()
