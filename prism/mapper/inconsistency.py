"""Authorization inconsistency detection algorithms."""

import structlog
from typing import Any
from pydantic import BaseModel, ConfigDict

from prism.models.authz import AuthzMatrix, AuthzDecision
from prism.mapper.graph import AuthzTopologyGraph

logger = structlog.get_logger(__name__)


class AuthzInconsistency(BaseModel):
    """Represents a discovered authorization inconsistency.

    Attributes:
        principal_id: The ID of the user experiencing the inconsistency.
        identifier: The specific object ID involved.
        accessible_endpoint: The endpoint signature where access was allowed.
        denied_endpoint: The endpoint signature where access was unexpectedly denied.
        reason: Description of the inconsistency logic.
    """
    model_config = ConfigDict(frozen=True)

    principal_id: str
    identifier: str
    accessible_endpoint: str
    denied_endpoint: str
    reason: str


class InconsistencyDetector:
    """Finds logic gaps where a principal can access an object via one path but not another."""

    def find_inconsistencies(self, graph: AuthzTopologyGraph, matrix: AuthzMatrix) -> tuple[AuthzInconsistency, ...]:
        """Detect inconsistent access patterns across the topology.

        Example: User 1 created object 555 (POST /users). User 1 can view object 555 (GET /users/555).
                 User 2 CANNOT create objects, but User 2 CAN view object 555 (GET /users/555).
                 This is a potential BOLA inconsistency.

        Args:
            graph: The NetworkX directed graph of object flows.
            matrix: The AuthzMatrix containing all decisions.

        Returns:
            A tuple of frozen AuthzInconsistency objects.
        """
        logger.info("inconsistency_detection_started", edges=graph.number_of_edges())
        
        inconsistencies: list[AuthzInconsistency] = []
        
        # Organize decisions by principal -> endpoint_signature -> decision
        by_principal: dict[str, dict[str, AuthzDecision]] = {}
        for d in matrix.decisions:
            sig = f"{d.endpoint_method} {d.endpoint_url}"
            if d.principal_id not in by_principal:
                by_principal[d.principal_id] = {}
            by_principal[d.principal_id][sig] = d

        # Analyze edges (source -> target via identifier)
        for source_sig, target_sig, edge_data in graph.edges(data=True):
            identifier = edge_data.get("identifier", "")
            if not identifier:
                continue

            for principal_id, endpoint_map in by_principal.items():
                source_decision = endpoint_map.get(source_sig)
                target_decision = endpoint_map.get(target_sig)

                if not source_decision or not target_decision:
                    continue

                # The core inconsistency heuristic:
                # If a principal is authorized to see the source that produced the ID,
                # but is inexplicably denied from the target that consumes it (or vice-versa
                # where they shouldn't see it but can).
                
                # Case 1: Inconsistent read/write
                # User has access to the collection/creation (source) but gets 403 on the item (target)
                if source_decision.is_authorized and not target_decision.is_authorized:
                    if target_decision.http_status in (401, 403):
                        inconsistencies.append(
                            AuthzInconsistency(
                                principal_id=principal_id,
                                identifier=identifier,
                                accessible_endpoint=source_sig,
                                denied_endpoint=target_sig,
                                reason="Authorized at source but forbidden at destination."
                            )
                        )

                # Case 2: Unearned Access (BOLA/IDOR pattern)
                # User DOES NOT have access to the source (e.g. didn't create it, can't list it)
                # But DOES have access to the specific target using the ID.
                elif not source_decision.is_authorized and target_decision.is_authorized:
                    if source_decision.http_status in (401, 403):
                        inconsistencies.append(
                            AuthzInconsistency(
                                principal_id=principal_id,
                                identifier=identifier,
                                accessible_endpoint=target_sig,
                                denied_endpoint=source_sig,
                                reason="Forbidden at source but authorized at destination (BOLA candidate)."
                            )
                        )

        # Deduplicate
        unique_inconsistencies = tuple(set(inconsistencies))
        logger.info("inconsistency_detection_completed", count=len(unique_inconsistencies))
        return unique_inconsistencies
