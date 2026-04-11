# Synthesis Engine

The Z3 SMT Synthesis Engine (`prism/synthesis/`) mathematically proves the viability of attack chains by modeling API state transitions and authentication bypasses as boolean variables.

It encodes the environment universe into Z3 constraint formulas, asks the solver if an invariant (e.g. "Users cannot delete inactive resources") can be violated given the known facts, and translates the SAT model into a human-readable exploit narrative if an attack path exists.
