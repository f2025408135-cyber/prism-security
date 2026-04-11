"""Swagger 2.0 specification parser."""

from typing import Any
import structlog
from prance import ResolvingParser

from prism.models.endpoint import Endpoint, Parameter
from prism.exceptions import IngestionError

logger = structlog.get_logger(__name__)


def parse_swagger_spec(file_path: str, target_url: str) -> tuple[Endpoint, ...]:
    """Parse a Swagger 2.0 specification and extract endpoints.

    Args:
        file_path: The local path to the Swagger specification file (JSON or YAML).
        target_url: The base target URL to prepend to extracted paths.

    Returns:
        A tuple of extracted, frozen Endpoint models.

    Raises:
        IngestionError: If the file cannot be parsed.
    """
    logger.info("parse_swagger_started", file_path=file_path)

    try:
        # Prance supports Swagger 2.0 as well
        parser = ResolvingParser(file_path, strict=False)
        resolved_spec = parser.specification
        
        swagger_version = resolved_spec.get("swagger")
        if swagger_version != "2.0":
            logger.warning("swagger_version_mismatch", version=swagger_version)
            
    except Exception as e:
        logger.error("swagger_resolution_failed", file_path=file_path, error=str(e))
        raise IngestionError(f"Failed to parse Swagger spec: {e}") from e

    endpoints: list[Endpoint] = []
    paths: dict[str, Any] = resolved_spec.get("paths", {})
    
    # Swagger 2.0 can define basePath globally
    base_path = resolved_spec.get("basePath", "")

    for path, methods in paths.items():
        formatted_path = path if path.startswith("/") else f"/{path}"
        full_path = f"{base_path}{formatted_path}"
        full_url = f"{target_url.rstrip('/')}{full_path}"

        for method, operation in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete", "options", "head", "trace"]:
                continue

            extracted_params: list[Parameter] = []
            
            raw_params = methods.get("parameters", []) + operation.get("parameters", [])
            for p in raw_params:
                param = Parameter(
                    name=p.get("name", "unknown"),
                    value="",
                    location=p.get("in", "query")
                )
                extracted_params.append(param)

            endpoint = Endpoint(
                method=method.upper(),
                url=full_url,
                parameters=tuple(extracted_params)
            )
            endpoints.append(endpoint)

    logger.info("parse_swagger_completed", file_path=file_path, endpoint_count=len(endpoints))
    return tuple(endpoints)
