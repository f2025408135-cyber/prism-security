# Academic Research & Basis

PRISM's engines are not random heuristics; they are grounded in established computer science and security research.

## State Machine Inference
PRISM's State Machine Inference engine builds heavily upon the concepts introduced by:

- **RESTler: Stateful REST API Fuzzing** (V. Atlidakis et al., ICSE 2019). PRISM adopts the methodology of dynamic dependency inference across API operations without requiring pre-existing specifications.
- **UML state machines for RESTful APIs**. PRISM borrows the state transition logic to model `non_existent` vs `terminal` states automatically.

## SMT Synthesis
The core of the zero-day engine utilizes the **Z3 Theorem Prover** by Microsoft Research. By reducing complex HTTP state anomalies into Boolean Satisfiability (SAT) problems, PRISM can mathematically prove the existence of an exploit chain rather than guessing via brute-force fuzzing.

## Dialectic Engines
The False Positive classification engine relies on adversarial dual-agent debate techniques shown to increase LLM reasoning accuracy (e.g., *Improving Factuality and Reasoning in Language Models through Multiagent Debate*, Du et al., 2023).
