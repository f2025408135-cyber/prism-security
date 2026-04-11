"""Scope enforcement guard implementation."""

import fnmatch
from urllib.parse import urlparse
import structlog

from prism.interfaces.http import IScopeGuard

logger = structlog.get_logger(__name__)


class ScopeGuard(IScopeGuard):
    """Enforces scope boundaries to prevent out-of-bounds scanning.

    This is a safety-critical component. It validates that every requested URL
    matches an explicitly permitted scope pattern.
    """

    def __init__(self, initial_patterns: tuple[str, ...] = ()) -> None:
        """Initialize the scope guard.

        Args:
            initial_patterns: A tuple of URL patterns (supports * wildcards).
        """
        self._patterns: set[str] = set(initial_patterns)

    def is_in_scope(self, url: str) -> bool:
        """Determine if a URL is permitted.

        Args:
            url: The exact URL attempting to be probed.

        Returns:
            True if the URL matches any allowed pattern, False otherwise.
        """
        # Normalize the URL by ensuring it doesn't just match substrings maliciously
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                logger.warning("scope_check_failed_invalid_url", url=url)
                return False
        except Exception:
            logger.warning("scope_check_failed_parsing", url=url)
            return False

        for pattern in self._patterns:
            if fnmatch.fnmatch(url, pattern):
                return True

        logger.warning("scope_check_rejected", url=url)
        return False

    def add_scope(self, pattern: str) -> None:
        """Add a URL pattern to the in-scope list.

        Args:
            pattern: The pattern to add (e.g., 'https://api.example.com/*').
        """
        self._patterns.add(pattern)
        logger.info("scope_pattern_added", pattern=pattern)
