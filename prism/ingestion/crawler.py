"""Wrapper for ProjectDiscovery's Katana crawler."""

import json
import asyncio
import structlog
from urllib.parse import urlparse, parse_qsl

from prism.models.endpoint import Endpoint, Parameter
from prism.exceptions import IngestionError

logger = structlog.get_logger(__name__)


async def run_katana_crawler(target_url: str, depth: int = 3) -> tuple[Endpoint, ...]:
    """Run katana crawler as a subprocess and parse its JSONL output.

    Katana must be installed and available in the system PATH.

    Args:
        target_url: The base URL to crawl.
        depth: The maximum crawl depth.

    Returns:
        A tuple of extracted, frozen Endpoint models.

    Raises:
        IngestionError: If the subprocess fails or katana is not installed.
    """
    logger.info("katana_crawler_started", target_url=target_url, depth=depth)

    # Note: '-j' outputs JSONL
    cmd = [
        "katana",
        "-u", target_url,
        "-d", str(depth),
        "-j",
        "-silent"
    ]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
    except FileNotFoundError as e:
        logger.error("katana_not_found", error=str(e))
        raise IngestionError("Katana is not installed or not in PATH.") from e
    except Exception as e:
        logger.error("katana_execution_failed", error=str(e))
        raise IngestionError(f"Katana execution failed: {e}") from e

    if process.returncode != 0:
        logger.warning("katana_returned_non_zero", returncode=process.returncode, stderr=stderr.decode())

    endpoints: list[Endpoint] = []
    seen_signatures = set()

    for line in stdout.decode().splitlines():
        if not line.strip():
            continue
            
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        url = data.get("request", {}).get("endpoint", "")
        if not url:
            continue

        method = data.get("request", {}).get("method", "GET").upper()

        # Deduplication signature
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        signature = f"{method}:{base_url}"

        if signature in seen_signatures:
            continue
        seen_signatures.add(signature)

        extracted_params: list[Parameter] = []

        # Katana provides query strings in the URL
        if parsed_url.query:
            queries = parse_qsl(parsed_url.query)
            for k, v in queries:
                extracted_params.append(Parameter(name=k, value=v, location="query"))

        endpoint = Endpoint(
            method=method,
            url=url,
            parameters=tuple(extracted_params)
        )
        endpoints.append(endpoint)

    logger.info("katana_crawler_completed", endpoint_count=len(endpoints))
    return tuple(endpoints)
