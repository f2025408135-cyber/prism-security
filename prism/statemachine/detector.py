"""Detection of state-changing HTTP operations."""

import structlog
from typing import Any

logger = structlog.get_logger(__name__)

class StateChangeDetector:
    """Identifies operations that mutate resource state.

    Standard REST heuristics map:
    - POST: Creates a new resource (transitions from NOT_FOUND to CREATED).
    - PUT/PATCH: Mutates an existing resource (transitions state, e.g., ACTIVE -> UPDATED).
    - DELETE: Removes a resource (transitions to DELETED/NOT_FOUND).
    """

    # HTTP Methods that are inherently expected to mutate state
    MUTATIVE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})

    def detect_mutations(self, traffic_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Filter traffic records down to only successful state-changing operations.

        Args:
            traffic_records: Raw traffic records from TrafficStorage.

        Returns:
            A list of traffic records that successfully mutated state (2xx or 3xx responses).
        """
        logger.debug("mutation_detection_started", total_records=len(traffic_records))

        mutations: list[dict[str, Any]] = []

        for record in traffic_records:
            req = record.get("request", {})
            resp = record.get("response", {})
            
            method = req.get("method", "").upper()
            status = resp.get("status_code", 0)

            if method in self.MUTATIVE_METHODS and 200 <= status < 400:
                mutations.append(record)

        logger.debug("mutation_detection_completed", mutative_records=len(mutations))
        return mutations

    def identify_resource_name(self, url: str) -> str:
        """Heuristically identify the resource name from a URL path.

        For example, `https://api.example.com/v1/users/123` -> `users`

        Args:
            url: The endpoint URL.

        Returns:
            The guessed resource collection name.
        """
        # Strip query parameters
        base_path = url.split("?")[0].rstrip("/")
        parts = base_path.split("/")

        # Usually the collection name is the second to last part if the last is an ID
        # or the last part if it's a collection endpoint
        if not parts or len(parts) < 2:
            return "unknown"

        last_part = parts[-1]
        
        # If the last part is numeric or a long UUID-like string or contains dashes, it's likely an item endpoint
        if last_part.isdigit() or len(last_part) > 15 or "-" in last_part:
            return parts[-2].lower()
            
        return last_part.lower()
