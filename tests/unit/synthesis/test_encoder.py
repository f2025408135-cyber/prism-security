"""Tests for Z3 constraints encoder."""

import pytest
from z3 import Solver

from prism.synthesis.primitive import PrimitiveFact
from prism.models.invariant import Invariant
from prism.synthesis.encoder import Z3Encoder

def test_encode_facts() -> None:
    """Test encoding facts creates Z3 Boolean variables."""
    encoder = Z3Encoder()
    solver = Solver()
    
    fact1 = PrimitiveFact(id="f1", fact_type="authz_bypass", actor="u1", target_resource="res", evidence_id="e1")
    fact2 = PrimitiveFact(id="f2", fact_type="state_transition", actor="u1", target_resource="res", evidence_id="e2")
    
    encoder.encode_facts(solver, [fact1, fact2])
    
    assert "f1" in encoder.fact_vars
    assert "f2" in encoder.fact_vars

def test_encode_invariant_violation() -> None:
    """Test generating a solver goal from facts."""
    encoder = Z3Encoder()
    solver = Solver()
    
    inv = Invariant(id="inv1", description="desc")
    
    fact1 = PrimitiveFact(id="f1", fact_type="authz_bypass", actor="u1", target_resource="res", evidence_id="e1")
    
    encoder.encode_facts(solver, [fact1])
    encoder.encode_invariant_violation(solver, inv, [fact1])
    
    # It should add a constraint that the authz bypass is True
    # If we check the solver now, it should be SAT
    assert solver.check().r == 1
