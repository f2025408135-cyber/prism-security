"""Tests to ensure concrete implementations satisfy interfaces."""

import pytest
from prism.interfaces.http import IScopeGuard
from prism.http.scope import ScopeGuard

def test_scope_guard_satisfies_interface() -> None:
    """Verify that ScopeGuard implements IScopeGuard."""
    guard = ScopeGuard()
    assert isinstance(guard, IScopeGuard)
