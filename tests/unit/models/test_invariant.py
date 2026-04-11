"""Tests for invariant data models."""

import pytest
from prism.models.invariant import Invariant, InvariantResult

def test_invariant_creation() -> None:
    """Test creation of an Invariant model."""
    inv = Invariant(
        id="inv_1",
        description="A user cannot delete another user's account.",
        severity="CRITICAL"
    )
    
    assert inv.id == "inv_1"
    assert inv.severity == "CRITICAL"

def test_invariant_result_creation() -> None:
    """Test creation of an InvariantResult model."""
    res = InvariantResult(
        invariant_id="inv_1",
        is_violated=True,
        proof_chain=("prim_1", "prim_2")
    )
    
    assert res.invariant_id == "inv_1"
    assert res.is_violated is True
    assert len(res.proof_chain) == 2

def test_invariant_is_frozen() -> None:
    """Test that the Invariant model is immutable."""
    inv = Invariant(id="i", description="d")
    with pytest.raises(Exception):
        inv.severity = "LOW"  # type: ignore
