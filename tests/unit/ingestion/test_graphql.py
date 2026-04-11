"""Tests for the GraphQL parser."""

import pytest
import respx
import httpx
from prism.ingestion.graphql import parse_graphql_introspection
from prism.exceptions import IngestionError

MOCK_INTROSPECTION_RESPONSE = {
    "data": {
        "__schema": {
            "queryType": {"name": "Query"},
            "mutationType": {"name": "Mutation"},
            "types": [
                {
                    "name": "Query",
                    "fields": [
                        {
                            "name": "getUser",
                            "args": [{"name": "id"}]
                        }
                    ]
                },
                {
                    "name": "Mutation",
                    "fields": [
                        {
                            "name": "createUser",
                            "args": [{"name": "input"}]
                        }
                    ]
                }
            ]
        }
    }
}

@pytest.mark.asyncio
@respx.mock
async def test_parse_graphql_introspection_success() -> None:
    """Test successful parsing of GraphQL introspection."""
    url = "https://api.example.com/graphql"
    respx.post(url).mock(return_value=httpx.Response(200, json=MOCK_INTROSPECTION_RESPONSE))
    
    endpoints = await parse_graphql_introspection(url)
    
    assert len(endpoints) == 2
    for ep in endpoints:
        assert ep.method == "POST"
        assert ep.url == url
        
    get_user = next(e for e in endpoints if e.parameters[0].value == "getUser")
    assert get_user.parameters[1].value == "query"
    assert get_user.parameters[2].name == "id"
    assert get_user.parameters[2].location == "graphql_var"
    
    create_user = next(e for e in endpoints if e.parameters[0].value == "createUser")
    assert create_user.parameters[1].value == "mutation"
    assert create_user.parameters[2].name == "input"

@pytest.mark.asyncio
@respx.mock
async def test_parse_graphql_introspection_disabled() -> None:
    """Test handling when introspection is disabled/fails."""
    url = "https://api.example.com/graphql"
    respx.post(url).mock(return_value=httpx.Response(400, json={"errors": ["Introspection disabled"]}))
    
    with pytest.raises(IngestionError, match="Failed to fetch GraphQL"):
        await parse_graphql_introspection(url)
