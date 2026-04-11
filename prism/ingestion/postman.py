"""Postman Collection specification parser."""

import json
from typing import Any
from urllib.parse import urlparse

import structlog

from prism.models.endpoint import Endpoint, Parameter
from prism.exceptions import IngestionError

logger = structlog.get_logger(__name__)


def _extract_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Recursively extract request items from folders."""
    requests = []
    for item in items:
        if "item" in item:
            # It's a folder
            requests.extend(_extract_items(item["item"]))
        elif "request" in item:
            # It's a request
            requests.append(item)
    return requests


def parse_postman_collection(file_path: str) -> tuple[Endpoint, ...]:
    """Parse a Postman Collection (v2.0/v2.1) and extract endpoints.

    Args:
        file_path: The local path to the Postman collection JSON file.

    Returns:
        A tuple of extracted, frozen Endpoint models.

    Raises:
        IngestionError: If the file cannot be parsed.
    """
    logger.info("parse_postman_started", file_path=file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            collection = json.load(f)
    except Exception as e:
        logger.error("postman_load_failed", file_path=file_path, error=str(e))
        raise IngestionError(f"Failed to load Postman collection: {e}") from e

    if "item" not in collection:
        raise IngestionError("Invalid Postman format: missing 'item' root.")

    endpoints: list[Endpoint] = []
    items = _extract_items(collection.get("item", []))

    for item in items:
        req = item.get("request", {})
        method = req.get("method", "GET").upper()
        
        if method not in ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]:
            continue

        url_data = req.get("url", {})
        raw_url = ""
        
        if isinstance(url_data, str):
            raw_url = url_data
        elif isinstance(url_data, dict):
            raw_url = url_data.get("raw", "")
            
        if not raw_url:
            continue

        extracted_params: list[Parameter] = []
        
        # Postman query params
        if isinstance(url_data, dict) and "query" in url_data:
            for query in url_data["query"]:
                param = Parameter(
                    name=query.get("key", "unknown"),
                    value=query.get("value", ""),
                    location="query"
                )
                extracted_params.append(param)
                
        # Postman headers
        headers = req.get("header", [])
        if isinstance(headers, list):
            for header in headers:
                param = Parameter(
                    name=header.get("key", "unknown"),
                    value=header.get("value", ""),
                    location="header"
                )
                extracted_params.append(param)

        endpoint = Endpoint(
            method=method,
            url=raw_url,
            parameters=tuple(extracted_params)
        )
        endpoints.append(endpoint)

    logger.info("parse_postman_completed", file_path=file_path, endpoint_count=len(endpoints))
    return tuple(endpoints)
