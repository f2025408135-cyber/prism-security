"""Tests for False Positive Classifier."""

import pytest

from prism.dialectic.verdict import DebateVerdict
from prism.dialectic.classifier import FalsePositiveClassifier
from prism.models.finding import Finding

def test_classifier_kills_false_positive() -> None:
    """Test dropping findings with high confidence FP."""
    finding = Finding(id="f1", title="title", description="desc", cwe_id="cwe", cvss_vector="cvss")
    verdict = DebateVerdict(finding_id="f1", is_true_positive=False, rationale="bad", confidence=0.9)
    
    classifier = FalsePositiveClassifier(confidence_threshold=0.8)
    survivor = classifier.classify(finding, verdict)
    
    assert survivor is None

def test_classifier_keeps_true_positive() -> None:
    """Test retaining findings that are true positives."""
    finding = Finding(id="f1", title="title", description="desc", cwe_id="cwe", cvss_vector="cvss")
    verdict = DebateVerdict(finding_id="f1", is_true_positive=True, rationale="good", confidence=0.9)
    
    classifier = FalsePositiveClassifier(confidence_threshold=0.8)
    survivor = classifier.classify(finding, verdict)
    
    assert survivor is not None
    assert survivor.id == "f1"
    assert "[Dialectic Rationale]: good" in survivor.description

def test_classifier_keeps_low_confidence_fp() -> None:
    """Test keeping a finding if FP confidence is too low."""
    finding = Finding(id="f1", title="title", description="desc", cwe_id="cwe", cvss_vector="cvss")
    verdict = DebateVerdict(finding_id="f1", is_true_positive=False, rationale="bad", confidence=0.5)
    
    classifier = FalsePositiveClassifier(confidence_threshold=0.8)
    survivor = classifier.classify(finding, verdict)
    
    assert survivor is not None
    assert survivor.id == "f1"
