"""Tests for constants."""

from prism.constants import (
    HTTP_OK, HTTP_UNAUTHORIZED, HTTP_FORBIDDEN, DEFAULT_TIMEOUT_SECONDS
)

def test_constants_values() -> None:
    """Verify that critical constants have expected values."""
    assert HTTP_OK == 200
    assert HTTP_UNAUTHORIZED == 401
    assert HTTP_FORBIDDEN == 403
    assert DEFAULT_TIMEOUT_SECONDS == 30.0
