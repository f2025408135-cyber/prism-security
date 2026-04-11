"""Tests for principal data models."""

import pytest
from prism.models.principal import Principal, Token, Credential

def test_principal_creation_generates_id() -> None:
    """Test that creating a Principal without an ID generates a unique one."""
    p1 = Principal(name="admin")
    p2 = Principal(name="user")
    
    assert p1.id is not None
    assert p2.id is not None
    assert p1.id != p2.id
    assert p1.name == "admin"
    assert p1.roles == frozenset()

def test_principal_is_frozen() -> None:
    """Test that the Principal model is immutable."""
    p = Principal(name="admin", roles=frozenset(["admin"]))
    
    with pytest.raises(Exception):
        p.name = "hacker"  # type: ignore

def test_token_creation() -> None:
    """Test creation of a Token model."""
    t = Token(principal_id="123", value="super_secret_token")
    
    assert t.principal_id == "123"
    assert t.value == "super_secret_token"
    assert t.token_type == "Bearer"

def test_credential_creation() -> None:
    """Test creation of a Credential model."""
    c = Credential(principal_id="456", username="alice", password="password123")
    
    assert c.principal_id == "456"
    assert c.username == "alice"
    assert c.password == "password123"
