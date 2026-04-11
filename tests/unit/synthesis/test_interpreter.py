"""Tests for the interpreter."""

import pytest

from prism.synthesis.primitive import PrimitiveFact
from prism.models.invariant import InvariantResult
from prism.synthesis.interpreter import SynthesisInterpreter

def test_interpret_violation() -> None:
    """Test mapping a proof chain back to English text."""
    interpreter = SynthesisInterpreter()
    
    f1 = PrimitiveFact(id="f1", fact_type="authz_bypass", actor="hacker", target_resource="database", precondition="locked", postcondition="open", evidence_id="e1")
    
    res = InvariantResult(invariant_id="inv", is_violated=True, proof_chain=("f1",))
    
    narrative = interpreter.interpret(res, [f1])
    
    assert "Attack Chain Synthesized:" in narrative
    assert "[AUTHZ_BYPASS]" in narrative
    assert "Actor 'hacker'" in narrative
    assert "from 'locked' to 'open'" in narrative

def test_interpret_safe() -> None:
    """Test interpreting an UNSAT result."""
    interpreter = SynthesisInterpreter()
    
    res = InvariantResult(invariant_id="inv", is_violated=False, proof_chain=())
    narrative = interpreter.interpret(res, [])
    
    assert "mathematically proven safe" in narrative
