"""Tests for Transcript Storage."""

import json
from pathlib import Path

from prism.dialectic.debate import DebateTranscript
from prism.dialectic.storage import TranscriptStorage

def test_transcript_storage_store(tmp_path: Path) -> None:
    """Test storing a debate transcript to disk."""
    storage = TranscriptStorage(str(tmp_path))
    
    transcript = DebateTranscript(
        finding_id="f1",
        final_verdict="STALEMATE",
        rounds=({"attacker": "A says", "defender": "B says"},)
    )
    
    path = storage.store(transcript)
    
    assert Path(path).exists()
    
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data["finding_id"] == "f1"
    assert data["final_verdict"] == "STALEMATE"
    assert data["rounds"][0]["attacker"] == "A says"
