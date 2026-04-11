"""Timing window measurement."""

import statistics
import structlog
from pydantic import BaseModel, ConfigDict

from prism.models.authz import AuthzDecision

logger = structlog.get_logger(__name__)


class TimingWindow(BaseModel):
    """Represents the execution time distribution for an endpoint.

    Attributes:
        endpoint_url: The URL measured.
        min_ms: The fastest execution time.
        max_ms: The slowest execution time.
        median_ms: The median execution time.
        is_viable: True if the window is large enough to reasonably exploit.
    """
    model_config = ConfigDict(frozen=True)

    endpoint_url: str
    min_ms: float
    max_ms: float
    median_ms: float
    is_viable: bool


class TimingAnalyzer:
    """Analyzes execution times to determine viable race condition windows."""

    # If an endpoint consistently responds faster than 5ms, it's very hard to exploit
    # concurrently without advanced single-packet techniques.
    MIN_VIABLE_WINDOW_MS = 5.0

    def measure_window(self, endpoint_url: str, decisions: list[AuthzDecision]) -> TimingWindow | None:
        """Calculate the timing distribution from a set of probe decisions.

        Args:
            endpoint_url: The endpoint being analyzed.
            decisions: A list of decisions (must be from the same endpoint).

        Returns:
            A TimingWindow model, or None if no valid timings exist.
        """
        logger.debug("measuring_timing_window", url=endpoint_url, count=len(decisions))

        timings = [d.timing_ms for d in decisions if d.endpoint_url == endpoint_url and d.timing_ms > 0]

        if not timings:
            logger.warning("no_timing_data_available", url=endpoint_url)
            return None

        min_t = min(timings)
        max_t = max(timings)
        median_t = statistics.median(timings)

        # We consider the window viable if the median execution time gives us enough
        # leeway to squeeze concurrent requests into the backend DB transaction frame.
        is_viable = median_t >= self.MIN_VIABLE_WINDOW_MS

        window = TimingWindow(
            endpoint_url=endpoint_url,
            min_ms=round(min_t, 2),
            max_ms=round(max_t, 2),
            median_ms=round(median_t, 2),
            is_viable=is_viable
        )

        logger.info("timing_window_measured", url=endpoint_url, viable=is_viable, median=window.median_ms)
        return window
