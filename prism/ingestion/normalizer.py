"""Endpoint deduplication and normalization engine."""

import structlog
from urllib.parse import urlparse

from prism.models.endpoint import Endpoint

logger = structlog.get_logger(__name__)


def normalize_and_deduplicate(endpoints: tuple[Endpoint, ...]) -> tuple[Endpoint, ...]:
    """Normalize URLs and deduplicate a collection of endpoints.

    Resolves minor path variations (e.g., trailing slashes) and deduplicates
    based on the exact method and normalized URL. Note that it does not currently
    merge differing parameter sets, it prioritizes the first seen.

    Args:
        endpoints: A tuple of potentially raw/duplicate endpoints.

    Returns:
        A tuple of unique, normalized Endpoint models.
    """
    logger.info("normalization_started", count=len(endpoints))
    
    unique_map: dict[str, Endpoint] = {}

    for ep in endpoints:
        parsed = urlparse(ep.url)
        
        # Normalize path: remove duplicate slashes, strip trailing slash unless root
        path = parsed.path
        while "//" in path:
            path = path.replace("//", "/")
            
        if len(path) > 1 and path.endswith("/"):
            path = path.rstrip("/")
            
        normalized_url = f"{parsed.scheme}://{parsed.netloc}{path}"
        if parsed.query:
            normalized_url += f"?{parsed.query}"

        signature = f"{ep.method}:{normalized_url}"

        if signature not in unique_map:
            # Rebuild endpoint with normalized URL
            normalized_ep = Endpoint(
                method=ep.method,
                url=normalized_url,
                parameters=ep.parameters
            )
            unique_map[signature] = normalized_ep

    result = tuple(unique_map.values())
    logger.info("normalization_completed", original_count=len(endpoints), final_count=len(result))
    return result
