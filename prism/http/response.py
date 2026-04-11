"""HTTP response parsing and classification."""

import httpx
import structlog
from typing import Any

from prism.models.endpoint import Response

logger = structlog.get_logger(__name__)

# How much of the body to keep for context/evidence
MAX_BODY_EXCERPT_LENGTH = 10000


def parse_response(httpx_response: httpx.Response, timing_ms: float) -> Response:
    """Convert an httpx Response into a frozen PRISM Response model.

    Args:
        httpx_response: The raw httpx response object.
        timing_ms: The duration of the request in milliseconds.

    Returns:
        A frozen Response model.
    """
    logger.debug("parse_response_started", status_code=httpx_response.status_code)

    headers_tuple: tuple[tuple[str, str], ...] = tuple(
        (k, v) for k, v in httpx_response.headers.items()
    )

    try:
        # Attempt to decode as text
        body_text = httpx_response.text
        if len(body_text) > MAX_BODY_EXCERPT_LENGTH:
            body_text = body_text[:MAX_BODY_EXCERPT_LENGTH] + "\n...[truncated]..."
    except UnicodeDecodeError:
        # If it's binary data (e.g. image, PDF), we don't store the raw bytes in excerpt
        content_type = httpx_response.headers.get("content-type", "application/octet-stream")
        body_text = f"[Binary data: {content_type}]"

    response = Response(
        status_code=httpx_response.status_code,
        headers=headers_tuple,
        body_excerpt=body_text,
        timing_ms=timing_ms
    )

    logger.debug(
        "parse_response_completed", 
        status=response.status_code, 
        excerpt_length=len(response.body_excerpt)
    )
    return response
