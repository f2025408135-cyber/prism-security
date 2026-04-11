# PRISM Architecture

PRISM is split into 10 distinct, modular phases connected by an asynchronous `IHTTPExecutor` pipeline and a shared SQLite data layer.

## Pipeline Flow

1. **Ingestion Engine**: Ingests endpoints from Swagger, OpenAPI, HAR files, Postman collections, active Katana crawls, JS Bundles, and GraphQL introspection.
2. **HTTP Engine**: Provides adaptive rate-limiting, strict scope enforcement, and stores all raw requests/responses for replay and evidence gathering.
3. **Authorization Topology Mapper**: Fires endpoints using a multi-principal matrix to map out exactly what objects a user can interact with vs. what they *should* interact with.
4. **State Machine Inference**: Detects mutative operations (POST/PUT/DELETE) and maps them to resource lifecycles (`non_existent` -> `created`).
5. **Race Condition Detector**: Finds Check-Then-Act sequences, analyzes their latencies, and attacks single-use endpoints concurrently.
6. **Primitive Graph & Z3 Synthesis**: Converts findings into boolean variables and runs them through a Z3 SMT solver to mathematically prove complex exploit chains.
7. **Dialectic Engine**: Pit an "Attacker" LLM against a "Defender" LLM to debate the validity of a finding, dropping false positives dynamically.
8. **Reporting**: Generates CVSS vectors, CWE mappings, and Markdown/HTML/JSON reports.
