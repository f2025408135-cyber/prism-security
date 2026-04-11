"""OpenAPI 3.x specification parser."""

from typing import Any
import structlog
from prance import ResolvingParser
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

from prism.models.endpoint import Endpoint, Parameter
from prism.exceptions import IngestionError

logger = structlog.get_logger(__name__)


def parse_openapi_spec(file_path: str, target_url: str) -> tuple[Endpoint, ...]:
    """Parse an OpenAPI 3.x specification and extract endpoints.

    Args:
        file_path: The local path to the OpenAPI specification file (JSON or YAML).
        target_url: The base target URL to prepend to extracted paths.

    Returns:
        A tuple of extracted, frozen Endpoint models.

    Raises:
        IngestionError: If the file cannot be parsed or validation fails.
    """
    logger.info("parse_openapi_started", file_path=file_path)

    # Validate against OpenAPI 3.x schema
    try:
        spec_dict, _ = read_from_filename(file_path)
        validate(spec_dict)
    except Exception as e:
        logger.error("openapi_validation_failed", file_path=file_path, error=str(e))
        raise IngestionError(f"Failed to validate OpenAPI spec: {e}") from e

    # Parse and resolve $ref references
    try:
        parser = ResolvingParser(file_path, strict=False)
        resolved_spec = parser.specification
    except Exception as e:
        logger.error("openapi_resolution_failed", file_path=file_path, error=str(e))
        raise IngestionError(f"Failed to resolve OpenAPI spec references: {e}") from e

    endpoints: list[Endpoint] = []
    paths: dict[str, Any] = resolved_spec.get("paths", {})

    for path, methods in paths.items():
        # Ensure path starts with a slash
        formatted_path = path if path.startswith("/") else f"/{path}"
        full_url = f"{target_url.rstrip('/')}{formatted_path}"

        for method, operation in methods.items():
            if method.lower() not in ["get", "post", "put", "patch", "delete", "options", "head", "trace"]:
                continue

            extracted_params: list[Parameter] = []
            
            # Combine path-level parameters and operation-level parameters
            raw_params = methods.get("parameters", []) + operation.get("parameters", [])
            for p in raw_params:
                # We default value to empty string since specs usually only define names, not values
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

    logger.info("parse_openapi_completed", file_path=file_path, endpoint_count=len(endpoints))
    return tuple(endpoints)
