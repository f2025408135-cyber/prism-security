"""Tests for the OpenAPI 3.x parser."""

import os
import pytest
from prism.ingestion.openapi import parse_openapi_spec
from prism.exceptions import IngestionError

SPEC_PATH = os.path.join(os.path.dirname(__file__), "../../fixtures/specs/openapi_3.json")

def test_parse_openapi_valid_spec() -> None:
    """Test parsing a valid OpenAPI 3.0 specification."""
    endpoints = parse_openapi_spec(SPEC_PATH, "https://api.example.com")
    
    assert len(endpoints) == 3
    
    methods = [e.method for e in endpoints]
    assert "GET" in methods
    assert "POST" in methods
    
    # Check the GET /users endpoint
    users_get = next(e for e in endpoints if e.url == "https://api.example.com/users" and e.method == "GET")
    assert len(users_get.parameters) == 1
    assert users_get.parameters[0].name == "limit"
    assert users_get.parameters[0].location == "query"

    # Check the GET /users/{id} endpoint with path-level parameter
    user_get = next(e for e in endpoints if e.url == "https://api.example.com/users/{id}" and e.method == "GET")
    assert len(user_get.parameters) == 1
    assert user_get.parameters[0].name == "id"
    assert user_get.parameters[0].location == "path"

def test_parse_openapi_invalid_file() -> None:
    """Test parsing an invalid or missing file raises IngestionError."""
    with pytest.raises(IngestionError):
        parse_openapi_spec("nonexistent.json", "https://api.example.com")
