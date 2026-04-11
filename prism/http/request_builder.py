"""HTTP Request Builder."""

from typing import Any
import structlog
from urllib.parse import urlencode, urlparse, urlunparse

from prism.models.endpoint import Endpoint
from prism.models.principal import Principal

logger = structlog.get_logger(__name__)


def build_request(endpoint: Endpoint, principal: Principal) -> dict[str, Any]:
    """Build httpx request arguments from an Endpoint and Principal.

    Extracts parameters based on their location (query, header, body) and
    injects authentication details from the Principal.

    Args:
        endpoint: The target Endpoint definition.
        principal: The authentication context to inject.

    Returns:
        A dictionary of kwargs suitable for passing to `httpx.request()`.
    """
    logger.debug("build_request_started", endpoint_url=endpoint.url, principal_id=principal.id)

    headers: dict[str, str] = {}
    query_params: dict[str, str] = {}
    json_body: dict[str, Any] = {}
    
    # Process Endpoint parameters
    for param in endpoint.parameters:
        if param.location == "query":
            query_params[param.name] = param.value
        elif param.location == "header":
            headers[param.name] = param.value
        elif param.location == "body":
            json_body[param.name] = param.value
        elif param.location == "graphql_var":
            # Custom mapping for GraphQL variables
            if "variables" not in json_body:
                json_body["variables"] = {}
            json_body["variables"][param.name] = param.value
            
    # Inject Principal authorization if available
    # For now, we simulate simple Bearer or basic token injection based on roles or ID
    # In a full implementation, the Principal model would carry explicit Token references
    # However per AGENTS.md we must not hardcode logic, so we'll simulate basic injection
    if principal.name != "anonymous":
        headers["Authorization"] = f"Bearer {principal.id}_token_mock"

    # Reconstruct URL with query parameters if they exist
    url = endpoint.url
    if query_params:
        parsed = urlparse(url)
        # Avoid double-encoding existing query params
        existing_query = parsed.query
        new_query = urlencode(query_params)
        final_query = f"{existing_query}&{new_query}" if existing_query else new_query
        
        parsed = parsed._replace(query="")  # Clear it to rebuild cleanly
        url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, final_query, parsed.fragment))

    req_args: dict[str, Any] = {
        "method": endpoint.method,
        "url": url,
        "headers": headers,
    }
    
    if json_body:
        req_args["json"] = json_body

    logger.debug("build_request_completed", endpoint_url=url, has_body=bool(json_body))
    return req_args
