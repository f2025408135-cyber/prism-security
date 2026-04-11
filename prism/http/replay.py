"""Replay engine for stored requests."""

import structlog
from typing import Any

from prism.http.client import AsyncHttpClient
from prism.http.storage import TrafficStorage
from prism.http.response import parse_response
from prism.models.endpoint import Response
from prism.exceptions import NetworkError

logger = structlog.get_logger(__name__)


class ReplayEngine:
    """Executes stored requests to verify determinism or replay attacks."""

    def __init__(self, client: AsyncHttpClient, storage: TrafficStorage) -> None:
        """Initialize the replay engine.

        Args:
            client: An active AsyncHttpClient.
            storage: The TrafficStorage instance containing logs.
        """
        self.client = client
        self.storage = storage

    async def replay_by_id(self, exchange_id: str) -> Response | None:
        """Replay a specific request by its exchange ID.

        Args:
            exchange_id: The UUID of the request to replay.

        Returns:
            The new Response model, or None if the ID was not found.
            
        Raises:
            NetworkError: If the HTTP request fails.
        """
        logger.info("replay_started", exchange_id=exchange_id)
        
        records = self.storage.load_all()
        target_record = next((r for r in records if r.get("id") == exchange_id), None)
        
        if not target_record:
            logger.warning("replay_record_not_found", exchange_id=exchange_id)
            return None
            
        request_kwargs: dict[str, Any] = target_record.get("request", {})
        
        # Extract method and url, the rest are passed to httpx
        method = request_kwargs.pop("method", "GET")
        url = request_kwargs.pop("url", "")
        
        if not url:
            logger.error("replay_invalid_record", exchange_id=exchange_id)
            raise NetworkError(f"Cannot replay invalid record {exchange_id}: missing URL")

        # Note: Because we mask Authorization tokens in storage for safety, 
        # a true full-fidelity replay might fail auth unless we reconstruct it via PrincipalManager.
        # This implementation replays what was stored.
        
        httpx_response, timing_ms = await self.client.request(method, url, **request_kwargs)
        
        response = parse_response(httpx_response, timing_ms)
        logger.info("replay_completed", exchange_id=exchange_id, new_status=response.status_code)
        
        return response
