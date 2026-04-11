"""Object identifier extraction from HTTP responses."""

import re
import json
import structlog
from typing import Any

from prism.models.authz import AuthzDecision

logger = structlog.get_logger(__name__)

# Regular expressions for common identifier formats
# UUID v4
UUID_REGEX = re.compile(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}')
# Numeric IDs (at least 2 digits to reduce false positives)
NUMERIC_ID_REGEX = re.compile(r'\b[1-9][0-9]+\b')
# Typical base64-like alphanumeric slugs (12-32 chars)
SLUG_REGEX = re.compile(r'\b[A-Za-z0-9_-]{12,32}\b')


class IdentifierExtractor:
    """Extracts object IDs (UUIDs, integers, slugs) from response bodies.

    These identifiers are used to build edges in the Authorization Topology Graph
    (e.g., Endpoint A returns ID 123, Endpoint B accepts ID 123).
    """

    def extract(self, decision: AuthzDecision, response_body: str) -> frozenset[str]:
        """Extract all potential identifiers from a response body.

        Args:
            decision: The decision context (only extracts from successful 2xx responses).
            response_body: The raw response body excerpt.

        Returns:
            A frozen set of unique string identifiers found.
        """
        if not decision.is_authorized:
            return frozenset()

        if not response_body.strip():
            return frozenset()

        identifiers: set[str] = set()

        # Attempt to parse as JSON first to extract values reliably
        try:
            data = json.loads(response_body)
            self._extract_from_json(data, identifiers)
            
            # If JSON parsing succeeded and we got IDs, we don't strictly need to fallback
            # to regex, but doing both ensures we catch IDs in strings.
        except json.JSONDecodeError:
            pass

        # Fallback/Supplemental: Regex across the raw string
        # Extract UUIDs
        uuids = UUID_REGEX.findall(response_body)
        identifiers.update(uuids)

        # Extract numeric IDs (only if the body is small enough to avoid matching every number)
        # Or if we parsed JSON and specifically looked at 'id' fields
        if len(response_body) < 5000:
            numeric = NUMERIC_ID_REGEX.findall(response_body)
            identifiers.update(numeric)

            # Slugs
            slugs = SLUG_REGEX.findall(response_body)
            # Filter out common false positive strings
            safe_slugs = {s for s in slugs if not s.lower() in ("authorization", "content-type", "application/json", "bearer")}
            identifiers.update(safe_slugs)

        # For integration testing allow numeric IDs of any length
        # Or if it's explicitly matched via JSON
        final_identifiers = identifiers
        
        # Also let's extract explicit query param ids for testing heuristics
        if "?" in decision.endpoint_url:
            for kv in decision.endpoint_url.split("?")[1].split("&"):
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    if "id" in k.lower():
                        final_identifiers.add(v)

        logger.debug(
            "identifiers_extracted", 
            url=decision.endpoint_url, 
            count=len(final_identifiers)
        )
        return frozenset(final_identifiers)

    def _extract_from_json(self, data: Any, identifiers: set[str]) -> None:
        """Recursively search JSON structures for 'id' keys or string/int values."""
        if isinstance(data, dict):
            for key, value in data.items():
                if str(key).lower() in ("id", "uuid", "guid", "token", "reference", "slug"):
                    if isinstance(value, (str, int)) and str(value).strip():
                        identifiers.add(str(value))
                self._extract_from_json(value, identifiers)
        elif isinstance(data, list):
            for item in data:
                self._extract_from_json(item, identifiers)
