"""Idempotency and single-use operation detection."""

import structlog
from typing import Any
from collections import defaultdict

from prism.models.state import StateMachine

logger = structlog.get_logger(__name__)


class IdempotencyDetector:
    """Detects operations that should only execute successfully once.

    A single-use operation (like DELETE or a POST that creates a strict one-to-one resource)
    loses its mutative effect or fails on the second attempt.
    """

    def identify_single_use_operations(
        self, 
        machine: StateMachine, 
        traffic_records: list[dict[str, Any]]
    ) -> tuple[str, ...]:
        """Identify endpoint signatures that only succeeded once per unique resource ID.

        Args:
            machine: The StateMachine representing the resource.
            traffic_records: Raw traffic logs to observe execution outcomes.

        Returns:
            A tuple of endpoint signatures (Method + URL path) that appear single-use.
        """
        logger.debug("identifying_single_use_operations", resource=machine.resource_name)

        # Map of endpoint_signature -> list of status codes observed
        execution_history: dict[str, list[int]] = defaultdict(list)

        for record in traffic_records:
            req = record.get("request", {})
            resp = record.get("response", {})
            
            method = req.get("method", "").upper()
            url = req.get("url", "")
            status = resp.get("status_code", 0)

            # We only care about mutative operations related to this state machine
            # We use a very simplified check: if the URL contains the resource name
            if machine.resource_name.lower() in url.lower():
                # We strip query params to group the endpoint signature
                base_path = url.split("?")[0]
                sig = f"{method} {base_path}"
                execution_history[sig].append(status)

        single_use: set[str] = set()

        for sig, statuses in execution_history.items():
            method = sig.split(" ")[0]
            
            # PUT and PATCH are inherently idempotent (repeating them is safe and returns 200)
            # We are looking for things that FAIL on the second try (e.g. 404 on second DELETE, 409 on second POST)
            if method in ("PUT", "PATCH"):
                continue

            successes = [s for s in statuses if 200 <= s < 300]
            failures = [s for s in statuses if s >= 400]

            # If we saw it succeed EXACTLY once, and fail subsequently (e.g., 404/409)
            # OR if it's a DELETE (which is almost always single-use per ID in reality)
            if len(successes) == 1 and len(failures) > 0:
                single_use.add(sig)
            elif method == "DELETE" and len(successes) >= 1:
                single_use.add(sig)

        return tuple(single_use)
