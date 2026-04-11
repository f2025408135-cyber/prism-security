"""Z3 Theorem Prover orchestration."""

import structlog
from z3 import Solver, sat, unsat, unknown # type: ignore

from prism.synthesis.primitive import PrimitiveFact
from prism.models.invariant import Invariant, InvariantResult
from prism.synthesis.encoder import Z3Encoder
from prism.exceptions import PrismError

logger = structlog.get_logger(__name__)


class SynthesisSolver:
    """Executes SMT queries to mathematically prove vulnerability chains."""

    def __init__(self, encoder: Z3Encoder) -> None:
        """Initialize the solver.

        Args:
            encoder: The configured Z3Encoder.
        """
        self.encoder = encoder

    def check_invariant(self, invariant: Invariant, available_facts: list[PrimitiveFact]) -> InvariantResult:
        """Check if an invariant can be violated using the available facts.

        Args:
            invariant: The invariant to test.
            available_facts: The pool of confirmed primitives the attacker can use.

        Returns:
            An InvariantResult detailing if it was violated and the proof chain.
        """
        logger.info("smt_solver_started", invariant_id=invariant.id, facts_available=len(available_facts))

        solver = Solver()
        
        # 1. Encode the universe of possibilities (the graph)
        self.encoder.encode_facts(solver, available_facts)
        
        # 2. Encode the attacker's goal (violating the invariant)
        self.encoder.encode_invariant_violation(solver, invariant, available_facts)
        
        # 3. Check satisfiability
        result = solver.check()
        
        if result == sat:
            logger.warning("invariant_violation_proven", invariant_id=invariant.id)
            model = solver.model()
            
            # Extract which facts the solver set to True to achieve the violation
            proof_chain: list[str] = []
            for fact in available_facts:
                fact_var = self.encoder.fact_vars.get(fact.id)
                # If the variable exists in the model and is evaluated to True
                if fact_var is not None and model.evaluate(fact_var, model_completion=True):
                    proof_chain.append(fact.id)
                    
            return InvariantResult(
                invariant_id=invariant.id,
                is_violated=True,
                proof_chain=tuple(proof_chain)
            )
            
        elif result == unsat:
            logger.info("invariant_proven_safe", invariant_id=invariant.id)
            return InvariantResult(
                invariant_id=invariant.id,
                is_violated=False,
                proof_chain=()
            )
            
        else:
            logger.error("smt_solver_timeout_or_unknown", invariant_id=invariant.id)
            raise PrismError(f"Z3 solver failed to resolve invariant {invariant.id} (returned {result})")
