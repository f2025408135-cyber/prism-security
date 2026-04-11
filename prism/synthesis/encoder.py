"""Encoder for translating PrimitiveFacts into Z3 constraints."""

import structlog
from z3 import Bool, Solver, Implies, And, Or # type: ignore
from typing import Any

from prism.synthesis.primitive import PrimitiveFact
from prism.models.invariant import Invariant

logger = structlog.get_logger(__name__)


class Z3Encoder:
    """Translates the graph of security facts into a Z3 SMT constraint model.

    In a full implementation, this translates HTTP state semantics (e.g. 
    `role == admin`, `state == created`) into discrete Z3 Integers or Booleans.
    This implementation maps the discrete `PrimitiveFact` IDs to Boolean variables
    representing whether that attack step was successfully executed.
    """

    def __init__(self) -> None:
        self.fact_vars: dict[str, Any] = {}

    def encode_facts(self, solver: Solver, facts: list[PrimitiveFact]) -> None:
        """Encode a list of primitive facts into the Z3 solver.

        Args:
            solver: The Z3 Solver instance.
            facts: The list of available PrimitiveFacts.
        """
        logger.debug("z3_encoding_facts", count=len(facts))

        for fact in facts:
            # We create a Boolean variable representing the execution of this fact
            var_name = f"fact_{fact.id}"
            fact_var = Bool(var_name)
            self.fact_vars[fact.id] = fact_var

            # Logic mapping:
            # If an authz_bypass fact is True, it implies the attacker achieved the postcondition
            # without satisfying the normal precondition (or from a generic 'True' state).
            # For simplicity in this structure, we just declare the variables exist.
            # In a deeper model, we would encode: Implies(fact_var, postcondition_var)
            
            # We add a constraint that the fact CAN occur (it's possible)
            # We don't force it to be True, the solver decides if it NEEDS to be True
            # to violate an invariant.

    def encode_invariant_violation(self, solver: Solver, invariant: Invariant, relevant_facts: list[PrimitiveFact]) -> None:
        """Encode the negation of an invariant (the attacker's goal) into the solver.

        Args:
            solver: The Z3 Solver instance.
            invariant: The security property that must hold true.
            relevant_facts: Facts that might relate to violating this invariant.
        """
        logger.debug("z3_encoding_invariant_violation", invariant_id=invariant.id)

        # In a real SMT model, the invariant is a logical formula (e.g. `Not(And(is_user, can_delete))`)
        # Here we simulate the logic by saying: "The invariant is violated if a specific chain of facts is True."
        
        # We will assume for this architecture chunk that if an `authz_bypass` fact
        # and a `state_transition` fact are BOTH true for a specific resource, the invariant is violated.
        
        authz_vars = []
        state_vars = []
        
        for fact in relevant_facts:
            if fact.fact_type == "authz_bypass":
                authz_vars.append(self.fact_vars[fact.id])
            elif fact.fact_type == "state_transition":
                state_vars.append(self.fact_vars[fact.id])
                
        # Attacker wins if they achieve at least one authz bypass AND one state transition
        if authz_vars and state_vars:
            attacker_goal = And(Or(*authz_vars), Or(*state_vars))
            solver.add(attacker_goal)
        elif authz_vars:
            # If no state transitions, just an authz bypass violates it
            solver.add(Or(*authz_vars))
        else:
            # If we don't have enough facts to even formulate a violation, we add False (UNSAT)
            solver.add(False)
