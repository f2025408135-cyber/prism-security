"""Rate limiting engine."""

import time
import asyncio
import structlog

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Enforces rate limits on HTTP requests.

    Ensures that the application does not exceed the allowed requests
    per second (RPS) threshold.
    """

    def __init__(self, max_rps: float) -> None:
        """Initialize the rate limiter.

        Args:
            max_rps: Maximum allowed requests per second.
        """
        self.max_rps = max_rps
        self._min_interval = 1.0 / max_rps if max_rps > 0 else 0
        self._last_request_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to send a request, pausing if necessary."""
        if self._min_interval <= 0:
            return

        async with self._lock:
            current_time = time.monotonic()
            elapsed = current_time - self._last_request_time
            wait_time = self._min_interval - elapsed

            if wait_time > 0:
                # Log debug instead of warning since waiting is expected behavior
                logger.debug("rate_limiter_waiting", wait_time=wait_time)
                await asyncio.sleep(wait_time)
                self._last_request_time = current_time + wait_time
            else:
                self._last_request_time = current_time

    def update_rate(self, new_rps: float) -> None:
        """Dynamically update the RPS limit (e.g., in response to 429 status).

        Args:
            new_rps: The new maximum allowed requests per second.
        """
        self.max_rps = new_rps
        self._min_interval = 1.0 / new_rps if new_rps > 0 else 0
        logger.info("rate_limiter_updated", new_rps=new_rps)
