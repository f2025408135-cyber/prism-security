"""NetworkX PrimitiveGraph implementation."""

import structlog
import networkx as nx # type: ignore

from prism.synthesis.primitive import PrimitiveFact

logger = structlog.get_logger(__name__)


class PrimitiveGraphManager:
    """Manages the directed graph of confirmed security facts.

    Nodes represent states or resources. Edges represent PrimitiveFacts
    (actions that transition state or bypass authorization).
    """

    def __init__(self) -> None:
        """Initialize the empty primitive graph."""
        self.graph = nx.DiGraph()

    def add_primitive(self, fact: PrimitiveFact) -> None:
        """Add a primitive fact to the knowledge graph.

        Args:
            fact: The PrimitiveFact to add.
        """
        # We model the graph where nodes are preconditions/postconditions
        # and edges are the actions (the facts themselves) that bridge them.
        
        # For Z3 synthesis later, we need to know how to connect them.
        # So Node A is the precondition state, Node B is the postcondition state.
        
        pre_node = f"{fact.target_resource}:{fact.precondition}"
        post_node = f"{fact.target_resource}:{fact.postcondition}"

        self.graph.add_edge(
            pre_node, 
            post_node, 
            fact_id=fact.id,
            fact_type=fact.fact_type,
            actor=fact.actor,
            evidence=fact.evidence_id
        )
        logger.debug("primitive_added_to_graph", fact_id=fact.id, edge=f"{pre_node}->{post_node}")

    def get_facts_by_type(self, fact_type: str) -> list[PrimitiveFact]:
        """Retrieve all facts of a specific type.

        Args:
            fact_type: The type string (e.g., 'authz_bypass').

        Returns:
            A list of matching PrimitiveFact representations extracted from edges.
        """
        facts = []
        for u, v, data in self.graph.edges(data=True):
            if data.get("fact_type") == fact_type:
                # Reconstruct fact from edge data (simplification for retrieval)
                # In a real database backed model, we'd query the DB using the fact_id.
                facts.append(
                    PrimitiveFact(
                        id=data["fact_id"],
                        fact_type=data["fact_type"],
                        actor=data["actor"],
                        target_resource=u.split(":", 1)[0],
                        precondition=u.split(":", 1)[1],
                        postcondition=v.split(":", 1)[1],
                        evidence_id=data["evidence"]
                    )
                )
        return facts

    def get_all_paths(self, start_node: str, end_node: str) -> list[list[str]]:
        """Find all possible chains of primitives from start to end condition.

        Args:
            start_node: The starting condition node.
            end_node: The target condition node.

        Returns:
            A list of paths, where each path is a list of node strings.
        """
        if start_node not in self.graph or end_node not in self.graph:
            return []
            
        try:
            paths = list(nx.all_simple_paths(self.graph, start_node, end_node))
            return paths
        except nx.NetworkXNoPath:
            return []
