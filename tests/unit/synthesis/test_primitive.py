"""Tests for Primitive Schema."""

import pytest
from pydantic import ValidationError
from prism.synthesis.primitive import PrimitiveFact, VALID_FACT_TYPES

def test_primitive_fact_creation() -> None:
    """Test valid fact creation."""
    fact = PrimitiveFact(
        id="1",
        fact_type="authz_bypass",
        actor="user1",
        target_resource="document",
        precondition="created",
        postcondition="deleted",
        evidence_id="ev_1"
    )
    
    assert fact.id == "1"
    assert fact.fact_type == "authz_bypass"
    assert fact.actor == "user1"
    assert fact.target_resource == "document"
    assert fact.precondition == "created"
    assert fact.postcondition == "deleted"

def test_primitive_fact_invalid_type() -> None:
    """Test invalid fact_type raises ValueError in post_init."""
    with pytest.raises(ValueError, match="Invalid fact_type: fake_type"):
        PrimitiveFact(
            id="1",
            fact_type="fake_type",
            actor="user1",
            target_resource="doc",
            evidence_id="ev_1"
        ).__post_init__()
