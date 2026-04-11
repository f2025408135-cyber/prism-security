"""End-to-End full scan integration testing."""

import pytest
import respx
import httpx
import networkx as nx
from pathlib import Path

# Components
from prism.models.principal import Principal
from prism.ingestion.openapi import parse_openapi_spec
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
from prism.reporting.terminal import TerminalReporter

@pytest.mark.asyncio
@respx.mock
async def test_full_scan_pipeline(tmp_path: Path) -> None:
    """Simulate a complete PRISM run from ingestion to reporting."""
    target_url = "https://api.vulnerable.com"
    
    # 1. Setup Mock API Network
    # An API where anyone can GET /admin/users, but only admins can POST /admin/users
    respx.post(f"{target_url}/admin/users").mock(side_effect=lambda request: 
        httpx.Response(201, json={"id": "555"}) if "admin_token" in request.headers.get("Authorization", "") 
        else httpx.Response(403, json={"error": "forbidden"})
    )
    respx.get(f"{target_url}/admin/users/555").mock(side_effect=lambda request:
        httpx.Response(200, json={"id": "555", "data": "secret"}) 
        # BOLA vulnerability: the GET endpoint doesn't check the token role properly!
    )

    # 2. Ingestion (Mocking an OpenAPI spec load)
    # We will simulate the output of the ingestor directly for the integration
    from prism.models.endpoint import Endpoint
    endpoints = (
        Endpoint(method="POST", url=f"{target_url}/admin/users"),
        Endpoint(method="GET", url=f"{target_url}/admin/users/555")
    )

    # 3. Principals
    p_admin = Principal(name="Admin", id="p_admin")
    p_user = Principal(name="Hacker", id="p_user")
    
    # 4. HTTP Engine Setup
    scope = ScopeGuard((f"{target_url}/*",))
    limiter = RateLimiter(max_rps=100.0)
    client = AsyncHttpClient(scope, limiter)
    storage = TrafficStorage(str(tmp_path))
    executor = HTTPExecutor(client, storage)

    # 5. Mapping Engine
    prober = EndpointProber(executor)
    matrix_builder = MatrixBuilder()

    # Map each endpoint against both principals
    for ep in endpoints:
        # Hack the request builder to use the specific tokens we mapped in respx
        # We temporarily patch build_request for this integration test
        import prism.http.request_builder as rb
        original_build = rb.build_request
        def mocked_build_request(endpoint, principal):
            req = original_build(endpoint, principal)
            if principal.name == "Admin":
                req["headers"]["Authorization"] = "Bearer admin_token"
            else:
                req["headers"]["Authorization"] = "Bearer user_token"
            return req
        
        rb.build_request = mocked_build_request
        try:
            profile = await prober.map_endpoint(ep, (p_admin, p_user))
            matrix_builder.add_profile(profile)
        finally:
            rb.build_request = original_build

    matrix = matrix_builder.build_matrix()
    
    # Verify Matrix state
    assert len(matrix.decisions) == 4

    # 6. Graph Building
    extractor = IdentifierExtractor()
    graph_builder = GraphBuilder(extractor)
    
    # We need the response bodies for graph building (from storage)
    records = storage.load_all()
    response_bodies = {}
    for r in records:
        url = r.get("request", {}).get("url")
        body = r.get("response", {}).get("body_excerpt")
        # Ensure we record the response for the POST endpoint too if it has an ID
        if r.get("request", {}).get("method") == "POST":
            response_bodies[url] = '{"id": "555"}'
        else:
            response_bodies[url] = body

    graph = graph_builder.build_topology_graph(matrix, response_bodies)
    
    # 7. Inconsistency Detection
    detector = InconsistencyDetector()
    inconsistencies = detector.find_inconsistencies(graph, matrix)
    
    # The BOLA should be caught: Hacker could not POST (403) but could GET (200) ID 555
    assert len(inconsistencies) > 0
    bola_finding = next(i for i in inconsistencies if i.principal_id == "p_user")
    
    # 8. Classification
    classifier = InconsistencyClassifier()
    classified = classifier.classify((bola_finding,))
    
    assert classified[0].vuln_class == "BOLA_CANDIDATE"

    # 9. Cleanup
    await client.close()
