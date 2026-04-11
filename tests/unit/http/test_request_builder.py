"""Tests for HTTP request builder."""

from prism.models.endpoint import Endpoint, Parameter
from prism.models.principal import Principal
from prism.http.request_builder import build_request

def test_build_request_with_parameters() -> None:
    """Test building a request with query, header, and body params."""
    ep = Endpoint(
        method="POST",
        url="https://api.example.com/data",
        parameters=(
            Parameter(name="q", value="search", location="query"),
            Parameter(name="X-Custom", value="header_val", location="header"),
            Parameter(name="item", value="body_val", location="body"),
            Parameter(name="var1", value="graphql_var", location="graphql_var")
        )
    )
    principal = Principal(id="user1", name="alice")
    
    req = build_request(ep, principal)
    
    assert req["method"] == "POST"
    assert "https://api.example.com/data?q=search" in req["url"]
    
    headers = req["headers"]
    assert headers["X-Custom"] == "header_val"
    assert "Bearer user1_token_mock" in headers.get("Authorization", "")
    
    json_body = req["json"]
    assert json_body["item"] == "body_val"
    assert json_body["variables"]["var1"] == "graphql_var"

def test_build_request_anonymous() -> None:
    """Test building a request without authorization injection."""
    ep = Endpoint(method="GET", url="https://api.example.com/public")
    principal = Principal(name="anonymous")
    
    req = build_request(ep, principal)
    assert req["method"] == "GET"
    assert "Authorization" not in req["headers"]
