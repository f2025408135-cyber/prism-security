"""Tests for Z3 solver orchestration."""

import pytest

from prism.synthesis.primitive import PrimitiveFact
from prism.models.invariant import Invariant
from prism.synthesis.encoder import Z3Encoder
from prism.synthesis.solver import SynthesisSolver

def test_check_invariant_sat() -> None:
    """Test the solver successfully finds a violation (SAT)."""
    encoder = Z3Encoder()
    solver = SynthesisSolver(encoder)
    
    inv = Invariant(id="inv_1", description="Users cannot delete inactive resources")
    
    f1 = PrimitiveFact(id="f1", fact_type="authz_bypass", actor="u1", target_resource="res", precondition="inactive", postcondition="deleted", evidence_id="e1")
    f2 = PrimitiveFact(id="f2", fact_type="state_transition", actor="u1", target_resource="res", precondition="created", postcondition="inactive", evidence_id="e2")
    
    result = solver.check_invariant(inv, [f1, f2])
    
    assert result.is_violated is True
    assert result.invariant_id == "inv_1"
    # Given our encoding rules, it should set f1 and f2 to True to violate the rule
    assert "f1" in result.proof_chain
    assert "f2" in result.proof_chain

def test_check_invariant_unsat() -> None:
    """Test the solver proves safety (UNSAT)."""
    encoder = Z3Encoder()
    solver = SynthesisSolver(encoder)
    
    inv = Invariant(id="inv_1", description="Must be admin to access")
    
    # Empty fact pool means no possible way to violate the invariant
    result = solver.check_invariant(inv, [])
    
    assert result.is_violated is False
    assert len(result.proof_chain) == 0
