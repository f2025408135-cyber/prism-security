"""Tests for endpoint data models."""

import pytest
from prism.models.endpoint import Endpoint, Parameter, Response

def test_parameter_creation() -> None:
    """Test creation of a Parameter model."""
    param = Parameter(name="id", value="10", location="query")
    
    assert param.name == "id"
    assert param.value == "10"
    assert param.location == "query"

def test_endpoint_creation_with_parameters() -> None:
    """Test creation of an Endpoint model with parameters."""
    param = Parameter(name="q", value="search", location="query")
    endpoint = Endpoint(
        method="GET",
        url="https://api.example.com/search",
        parameters=(param,)
    )
    
    assert endpoint.method == "GET"
    assert endpoint.url == "https://api.example.com/search"
    assert len(endpoint.parameters) == 1
    assert endpoint.parameters[0].name == "q"

def test_endpoint_is_frozen() -> None:
    """Test that the Endpoint model is immutable."""
    endpoint = Endpoint(method="POST", url="https://api.example.com/data")
    
    with pytest.raises(Exception):
        endpoint.url = "http://hacked.com"  # type: ignore

def test_response_creation() -> None:
    """Test creation of a Response model."""
    response = Response(
        status_code=200,
        headers=(("Content-Type", "application/json"),),
        body_excerpt='{"status": "ok"}',
        timing_ms=45.2
    )
    
    assert response.status_code == 200
    assert len(response.headers) == 1
    assert response.headers[0][1] == "application/json"
    assert response.timing_ms == 45.2
