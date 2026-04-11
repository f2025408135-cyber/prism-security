"""JS bundle endpoint extraction using regex patterns."""

import re
import structlog
import httpx

from prism.models.endpoint import Endpoint
from prism.exceptions import IngestionError
from prism.constants import DEFAULT_TIMEOUT_SECONDS

logger = structlog.get_logger(__name__)

# Common regex patterns to find API endpoints in JS bundles
# Matches absolute paths starting with /api/ or /v1/, etc.
ENDPOINT_REGEX = re.compile(r'["\'](?:/api/|/v[1-9]/|/rest/)([^"\']+)["\']')


async def extract_endpoints_from_js(js_url: str, target_url: str) -> tuple[Endpoint, ...]:
    """Fetch a JavaScript bundle and extract potential API endpoints via regex.

    Args:
        js_url: The URL of the JavaScript file to parse.
        target_url: The base target URL to prepend to extracted paths.

    Returns:
        A tuple of extracted, frozen Endpoint models.

    Raises:
        IngestionError: If the JS bundle cannot be fetched.
    """
    logger.info("js_extraction_started", js_url=js_url)

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            response = await client.get(js_url)
            response.raise_for_status()
            js_content = response.text
    except Exception as e:
        logger.error("js_fetch_failed", js_url=js_url, error=str(e))
        raise IngestionError(f"Failed to fetch JS bundle {js_url}: {e}") from e

    matches = ENDPOINT_REGEX.findall(js_content)
    
    endpoints: set[Endpoint] = set()
    base = target_url.rstrip("/")

    for match in matches:
        # Reconstruct the matched path (regex captured the part after the prefix)
        # We need to find the full original string or just heuristically guess.
        # Actually, let's just use a simpler regex for extraction to get the full path:
        pass

    # Let's use a better regex that captures the whole path
    full_path_regex = re.compile(r'["\'](/api/[^"\']+|/v[1-9]/[^"\']+|/rest/[^"\']+)["\']')
    full_matches = full_path_regex.findall(js_content)

    for match in full_matches:
        full_url = f"{base}{match}"
        # We assume GET for extracted endpoints as a safe default for probing
        endpoints.add(Endpoint(method="GET", url=full_url))

    logger.info("js_extraction_completed", js_url=js_url, endpoint_count=len(endpoints))
    return tuple(endpoints)
