"""Tests for the Swagger 2.0 parser."""

import os
import pytest
from prism.ingestion.swagger import parse_swagger_spec
from prism.exceptions import IngestionError

SPEC_PATH = os.path.join(os.path.dirname(__file__), "../../fixtures/specs/swagger_2.json")

def test_parse_swagger_valid_spec() -> None:
    """Test parsing a valid Swagger 2.0 specification."""
    endpoints = parse_swagger_spec(SPEC_PATH, "https://api.example.com")
    
    assert len(endpoints) == 1
    
    endpoint = endpoints[0]
    assert endpoint.method == "GET"
    # Base path should be prepended
    assert endpoint.url == "https://api.example.com/v1/items"
    
    assert len(endpoint.parameters) == 1
    assert endpoint.parameters[0].name == "q"
    assert endpoint.parameters[0].location == "query"

def test_parse_swagger_invalid_file() -> None:
    """Test parsing an invalid or missing file raises IngestionError."""
    with pytest.raises(IngestionError):
        parse_swagger_spec("nonexistent.json", "https://api.example.com")
