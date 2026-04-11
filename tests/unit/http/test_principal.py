"""Tests for Principal Manager."""

import pytest
from prism.http.principal import PrincipalManager
from prism.exceptions import ConfigurationError

def test_principal_manager_anonymous_init() -> None:
    """Test that the manager always initializes an anonymous principal."""
    manager = PrincipalManager()
    
    principals = manager.get_all_principals()
    assert len(principals) == 1
    assert principals[0].name == "anonymous"
    assert manager.get_token(principals[0].id) is None

def test_principal_manager_registration() -> None:
    """Test registering a new principal with roles."""
    manager = PrincipalManager()
    
    admin = manager.register_principal(name="admin_user", roles=("admin", "root"))
    
    assert admin.name == "admin_user"
    assert "admin" in admin.roles
    assert len(manager.get_all_principals()) == 2

def test_principal_manager_add_token() -> None:
    """Test associating a token with a registered principal securely."""
    manager = PrincipalManager()
    user = manager.register_principal("user", ("viewer",))
    
    token = manager.add_token(user.id, "my_super_secret_jwt", "Bearer")
    
    assert token.value == "my_super_secret_jwt"
    assert token.token_type == "Bearer"
    
    retrieved = manager.get_token(user.id)
    assert retrieved is not None
    assert retrieved.value == "my_super_secret_jwt"

def test_principal_manager_add_token_unregistered() -> None:
    """Test adding a token to an unregistered ID raises ConfigurationError."""
    manager = PrincipalManager()
    
    with pytest.raises(ConfigurationError, match="not found"):
        manager.add_token("fake_id", "token123")
