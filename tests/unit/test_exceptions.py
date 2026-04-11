"""Tests for custom exceptions."""

import pytest
from prism.exceptions import PrismError, ScopeViolationError, NetworkError

def test_exceptions_inherit_from_base() -> None:
    """Test that all custom exceptions inherit from PrismError."""
    assert issubclass(ScopeViolationError, PrismError)
    assert issubclass(NetworkError, PrismError)

def test_exception_raising() -> None:
    """Test raising and catching a custom exception."""
    with pytest.raises(ScopeViolationError, match="Out of scope"):
        raise ScopeViolationError("Out of scope")
