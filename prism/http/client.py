"""Async HTTP Client wrapper."""

import time
import httpx
import structlog
from typing import Any

from prism.http.rate_limiter import RateLimiter
from prism.interfaces.http import IScopeGuard
from prism.exceptions import NetworkError, ScopeViolationError
from prism.constants import DEFAULT_TIMEOUT_SECONDS

logger = structlog.get_logger(__name__)


class AsyncHttpClient:
    """Wraps httpx.AsyncClient with rate limiting, scope guarding, and error handling."""

    def __init__(self, scope_guard: IScopeGuard, rate_limiter: RateLimiter):
        """Initialize the client.

        Args:
            scope_guard: The configured IScopeGuard instance.
            rate_limiter: The configured RateLimiter instance.
        """
        self.scope_guard = scope_guard
        self.rate_limiter = rate_limiter
        # Require HTTP/2 support as per dependencies
        self._client = httpx.AsyncClient(http2=True, timeout=DEFAULT_TIMEOUT_SECONDS)

    async def request(self, method: str, url: str, **kwargs: Any) -> tuple[httpx.Response, float]:
        """Send an HTTP request with safety constraints.

        Args:
            method: The HTTP method (e.g., 'GET').
            url: The exact URL to request.
            **kwargs: Additional arguments to pass to httpx (headers, json, etc.).

        Returns:
            A tuple of (httpx.Response, request_duration_ms).

        Raises:
            ScopeViolationError: If the URL is out of scope.
            NetworkError: On timeout, connect error, or protocol error.
        """
        # 1. SCOPE CHECK - Safety Critical
        if not self.scope_guard.is_in_scope(url):
            logger.warning("probe_blocked_out_of_scope", url=url)
            raise ScopeViolationError(f"URL out of scope: {url}")

        # 2. RATE LIMITER
        await self.rate_limiter.acquire()

        # 3. EXECUTE WITH ERROR HANDLING
        start_time = time.monotonic()
        try:
            logger.debug("http_request_sending", method=method, url=url)
            response = await self._client.request(method, url, **kwargs)
        except httpx.TimeoutException as e:
            logger.error("probe_timeout", url=url, timeout=DEFAULT_TIMEOUT_SECONDS, error=str(e))
            raise NetworkError(f"Timeout after {DEFAULT_TIMEOUT_SECONDS}s: {url}") from e
        except httpx.ConnectError as e:
            logger.error("probe_connect_error", url=url, error=str(e))
            raise NetworkError(f"Connection failed: {url}") from e
        except Exception as e:
            logger.error("probe_unexpected_error", url=url, error=str(e))
            raise NetworkError(f"Unexpected HTTP error: {url} -> {e}") from e

        end_time = time.monotonic()
        duration_ms = (end_time - start_time) * 1000.0

        # Log significant operations (never log token values or full request bodies)
        logger.info(
            "http_request_completed", 
            method=method, 
            url=url, 
            status=response.status_code, 
            duration_ms=round(duration_ms, 2)
        )

        return response, duration_ms

    async def close(self) -> None:
        """Close the underlying HTTP client connections."""
        await self._client.aclose()
