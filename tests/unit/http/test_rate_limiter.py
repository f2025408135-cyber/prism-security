"""Tests for the RateLimiter implementation."""

import pytest
import time
import asyncio
from prism.http.rate_limiter import RateLimiter

@pytest.mark.asyncio
async def test_rate_limiter_acquires_immediately() -> None:
    """Test that zero wait happens when limit is high/first request."""
    limiter = RateLimiter(max_rps=100.0)
    
    start = time.monotonic()
    await limiter.acquire()
    await limiter.acquire()
    end = time.monotonic()
    
    # Two requests at 100rps should take ~10ms.
    # Asserting it's relatively fast.
    assert (end - start) < 0.1

@pytest.mark.asyncio
async def test_rate_limiter_throttles_correctly() -> None:
    """Test that the limiter correctly pauses."""
    limiter = RateLimiter(max_rps=10.0) # 100ms per request
    
    start = time.monotonic()
    await limiter.acquire() # 1st immediate
    await limiter.acquire() # 2nd waits 100ms
    await limiter.acquire() # 3rd waits 100ms
    end = time.monotonic()
    
    elapsed = end - start
    assert elapsed >= 0.2  # at least 200ms total wait
    assert elapsed < 0.35  # Shouldn't take absurdly long

def test_rate_limiter_update_rate() -> None:
    """Test dynamically updating the RPS."""
    limiter = RateLimiter(max_rps=50.0)
    assert limiter.max_rps == 50.0
    
    limiter.update_rate(10.0)
    assert limiter.max_rps == 10.0
    assert limiter._min_interval == 0.1
