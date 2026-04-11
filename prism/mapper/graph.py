"""Authorization topology graph construction."""

import structlog
import networkx as nx # type: ignore

from prism.models.authz import AuthzMatrix, AuthzDecision
from prism.mapper.identifier import IdentifierExtractor

logger = structlog.get_logger(__name__)

# Re-declare type for local implementation
AuthzTopologyGraph = nx.DiGraph


class GraphBuilder:
    """Builds a directed graph of authorization relationships.

    Nodes: Endpoints (e.g., 'GET /users')
    Edges: Object Flow (Endpoint A returns an ID that Endpoint B uses)
    """

    def __init__(self, extractor: IdentifierExtractor) -> None:
        """Initialize the graph builder.

        Args:
            extractor: The identifier extractor to map data flows.
        """
        self.extractor = extractor

    def build_topology_graph(self, matrix: AuthzMatrix, response_bodies: dict[str, str]) -> AuthzTopologyGraph:
        """Build the NetworkX directed graph from the AuthzMatrix.

        Args:
            matrix: The aggregated AuthzMatrix.
            response_bodies: A dictionary mapping `decision.endpoint_url` to its raw body.
                             (Required since AuthzDecision intentionally omits the full body payload)

        Returns:
            A constructed nx.DiGraph instance.
        """
        logger.info("build_topology_graph_started", decisions=len(matrix.decisions))

        graph = nx.DiGraph()

        # Step 1: Add nodes (Endpoints)
        # We group decisions by unique Endpoint (Method + URL)
        endpoint_signatures = set()
        for decision in matrix.decisions:
            sig = f"{decision.endpoint_method} {decision.endpoint_url}"
            if sig not in endpoint_signatures:
                graph.add_node(sig, method=decision.endpoint_method, url=decision.endpoint_url)
                endpoint_signatures.add(sig)

        # Step 2: Extract identifiers produced by each endpoint
        # Map of identifier string -> list of source endpoint signatures
        produced_ids: dict[str, set[str]] = {}

        for decision in matrix.decisions:
            if not decision.is_authorized:
                continue

            body = response_bodies.get(decision.endpoint_url, "")
            if not body:
                continue

            sig = f"{decision.endpoint_method} {decision.endpoint_url}"
            identifiers = self.extractor.extract(decision, body)

            for ident in identifiers:
                if ident not in produced_ids:
                    produced_ids[ident] = set()
                produced_ids[ident].add(sig)

        # Step 3: Create edges based on ID flow
        # If Endpoint A produced ID '123' and Endpoint B's URL contains '123', B depends on A
        for ident, sources in produced_ids.items():
            for target_sig in endpoint_signatures:
                # Simple heuristic: if the ID is part of the target URL, there is a data flow
                # We append a slash to ensure we match exact path segments, or end of string
                target_url = target_sig.split(" ", 1)[1]
                parts = target_url.split("/")
                if ident in parts or f"?id={ident}" in target_url or f"={ident}" in target_url:
                    for source_sig in sources:
                        if source_sig != target_sig:
                            graph.add_edge(source_sig, target_sig, identifier=ident)
                elif ident in target_sig: # Fallback
                     for source_sig in sources:
                        if source_sig != target_sig:
                            graph.add_edge(source_sig, target_sig, identifier=ident)

        logger.info(
            "build_topology_graph_completed", 
            nodes=graph.number_of_nodes(), 
            edges=graph.number_of_edges()
        )
        return graph
