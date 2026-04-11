"""HTML + Pyvis Interactive Graph Report."""

import structlog
import networkx as nx
from pathlib import Path
from pyvis.network import Network # type: ignore

from prism.models.finding import Finding
from prism.models.authz import AuthzMatrix

logger = structlog.get_logger(__name__)


class HtmlReporter:
    """Generates an interactive HTML dashboard using Pyvis and networkx."""

    def generate(self, findings: tuple[Finding, ...], graph: nx.DiGraph, output_path: str) -> str:
        """Create the HTML graph report.

        Args:
            findings: The tuple of confirmed findings.
            graph: The NetworkX directed graph representing the topology.
            output_path: Where to save the HTML file.

        Returns:
            The path to the generated HTML file.
        """
        logger.info("html_report_generated", path=output_path)

        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white", directed=True)
        net.barnes_hut()

        # Add Nodes representing endpoints
        for node, data in graph.nodes(data=True):
            method = data.get("method", "UNK")
            url = data.get("url", node)
            color = "#00ff00" if method == "GET" else "#ff9900"
            net.add_node(node, label=f"{method} {url}", title=f"Endpoint: {node}", color=color)

        # Add Edges representing object flow IDs
        for u, v, data in graph.edges(data=True):
            ident = data.get("identifier", "")
            net.add_edge(u, v, title=f"Flow: ID={ident}", color="#ffffff")

        # In a full implementation, we'd embed the findings into an HTML panel
        # beside the Pyvis graph. For now, Pyvis generates the core output.
        path = Path(output_path)
        net.write_html(str(path))

        return str(path)
