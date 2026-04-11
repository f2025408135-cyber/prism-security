"""GraphQL introspection parser."""

import httpx
import structlog
from typing import Any

from prism.models.endpoint import Endpoint, Parameter
from prism.exceptions import IngestionError
from prism.constants import DEFAULT_TIMEOUT_SECONDS

logger = structlog.get_logger(__name__)

INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name
      kind
      fields {
        name
        args {
          name
          type { name kind }
        }
      }
    }
  }
}
"""


async def parse_graphql_introspection(graphql_url: str) -> tuple[Endpoint, ...]:
    """Fetch and parse GraphQL introspection to generate endpoints.

    Since GraphQL typically operates on a single endpoint, this maps each
    Query and Mutation field into a conceptual PRISM Endpoint model (e.g. POST /graphql?op=myQuery).

    Args:
        graphql_url: The URL of the GraphQL endpoint.

    Returns:
        A tuple of extracted, frozen Endpoint models representing discrete operations.

    Raises:
        IngestionError: If introspection fails or is disabled.
    """
    logger.info("graphql_introspection_started", url=graphql_url)

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
            response = await client.post(graphql_url, json={"query": INTROSPECTION_QUERY})
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        logger.error("graphql_introspection_failed", url=graphql_url, error=str(e))
        raise IngestionError(f"Failed to fetch GraphQL introspection: {e}") from e

    schema = data.get("data", {}).get("__schema")
    if not schema:
        raise IngestionError("Invalid introspection response: missing __schema")

    query_type_name = schema.get("queryType", {}).get("name") if schema.get("queryType") else None
    mutation_type_name = schema.get("mutationType", {}).get("name") if schema.get("mutationType") else None

    endpoints: list[Endpoint] = []

    for t in schema.get("types", []):
        if t.get("name") not in [query_type_name, mutation_type_name]:
            continue

        op_type = "query" if t.get("name") == query_type_name else "mutation"
        fields = t.get("fields") or []

        for field in fields:
            op_name = field.get("name")
            
            # We model GraphQL operations as parameters inside a single POST Endpoint
            extracted_params: list[Parameter] = [
                Parameter(name="operationName", value=op_name, location="body"),
                Parameter(name="operationType", value=op_type, location="body"),
            ]

            for arg in field.get("args", []):
                extracted_params.append(
                    Parameter(name=arg.get("name"), value="", location="graphql_var")
                )

            endpoint = Endpoint(
                method="POST",
                url=graphql_url,
                parameters=tuple(extracted_params)
            )
            endpoints.append(endpoint)

    logger.info("graphql_introspection_completed", url=graphql_url, operation_count=len(endpoints))
    return tuple(endpoints)
