"""Interpreter translating Z3 mathematical models to human attack chains."""

import structlog
from typing import Any

from prism.synthesis.primitive import PrimitiveFact
from prism.models.invariant import InvariantResult

logger = structlog.get_logger(__name__)


class SynthesisInterpreter:
    """Translates the SAT model from Z3 into a human-readable format."""

    def interpret(self, result: InvariantResult, all_facts: list[PrimitiveFact]) -> str:
        """Translate the proof chain into an attack narrative.

        Args:
            result: The InvariantResult from the solver.
            all_facts: The full list of available PrimitiveFacts to cross-reference IDs.

        Returns:
            A human-readable string explaining the attack sequence.
        """
        logger.debug("interpreting_synthesis_result", invariant_id=result.invariant_id)

        if not result.is_violated:
            return "No attack chain found. The system is mathematically proven safe against this invariant based on current facts."

        if not result.proof_chain:
            return "Invariant violated, but no specific fact chain was extracted."

        # Map IDs back to fact objects
        fact_map = {f.id: f for f in all_facts}
        chain_facts = [fact_map[fid] for fid in result.proof_chain if fid in fact_map]

        narrative = "Attack Chain Synthesized:\n"
        
        for i, fact in enumerate(chain_facts, 1):
            narrative += f"Step {i}: [{fact.fact_type.upper()}] "
            narrative += f"Actor '{fact.actor}' targets '{fact.target_resource}'. "
            narrative += f"Changes state from '{fact.precondition}' to '{fact.postcondition}'.\n"
            
        narrative += "\nConclusion: The combination of these primitives successfully violates the security invariant."
        
        return narrative
