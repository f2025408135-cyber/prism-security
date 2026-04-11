"""Tests for Verdict Extractor."""

import pytest

from prism.dialectic.debate import DebateTranscript
from prism.dialectic.verdict import VerdictExtractor

def test_verdict_extractor_attacker_wins() -> None:
    """Test extracting a TP verdict."""
    transcript = DebateTranscript(finding_id="f1", rounds=(), final_verdict="ATTACKER_WINS_TRUE_POSITIVE")
    extractor = VerdictExtractor()
    
    verdict = extractor.evaluate(transcript)
    
    assert verdict.finding_id == "f1"
    assert verdict.is_true_positive is True
    assert verdict.confidence > 0.8
    assert "conceded" in verdict.rationale

def test_verdict_extractor_defender_wins() -> None:
    """Test extracting an FP verdict."""
    transcript = DebateTranscript(finding_id="f1", rounds=(), final_verdict="DEFENDER_WINS_FALSE_POSITIVE")
    extractor = VerdictExtractor()
    
    verdict = extractor.evaluate(transcript)
    
    assert verdict.finding_id == "f1"
    assert verdict.is_true_positive is False
    assert verdict.confidence > 0.8
    assert "unexploitable" in verdict.rationale

def test_verdict_extractor_stalemate() -> None:
    """Test extracting a stalemate verdict."""
    transcript = DebateTranscript(finding_id="f1", rounds=(), final_verdict="STALEMATE")
    extractor = VerdictExtractor()
    
    verdict = extractor.evaluate(transcript)
    
    assert verdict.finding_id == "f1"
    assert verdict.is_true_positive is True # defaults to true on stalemate
    assert verdict.confidence <= 0.5
    assert "caution" in verdict.rationale
