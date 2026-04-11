"""Integration test simulating VAmPI (Vulnerable API) targets."""

import pytest
import respx
import httpx
from pathlib import Path

from prism.models.principal import Principal
from prism.models.endpoint import Endpoint, Parameter
from prism.http.client import AsyncHttpClient
from prism.http.scope import ScopeGuard
from prism.http.rate_limiter import RateLimiter
from prism.http.storage import TrafficStorage
from prism.http.executor import HTTPExecutor
from prism.mapper.prober import EndpointProber
from prism.mapper.matrix import MatrixBuilder
from prism.mapper.identifier import IdentifierExtractor
from prism.mapper.graph import GraphBuilder
from prism.mapper.inconsistency import InconsistencyDetector
from prism.mapper.classifier import InconsistencyClassifier
from prism.race.scorer import RaceProbabilityScorer

@pytest.mark.asyncio
@respx.mock
async def test_vampi_bola_and_bfla(tmp_path: Path) -> None:
    """Test detecting VAmPI's BOLA vulnerabilities on User profiles.
    
    In VAmPI:
    - User 1 is created and gets ID 'u1_id'
    - User 2 is created and gets ID 'u2_id'
    - User 1 can GET /users/u2_id (BOLA - Read)
    - User 1 can PUT /users/u2_id/email (BOLA - Update)
    """
    target = "http://vampi.local"
    
    # 1. Mocking VAmPI's API
    # Both users exist
    users_db = {
        "u1_id": {"username": "user1", "email": "user1@test.com"},
        "u2_id": {"username": "user2", "email": "user2@test.com"}
    }

    # GET /users/{user_id} - Vulnerable to BOLA (anyone with a token can read any user)
    def mock_get_user(request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return httpx.Response(401, json={"message": "Unauthorized"})
            
        # The user ID is the last part of the path
        user_id = request.url.path.split("/")[-1]
        
        if user_id in users_db:
            return httpx.Response(200, json={"username": users_db[user_id]["username"], "email": users_db[user_id]["email"]})
        return httpx.Response(404, json={"message": "Not found"})

    # PUT /users/{user_id}/email - Vulnerable to destructive BOLA
    def mock_put_email(request: httpx.Request) -> httpx.Response:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return httpx.Response(401, json={"message": "Unauthorized"})
            
        # Path is /users/{user_id}/email
        user_id = request.url.path.split("/")[-2]
        
        if user_id in users_db:
            return httpx.Response(200, json={"message": "Email updated successfully"})
        return httpx.Response(404, json={"message": "Not found"})

    respx.get(f"{target}/users/u1_id").mock(side_effect=mock_get_user)
    respx.get(f"{target}/users/u2_id").mock(side_effect=mock_get_user)
    respx.put(f"{target}/users/u2_id/email").mock(side_effect=mock_put_email)

    # 2. Ingestion (Simulating extracting endpoints from VAmPI's OpenAPI spec)
    endpoints = (
        Endpoint(method="GET", url=f"{target}/users/u1_id"),
        Endpoint(method="GET", url=f"{target}/users/u2_id"),
        Endpoint(method="PUT", url=f"{target}/users/u2_id/email", parameters=(
            Parameter(name="email", value="hacked@test.com", location="body"),
        ))
    )
    
    # 3. Principals
    p_u1 = Principal(name="User 1", id="p_u1")
    p_u2 = Principal(name="User 2", id="p_u2")

    # 4. Engine Setup
    client = AsyncHttpClient(ScopeGuard((f"{target}/*",)), RateLimiter(100.0))
    storage = TrafficStorage(str(tmp_path))
    executor = HTTPExecutor(client, storage)

    prober = EndpointProber(executor)
    mb = MatrixBuilder()

    # Inject proper authentication tokens based on the Principal
    import prism.http.request_builder as rb
    original_build = rb.build_request
    def mocked_build_request(endpoint, principal):
        req = original_build(endpoint, principal)
        req["headers"]["Authorization"] = f"Bearer {principal.id}_token"
        return req
    rb.build_request = mocked_build_request

    try:
        # Run the Authz Mapper concurrently
        for ep in endpoints:
            profile = await prober.map_endpoint(ep, (p_u1, p_u2))
            mb.add_profile(profile)
    finally:
        rb.build_request = original_build

    matrix = mb.build_matrix()
    
    # 5. Graph Building
    # In VAmPI, the user IDs are known (u1_id, u2_id). We manually simulate that 
    # the creation endpoints (POST /users) returned these IDs, which are then 
    # consumed by the GET and PUT endpoints.
    extractor = IdentifierExtractor()
    
    # We populate the graph manually to represent the topology discovery
    from prism.mapper.graph import GraphBuilder
    import networkx as nx
    
    graph = nx.DiGraph()
    # Source nodes (Creation)
    graph.add_node(f"POST {target}/users", method="POST", url=f"{target}/users")
    
    # Target nodes (Consumption)
    graph.add_node(f"GET {target}/users/u2_id", method="GET", url=f"{target}/users/u2_id")
    graph.add_node(f"PUT {target}/users/u2_id/email", method="PUT", url=f"{target}/users/u2_id/email")
    
    # Edges (Data flow of ID 'u2_id')
    graph.add_edge(f"POST {target}/users", f"GET {target}/users/u2_id", identifier="u2_id")
    graph.add_edge(f"POST {target}/users", f"PUT {target}/users/u2_id/email", identifier="u2_id")

    # We also need to inject the mock POST decisions into the matrix so the InconsistencyDetector
    # knows that User 1 did NOT create User 2.
    from prism.models.authz import AuthzDecision, AuthzMatrix
    
    d_post_u2_by_u2 = AuthzDecision(endpoint_url=f"{target}/users", endpoint_method="POST", principal_id="p_u2", http_status=201, is_authorized=True, timing_ms=10)
    d_post_u2_by_u1 = AuthzDecision(endpoint_url=f"{target}/users", endpoint_method="POST", principal_id="p_u1", http_status=403, is_authorized=False, timing_ms=10)
    
    matrix = AuthzMatrix(decisions=matrix.decisions + (d_post_u2_by_u2, d_post_u2_by_u1))
    
    # 6. Inconsistency Detection & Classification
    inconsistencies = InconsistencyDetector().find_inconsistencies(graph, matrix)
    
    # User 1 should have 2 inconsistencies against User 2's data (one GET, one PUT)
    assert len(inconsistencies) >= 2
    
    classified = InconsistencyClassifier().classify(inconsistencies)
    
    # Verify the GET BOLA
    get_bola = next(c for c in classified if "GET" in c.inconsistency.accessible_endpoint)
    assert get_bola.vuln_class == "BOLA_CANDIDATE"
    assert get_bola.confidence == 0.8  # Standard BOLA
    
    # Verify the PUT BOLA (Destructive)
    put_bola = next(c for c in classified if "PUT" in c.inconsistency.accessible_endpoint)
    assert put_bola.vuln_class == "BOLA_CANDIDATE"
    assert put_bola.confidence == 0.95 # Destructive BOLA gets higher confidence score

    await client.close()
