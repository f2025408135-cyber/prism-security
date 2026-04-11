"""Tests for the Postman parser."""

import os
import pytest
from prism.ingestion.postman import parse_postman_collection
from prism.exceptions import IngestionError

SPEC_PATH = os.path.join(os.path.dirname(__file__), "../../fixtures/specs/postman.json")

def test_parse_postman_valid_collection() -> None:
    """Test parsing a valid Postman collection."""
    endpoints = parse_postman_collection(SPEC_PATH)
    
    assert len(endpoints) == 2
    
    get_users = next(e for e in endpoints if e.method == "GET")
    assert get_users.url == "https://api.example.com/users?role=admin"
    assert len(get_users.parameters) == 2
    
    # Check headers and queries were both extracted
    param_names = [p.name for p in get_users.parameters]
    assert "role" in param_names
    assert "Authorization" in param_names
    
    # Check nested folder request
    put_user = next(e for e in endpoints if e.method == "PUT")
    assert put_user.url == "https://api.example.com/users/1"
    assert len(put_user.parameters) == 0

def test_parse_postman_invalid_file() -> None:
    """Test parsing an invalid or missing file raises IngestionError."""
    with pytest.raises(IngestionError):
        parse_postman_collection("nonexistent.json")
