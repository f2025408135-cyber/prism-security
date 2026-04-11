"""HTTP Archive (HAR) format parser."""

import json
from urllib.parse import urlparse, parse_qsl

import structlog

from prism.models.endpoint import Endpoint, Parameter
from prism.exceptions import IngestionError

logger = structlog.get_logger(__name__)


def parse_har_file(file_path: str) -> tuple[Endpoint, ...]:
    """Parse an HTTP Archive (HAR) file and extract endpoints.

    Args:
        file_path: The local path to the HAR JSON file.

    Returns:
        A tuple of extracted, frozen Endpoint models.

    Raises:
        IngestionError: If the file cannot be parsed or is invalid HAR format.
    """
    logger.info("parse_har_started", file_path=file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            har_data = json.load(f)
    except Exception as e:
        logger.error("har_load_failed", file_path=file_path, error=str(e))
        raise IngestionError(f"Failed to load HAR file: {e}") from e

    log_obj = har_data.get("log")
    if not log_obj or "entries" not in log_obj:
        raise IngestionError("Invalid HAR format: missing 'log.entries'.")

    endpoints: list[Endpoint] = []
    entries = log_obj.get("entries", [])
    
    seen_endpoints = set()

    for entry in entries:
        req = entry.get("request", {})
        method = req.get("method", "GET").upper()
        url = req.get("url", "")
        
        if not url:
            continue
            
        if method not in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
            continue

        # Strip query string from URL to create unique signature
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        signature = f"{method}:{base_url}"
        
        if signature in seen_endpoints:
            continue
            
        seen_endpoints.add(signature)

        extracted_params: list[Parameter] = []
        
        # HAR query params
        query_string = req.get("queryString", [])
        for qs in query_string:
            param = Parameter(
                name=qs.get("name", "unknown"),
                value=qs.get("value", ""),
                location="query"
            )
            extracted_params.append(param)
            
        # HAR headers
        headers = req.get("headers", [])
        for header in headers:
            # Skip standard headers to avoid bloat
            if header.get("name", "").lower() in ["accept", "user-agent", "host", "connection"]:
                continue
                
            param = Parameter(
                name=header.get("name", "unknown"),
                value=header.get("value", ""),
                location="header"
            )
            extracted_params.append(param)

        endpoint = Endpoint(
            method=method,
            url=url,
            parameters=tuple(extracted_params)
        )
        endpoints.append(endpoint)

    logger.info("parse_har_completed", file_path=file_path, endpoint_count=len(endpoints))
    return tuple(endpoints)
