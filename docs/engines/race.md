# Race Condition Engine

The Race Condition Surface Detector (`prism/race/`) identifies check-then-act (TOCTOU) sequences from inferred API State Machines.

It statistically analyzes median response times to determine viable concurrency windows. It then targets high-value endpoints (financial operations, mutative single-use actions) by clustering and dispatching perfectly staggered asynchronous probe bursts to intentionally bypass backend transaction locks or induce deadlocks.
