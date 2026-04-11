"""Storage for debate transcripts for human review."""

import json
import structlog
from pathlib import Path
from typing import Any

from prism.dialectic.debate import DebateTranscript
from prism.exceptions import StorageError

logger = structlog.get_logger(__name__)


class TranscriptStorage:
    """Persists adversarial debate transcripts to disk for human researchers to audit."""

    def __init__(self, workspace_dir: str) -> None:
        """Initialize the transcript storage.

        Args:
            workspace_dir: The .prism root workspace directory.
        """
        self.workspace_dir = Path(workspace_dir)
        self.transcripts_dir = self.workspace_dir / "transcripts"
        
        try:
            self.transcripts_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error("transcript_storage_init_failed", error=str(e))
            raise StorageError(f"Failed to initialize transcript storage: {e}") from e

    def store(self, transcript: DebateTranscript) -> str:
        """Save a debate transcript to a JSON file.

        Args:
            transcript: The transcript to store.

        Returns:
            The path to the saved file.

        Raises:
            StorageError: If the file cannot be written.
        """
        file_name = f"transcript_{transcript.finding_id}.json"
        file_path = self.transcripts_dir / file_name

        # Convert the immutable Pydantic model to a standard dict for JSON serialization
        data = {
            "finding_id": transcript.finding_id,
            "final_verdict": transcript.final_verdict,
            "rounds": list(transcript.rounds)
        }

        try:
            with file_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("transcript_store_failed", finding_id=transcript.finding_id, error=str(e))
            raise StorageError(f"Failed to write transcript {transcript.finding_id}: {e}") from e

        logger.info("transcript_stored", finding_id=transcript.finding_id, path=str(file_path))
        return str(file_path)
