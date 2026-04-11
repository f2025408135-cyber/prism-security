"""Authorization Topology Mapper interfaces."""

from typing import Protocol, Any

from prism.models.endpoint import Endpoint
from prism.models.principal import Principal
from prism.models.authz import AuthzDecision

# Temporary type alias until models are fully built out in later chunks
EndpointAuthzProfile = tuple[AuthzDecision, ...]
AuthzTopologyGraph = Any # Replace with nx.DiGraph later
AuthzInconsistency = Any # Replace with model later

class IAuthzMapper(Protocol):
    """Maps authorization topology across endpoints and principals."""

    async def map_endpoint(
        self,
        endpoint: Endpoint,
        principals: tuple[Principal, ...],
    ) -> EndpointAuthzProfile:
        """Probe endpoint with all principals. Return full profile."""
        ...

    def build_topology_graph(
        self,
        profiles: tuple[EndpointAuthzProfile, ...],
    ) -> AuthzTopologyGraph:
        """Build NetworkX directed graph from profiles."""
        ...

    def find_inconsistencies(
        self,
        graph: AuthzTopologyGraph,
    ) -> tuple[AuthzInconsistency, ...]:
        """Find authorization inconsistencies in the graph."""
        ...
