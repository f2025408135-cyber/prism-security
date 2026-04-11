"""Tests for the ScopeGuard implementation."""

import pytest
from prism.http.scope import ScopeGuard

def test_scope_guard_initial_patterns() -> None:
    """Test initializing with patterns and basic matching."""
    guard = ScopeGuard(("https://api.example.com/*", "http://localhost:8000/v1/*"))
    
    assert guard.is_in_scope("https://api.example.com/users") is True
    assert guard.is_in_scope("http://localhost:8000/v1/auth") is True
    assert guard.is_in_scope("https://api.example.com/") is True
    
    # Out of bounds
    assert guard.is_in_scope("https://evil.com/users") is False
    assert guard.is_in_scope("http://localhost:8000/v2/auth") is False

def test_scope_guard_add_pattern() -> None:
    """Test dynamically adding a scope pattern."""
    guard = ScopeGuard()
    assert guard.is_in_scope("https://target.com/api") is False
    
    guard.add_scope("https://target.com/*")
    assert guard.is_in_scope("https://target.com/api") is True

def test_scope_guard_invalid_urls() -> None:
    """Test that malformed URLs are safely rejected."""
    guard = ScopeGuard(("*",)) # Even with wildcard, malformed should drop
    
    assert guard.is_in_scope("not_a_url") is False
    assert guard.is_in_scope("") is False
    assert guard.is_in_scope(":///broken") is False
