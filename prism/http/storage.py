"""Raw request/response storage for audit and replay."""

import json
import uuid
import structlog
from pathlib import Path
from typing import Any

from prism.exceptions import StorageError

logger = structlog.get_logger(__name__)


class TrafficStorage:
    """Persists raw HTTP traffic to append-only JSON Lines files.

    This ensures every request PRISM makes is recorded for audit trails,
    evidence generation, and replay functionality.
    """

    def __init__(self, workspace_dir: str) -> None:
        """Initialize the storage engine.

        Args:
            workspace_dir: The directory where traffic logs should be stored.
        """
        self.workspace_dir = Path(workspace_dir)
        self.traffic_file = self.workspace_dir / "traffic.jsonl"
        
        try:
            self.workspace_dir.mkdir(parents=True, exist_ok=True)
            self.traffic_file.touch(exist_ok=True)
        except Exception as e:
            logger.error("traffic_storage_init_failed", error=str(e))
            raise StorageError(f"Failed to initialize traffic storage in {workspace_dir}: {e}") from e

    def store(
        self,
        principal_id: str,
        request_kwargs: dict[str, Any],
        status_code: int,
        response_headers: tuple[tuple[str, str], ...],
        response_body: str,
        timing_ms: float
    ) -> str:
        """Store a single HTTP exchange.

        Args:
            principal_id: The ID of the principal making the request.
            request_kwargs: The httpx kwargs used to build the request.
            status_code: The resulting HTTP status code.
            response_headers: The response headers.
            response_body: The response body excerpt.
            timing_ms: The duration of the request in milliseconds.

        Returns:
            The unique UUID of the stored exchange.

        Raises:
            StorageError: If the write operation fails.
        """
        exchange_id = str(uuid.uuid4())
        
        # Mask sensitive headers in storage
        safe_kwargs = request_kwargs.copy()
        if "headers" in safe_kwargs:
            safe_headers = safe_kwargs["headers"].copy()
            if "Authorization" in safe_headers:
                val = safe_headers["Authorization"]
                safe_headers["Authorization"] = val[:15] + "..." if len(val) > 15 else "***"
            safe_kwargs["headers"] = safe_headers

        record = {
            "id": exchange_id,
            "principal_id": principal_id,
            "request": safe_kwargs,
            "response": {
                "status_code": status_code,
                "headers": dict(response_headers),
                "body_excerpt": response_body,
                "timing_ms": timing_ms
            }
        }

        try:
            # We use synchronous append for simplicity in this implementation,
            # though in a massively parallel scenario anyio.Path might be preferable.
            with self.traffic_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record) + "\n")
        except Exception as e:
            logger.error("traffic_storage_write_failed", exchange_id=exchange_id, error=str(e))
            raise StorageError(f"Failed to write traffic record {exchange_id}") from e

        return exchange_id

    def load_all(self) -> list[dict[str, Any]]:
        """Load all stored traffic records.

        Returns:
            A list of dictionary records.

        Raises:
            StorageError: If reading the file fails.
        """
        records: list[dict[str, Any]] = []
        try:
            with self.traffic_file.open("r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        records.append(json.loads(line))
        except Exception as e:
            logger.error("traffic_storage_read_failed", error=str(e))
            raise StorageError(f"Failed to read traffic logs: {e}") from e

        return records
