# PRISM — AGENTS.md
# Master instruction file for Google Jules
# Jules reads this before EVERY task. Every rule here is non-negotiable.
# Last updated: keep this current as project evolves.

---

## SECTION 0 — WHAT THIS PROJECT IS

PRISM is a production-grade open source Python security research framework.
It maps API authorization topology as a directed graph, infers business logic
state machines from HTTP traffic, and finds authorization inconsistencies and
race conditions automatically.

This is NOT a prototype. NOT a demo. NOT a script.
Every module Jules writes is production code that security researchers
will stake their professional reputation on.

A security researcher using PRISM on an authorized target will file
vulnerability reports based on PRISM's output. If PRISM produces
incorrect results, the researcher files an invalid report and loses
their credibility with a bug bounty program. The cost of slop here
is not aesthetics — it is professional damage.

This context governs every decision Jules makes.

---

## SECTION 1 — HOW JULES MUST WORK ON THIS PROJECT

### 1.1 Task Size Rule — NON-NEGOTIABLE

Jules receives one file per task. Maximum 400 lines per file.
Never combine two files into one task.
Never create more files than the task specifies.

If Jules believes a file needs more than 400 lines:
  → Split the file into two logical files
  → Implement file 1 completely
  → Note in the PR: "File 2 needed: [name] — [what it contains]"
  → Stop. Do not attempt file 2 in the same task.

This rule exists because:
  a) Jules loses coherence past 400 LOC in a single pass
  b) The critic cannot effectively review oversized outputs
  c) Human review of large diffs catches fewer errors
  d) Small PRs are easier to roll back when wrong

### 1.2 Interface-First Rule

Every new file Jules writes must implement an interface that already exists
in the codebase as either:
  a) A Protocol class in prism/interfaces/[module].py
  b) A type alias in prism/types.py
  c) Explicit function signatures in the task description

If an interface does not exist for the file Jules is writing:
  → Jules creates the interface file FIRST as a separate PR
  → Jules does NOT implement the concrete class until 
    the interface PR is merged
  → Jules flags this in the PR: "Interface file created. 
    Implementation ready when interface is merged."

### 1.3 Dependency Rule

Jules may only use packages listed in pyproject.toml.
If Jules needs a new package:
  → Add it to pyproject.toml [dependencies] section
  → Add a comment: # Added for [module] — [reason]
  → Never use a package not in the dependency list

Approved packages for this project:
  httpx[http2]        # HTTP client with HTTP/2 support
  pydantic>=2.0       # Data validation and models
  sqlalchemy>=2.0     # ORM and persistence
  alembic             # Database migrations
  networkx            # Graph data structures
  z3-solver           # Theorem prover for synthesis engine
  rich                # Terminal UI and output
  typer               # CLI framework
  litellm             # LLM routing (dialectic engine only)
  pyvis               # Graph visualization
  mitmproxy           # Proxy integration
  pytest              # Testing framework
  pytest-asyncio      # Async test support
  pytest-httpx        # HTTP mocking for tests
  respx               # httpx request mocking
  openapi-spec-validator  # OpenAPI parsing
  prance              # OpenAPI $ref resolution
  PyYAML              # YAML config files
  structlog           # Structured logging
  tenacity            # Retry logic

Jules must NEVER add:
  requests            # Use httpx instead
  aiohttp             # Use httpx instead
  click               # Use typer instead
  flask / fastapi     # PRISM is a CLI tool, not a server
  Any package not in the approved list without explicit task instruction

---

## SECTION 2 — PYTHON STANDARDS — EVERY FILE

### 2.1 Type Hints — Mandatory Everywhere

Every function signature must have complete type hints.
Every class attribute must have a type annotation.
No bare Any except where explicitly documented with a comment.

CORRECT:
```python
async def probe_endpoint(
    endpoint: Endpoint,
    principal: Principal,
    timeout: float = 30.0,
) -> AuthzDecision:
    ...
```

WRONG:
```python
async def probe_endpoint(endpoint, principal, timeout=30.0):
    ...
```

Use Python 3.11+ union syntax:
  CORRECT: str | None
  WRONG:   Optional[str]

Use built-in generic types:
  CORRECT: list[str], dict[str, int], tuple[str, ...]
  WRONG:   List[str], Dict[str, int], Tuple[str, ...]

### 2.2 Docstrings — Mandatory on All Public Functions and Classes

Use Google-style docstrings. Minimum: one-line summary + Args + Returns.
Add Raises when the function raises exceptions.
Add Examples for non-obvious behavior.

CORRECT:
```python
async def probe_endpoint(
    endpoint: Endpoint,
    principal: Principal,
    timeout: float = 30.0,
) -> AuthzDecision:
    """Probe a single endpoint with a single principal context.

    Sends an authenticated HTTP request and returns the authorization
    decision observed from the response. Does not modify any state.

    Args:
        endpoint: The endpoint specification to probe.
        principal: The authentication context to use.
        timeout: Request timeout in seconds. Defaults to 30.0.

    Returns:
        AuthzDecision containing HTTP status, response headers,
        body excerpt, and timing information.

    Raises:
        NetworkError: If the request fails due to connectivity.
        TimeoutError: If the request exceeds the timeout.

    Examples:
        >>> decision = await probe_endpoint(endpoint, principal_a)
        >>> print(decision.http_status)
        200
    """
```

WRONG: No docstring, or one-line only with no Args/Returns.

### 2.3 Error Handling — Explicit Always

Never use bare except.
Never swallow exceptions silently.
Always wrap external calls (HTTP, DB, file IO) in explicit exception handlers.
Always log the exception with structlog before re-raising or returning error.

CORRECT:
```python
try:
    response = await self.client.get(url, headers=headers)
except httpx.TimeoutException as e:
    self.logger.error(
        "probe_timeout",
        url=url,
        timeout=timeout,
        error=str(e),
    )
    raise NetworkError(f"Timeout after {timeout}s: {url}") from e
except httpx.ConnectError as e:
    self.logger.error(
        "probe_connect_error",
        url=url,
        error=str(e),
    )
    raise NetworkError(f"Connection failed: {url}") from e
```

WRONG:
```python
try:
    response = await self.client.get(url)
except Exception:
    pass
```

### 2.4 Logging — structlog Everywhere

Every module gets a module-level logger:
```python
import structlog
logger = structlog.get_logger(__name__)
```

Log at these levels with these semantics:
  logger.debug()  — internal state useful for debugging
  logger.info()   — significant operations (probe sent, finding created)
  logger.warning() — recoverable anomalies (rate limited, retry)
  logger.error()  — failures that affect output (probe failed, DB error)

Every log call must use keyword arguments, never string formatting:
  CORRECT: logger.info("probe_sent", endpoint=url, principal=principal_id)
  WRONG:   logger.info(f"Probe sent to {url}")

### 2.5 Immutability — Pydantic Models are Frozen

All Pydantic models in prism/models/ must use model_config with frozen=True
unless the model represents mutable work-in-progress state.
```python
class Endpoint(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    method: str
    parameters: tuple[Parameter, ...]  # tuple, not list — immutable
```

Use tuple instead of list for collections in frozen models.
Use frozenset instead of set for frozen models.

### 2.6 Async — httpx Operations Are Always Async

All HTTP operations use async/await.
All database operations use SQLAlchemy async session.
All file I/O in hot paths uses anyio.

Sync functions are acceptable for:
  - Pure computation (no I/O)
  - CLI entry points (Typer handles the async boundary)
  - Configuration loading at startup

### 2.7 Constants — Never Magic Numbers

No magic numbers anywhere. All constants go in prism/constants.py.

WRONG:
```python
if response.status_code == 200:
    ...
if timing_ms > 5000:
    ...
```

CORRECT:
```python
from prism.constants import HTTP_OK, TIMING_OUTLIER_THRESHOLD_MS

if response.status_code == HTTP_OK:
    ...
if timing_ms > TIMING_OUTLIER_THRESHOLD_MS:
    ...
```

---

## SECTION 3 — TESTING STANDARDS — EVERY FILE

### 3.1 Test File Location and Naming

Every prism/[module]/[file].py gets a test file at:
  tests/unit/[module]/test_[file].py

Jules creates the test file in the SAME PR as the implementation.
Never submit an implementation PR without tests.

### 3.2 Test Coverage Requirements

Minimum coverage per file: 80%.
For security-critical paths (prism/http/, prism/mapper/, prism/synthesis/):
  Minimum coverage: 90%.

### 3.3 What Must Be Tested

For every public function:
  1. Happy path (expected input, expected output)
  2. Boundary conditions (empty input, None, zero, max values)
  3. Error conditions (what happens when dependencies fail)
  4. Type contract (does the function reject wrong types gracefully?)

### 3.4 HTTP Mocking — Never Hit Real Networks in Tests

Use respx to mock all httpx calls in tests.
Never make real HTTP requests in any test.
Every test that involves HTTP must mock the HTTP layer explicitly.

CORRECT pattern:
```python
import respx
import httpx
import pytest

@pytest.mark.asyncio
@respx.mock
async def test_probe_endpoint_returns_200():
    respx.get("https://api.example.com/users/1").mock(
        return_value=httpx.Response(200, json={"id": 1, "name": "Alice"})
    )
    
    endpoint = Endpoint(url="https://api.example.com/users/1", method="GET")
    principal = Principal(token="test_token_abc")
    
    decision = await probe_endpoint(endpoint, principal)
    
    assert decision.http_status == 200
    assert decision.principal_id == principal.id
```

### 3.5 Fixtures Location

Shared fixtures go in tests/conftest.py.
Module-specific fixtures go in tests/unit/[module]/conftest.py.
Sample OpenAPI specs for testing go in tests/fixtures/specs/.
Sample HTTP responses go in tests/fixtures/responses/.

### 3.6 Test Names — Descriptive Always

CORRECT: test_probe_endpoint_returns_authz_denied_when_token_expired
WRONG:   test_probe_1, test_it_works, test_endpoint

---

## SECTION 4 — SECURITY CONSTRAINTS

### 4.1 This Tool Tests APIs — It Has an Attack Surface Itself

PRISM handles: authentication tokens, API keys, session cookies,
raw HTTP responses from potentially hostile servers.

Jules must treat all of these as untrusted input:
  - Never log token values (log first 8 chars only: token[:8] + "...")
  - Never store token values in plaintext in SQLite
    (store a reference ID and load from environment/keychain)
  - Never eval() or exec() any data from HTTP responses
  - Never use pickle for any data that touched external input
  - Validate all data from external sources with Pydantic before use

### 4.2 Scope Enforcement is Safety-Critical

prism/http/scope.py is the scope enforcement guard.
Every probe MUST pass through scope.is_in_scope() before execution.
This is not optional. This is not a feature. This is a hard stop.

Any code Jules writes that sends HTTP requests MUST call scope check first:
```python
if not self.scope.is_in_scope(endpoint.url):
    self.logger.warning(
        "probe_blocked_out_of_scope",
        url=endpoint.url,
    )
    return ScopeViolationResult(url=endpoint.url)
```

Jules must NEVER write code that bypasses or conditionally skips scope check.

### 4.3 Rate Limiting is Required — Not Optional

Every HTTP execution path must check rate limiter before sending.
The rate limiter is in prism/http/rate_limiter.py.
All probes go through it. No exceptions.

### 4.4 No Hardcoded Credentials

Jules must never write code that hardcodes:
  - API keys or tokens
  - Passwords or secrets
  - URLs that look like real targets
  - IP addresses that look like real infrastructure

Test credentials use the pattern: "test_token_abc123" or environment vars.

---

## SECTION 5 — PROJECT STRUCTURE

Jules must maintain this exact structure.
Never create files outside this structure without explicit instruction.
prism/
init.py
constants.py          # All constants — no magic numbers elsewhere
exceptions.py         # All custom exception classes
types.py              # Type aliases used across modules
interfaces/           # Protocol classes (interfaces)
http.py
mapper.py
statemachine.py
synthesis.py
reporting.py
models/               # Pydantic data models (frozen)
principal.py
endpoint.py
authz.py
state.py
primitive.py
invariant.py
finding.py
config.py
db/                   # Database layer
engine.py
models.py           # SQLAlchemy ORM models
repository.py
migrations/
http/                 # HTTP execution engine
client.py
principal.py
request_builder.py
response.py
rate_limiter.py
storage.py
executor.py
replay.py
scope.py
ingestion/            # Target ingestion
openapi.py
swagger.py
postman.py
har.py
proxy.py
crawler.py
js_extractor.py
graphql.py
normalizer.py
mapper/               # Authorization topology mapping
prober.py
matrix.py
identifier.py
graph.py
inconsistency.py
classifier.py
ranker.py
statemachine/         # State machine inference
observer.py
detector.py
builder.py
lifecycle.py
idempotency.py
hypothesis.py
executor.py
analyzer.py
race/                 # Race condition detection
scorer.py
toctou.py
h2_attacker.py
timer.py
executor.py
analyzer.py
reporter.py
synthesis/            # Z3 primitive synthesis
primitive.py
graph.py
depositor.py
encoder.py
solver.py
interpreter.py
novel_detector.py
chain_builder.py
dialectic/            # Adversarial false-positive review
attacker.py
defender.py
debate.py
verdict.py
models.py
storage.py
classifier.py
reporting/            # Output and PoC generation
poc.py
cvss.py
cwe.py
terminal.py
html.py
json_reporter.py
markdown.py
h1_template.py
evidence.py
cli/                  # CLI entry points
main.py
scan.py
report.py
config.py
tests/
conftest.py
unit/
models/
http/
ingestion/
mapper/
statemachine/
race/
synthesis/
dialectic/
reporting/
integration/
test_full_scan.py
test_against_crapi.py
fixtures/
specs/              # Sample OpenAPI specs
responses/          # Sample HTTP responses
docs/
index.md
quickstart.md
architecture.md
research.md
engines/
contributing.md
pyproject.toml
AGENTS.md               # This file
README.md
Dockerfile
docker-compose.yml
.github/workflows/ci.yml

---

## SECTION 6 — JULES TASK PATTERNS AND ANTI-PATTERNS

### 6.1 What Jules Does Well — Use These Patterns

PATTERN 1 — IMPLEMENT ONE MODULE FROM ITS INTERFACE:
Best use of Jules. Give it a Protocol class (interface) and ask it to
implement the concrete class. The interface constrains what Jules can
generate. Output is predictable and reviewable.

PATTERN 2 — WRITE TESTS FOR EXISTING IMPLEMENTATION:
Give Jules an existing file and ask for tests only. Works excellently.
Always specify: "Tests go in tests/unit/[module]/test_[file].py"

PATTERN 3 — IMPLEMENT A DATA MODEL:
Give Jules field names, types, constraints, and validation rules.
Ask for a Pydantic model. Jules excels here.

PATTERN 4 — REFACTOR ONE FILE:
Give Jules one existing file and one specific refactoring goal.
Never ask Jules to refactor across multiple files in one task.

PATTERN 5 — ADD ERROR HANDLING TO EXISTING FILE:
Give Jules an existing file and ask it to add explicit error handling
to all external calls. Specify which exception types to handle.

### 6.2 What Jules Does Badly — Avoid These Patterns

ANTI-PATTERN 1 — "BUILD THE WHOLE THING":
Never give Jules an entire module to build in one task.
"Build prism/mapper/" will produce slop.
"Build prism/mapper/graph.py implementing the GraphMapper protocol" works.

ANTI-PATTERN 2 — CROSS-FILE CHANGES IN ONE TASK:
Never ask Jules to modify 5 files at once.
It loses coherence. The diff becomes impossible to review.
One file = one task. No exceptions.

ANTI-PATTERN 3 — AMBIGUOUS REQUIREMENTS:
"Add security to the probe function" will produce random security theater.
"Add explicit scope enforcement check before line 47 of executor.py,
returning ScopeViolationResult if scope.is_in_scope() returns False" works.

ANTI-PATTERN 4 — NO TEST REQUIREMENT IN PROMPT:
If the prompt doesn't say "include tests", Jules may skip them.
Always explicitly state: "Include tests in tests/unit/[module]/test_[file].py"

ANTI-PATTERN 5 — ASKING JULES TO DESIGN ARCHITECTURE:
Jules follows architecture. It does not design it.
Architecture decisions are made in this AGENTS.md file and the
prism/interfaces/ Protocol files, never by Jules itself.

---

## SECTION 7 — PHASE TRACKING

The project builds in phases. Each phase must be fully complete
(all files merged, all tests green) before the next phase starts.

Current phase: Track in PHASE_STATUS.md (Jules updates this)
PHASE 1: Core Data Model + CLI Skeleton
Status: [ ] NOT STARTED
Files:  prism/models/principal.py
prism/models/endpoint.py
prism/models/authz.py
prism/models/state.py
prism/models/primitive.py
prism/models/invariant.py
prism/models/finding.py
prism/models/config.py
prism/exceptions.py
prism/types.py
prism/constants.py
prism/db/engine.py
prism/db/models.py
prism/db/repository.py
prism/cli/main.py
prism/cli/scan.py
prism/cli/report.py
prism/cli/config.py
PHASE 2: Target Ingestion Engine
Status: [ ] BLOCKED ON PHASE 1
Files:  prism/ingestion/openapi.py
prism/ingestion/swagger.py
prism/ingestion/postman.py
prism/ingestion/har.py
prism/ingestion/proxy.py
prism/ingestion/crawler.py
prism/ingestion/js_extractor.py
prism/ingestion/graphql.py
prism/ingestion/normalizer.py
[... phases 3-10 listed same format ...]

Jules must:
  1. Check PHASE_STATUS.md before starting any task
  2. Refuse to implement a file from Phase N+1 if Phase N is incomplete
  3. Update PHASE_STATUS.md when it completes a file (mark ✓ DONE)
  4. Mark ✗ BLOCKED with reason if a dependency is missing

---

## SECTION 8 — INTERFACE CONTRACTS

### 8.1 The Most Important File: prism/interfaces/

Every engine in PRISM has a Protocol interface.
Jules implements the Protocol. Never changes the Protocol.
If the Protocol needs changing: create a new PR to discuss, not silently modify.

### 8.2 Key Interfaces Jules Must Know
```python
# prism/interfaces/http.py

class IHTTPExecutor(Protocol):
    """Executes HTTP probes against authorized targets."""

    async def probe(
        self,
        endpoint: Endpoint,
        principal: Principal,
    ) -> AuthzDecision:
        """Send one probe. Return one decision. No side effects."""
        ...

    async def probe_concurrent(
        self,
        endpoint: Endpoint,
        principal: Principal,
        count: int,
        interval_ms: float = 0,
    ) -> list[AuthzDecision]:
        """Send N concurrent probes for race condition testing."""
        ...

class IScopeGuard(Protocol):
    """Enforces scope boundaries. Safety-critical."""

    def is_in_scope(self, url: str) -> bool:
        """Return True only if URL is explicitly in-scope."""
        ...

    def add_scope(self, pattern: str) -> None:
        """Add a URL pattern to the in-scope list."""
        ...

# prism/interfaces/mapper.py

class IAuthzMapper(Protocol):
    """Maps authorization topology across endpoints and principals."""

    async def map_endpoint(
        self,
        endpoint: Endpoint,
        principals: list[Principal],
    ) -> EndpointAuthzProfile:
        """Probe endpoint with all principals. Return full profile."""
        ...

    def build_topology_graph(
        self,
        profiles: list[EndpointAuthzProfile],
    ) -> AuthzTopologyGraph:
        """Build NetworkX directed graph from profiles."""
        ...

    def find_inconsistencies(
        self,
        graph: AuthzTopologyGraph,
    ) -> list[AuthzInconsistency]:
        """Find authorization inconsistencies in the graph."""
        ...
```

### 8.3 Data Flow Rules

Data flows in ONE direction through the pipeline:
  Ingestion → HTTP Engine → Mapper → State Machine
           → Race Detector → Primitive Graph → Synthesis
           → Dialectic → Reporting

No module imports from a module to its RIGHT in this pipeline.
No circular imports. Ever.

Imports allowed:
  All modules → prism/models/, prism/types.py, prism/constants.py
  Mapper → prism/http/
  StateMachine → prism/http/
  Synthesis → prism/mapper/, prism/statemachine/, prism/race/
  Dialectic → prism/synthesis/
  Reporting → everything (read-only)

---

## SECTION 9 — HOW JULES HANDLES AMBIGUITY

### 9.1 When Jules Encounters an Ambiguous Requirement

Jules must NOT guess. Jules must NOT hallucinate a design decision.

Jules must:
  1. Complete whatever IS clear in the task
  2. Add a comment block in the code:
 # DESIGN DECISION NEEDED:
 # [describe the ambiguity]
 # Option A: [describe]
 # Option B: [describe]
 # Defaulting to Option A pending clarification.
  3. Add a PR comment: "Ambiguity found in [section]. 
     Implemented Option A. See inline comment line [N]. 
     Please confirm or redirect."

### 9.2 When a Dependency Is Missing

If Jules needs a file that doesn't exist yet (e.g., it needs to import
from prism/interfaces/http.py but that file hasn't been created):

Jules must:
  1. Create a minimal stub of the dependency in the same PR
  2. Mark it clearly: # STUB — replace with full implementation
  3. PR comment: "Created stub for [file] — full implementation needed."

Jules must NOT invent the full implementation of the missing dependency.
Only stubs. The stub contains just enough to make the current file compile.

### 9.3 When Tests Fail in Jules' VM

Jules runs tests in its cloud VM before submitting the PR.
If tests fail:
  1. Jules attempts to fix the failure (up to 3 attempts)
  2. If still failing after 3 attempts:
     Jules submits the PR anyway but prefixes the title: "[WIP] "
     Jules adds a PR comment: "Tests failing on: [test names]
     Root cause: [diagnosis]
     Blocked on: [what needs to change]"
  3. Jules never submits a PR claiming tests pass when they don't

---

## SECTION 10 — PR STANDARDS

### 10.1 PR Title Format
[PHASE N] prism/[module]/[file].py: [what this does]
Examples:
[PHASE 1] prism/models/endpoint.py: Endpoint and Parameter data models
[PHASE 3] prism/http/executor.py: Async parallel probe execution engine
[PHASE 4] prism/mapper/graph.py: NetworkX authorization topology graph

### 10.2 PR Body Template

Jules must fill this template for every PR:
```markdown
## What this implements

[One paragraph. What does this file do? Why does it exist?]

## Interface it satisfies

[Which Protocol class does this implement? Or: N/A for models/utilities]

## Design decisions

[Any non-obvious choices Jules made. Why this approach over alternatives.]

## Test coverage

[What tests were written. What edge cases are covered.]

## Dependencies added

[Any new packages added to pyproject.toml. Why each is needed.]

## Ambiguities or stubs

[Any design decision comments or stubs Jules created. Human input needed.]

## Phase status update

[Which PHASE_STATUS.md entries Jules updated to ✓ DONE]
```

### 10.3 What Jules Must NOT Do in PRs

- Never modify AGENTS.md (this file)
- Never modify prism/interfaces/ Protocol classes
- Never change pyproject.toml without documenting why in PR body
- Never force-push to main
- Never merge its own PR
- Never modify existing tests without explicit instruction

---

## SECTION 11 — FALLBACK PROTOCOLS

### 11.1 If Jules Produces More Than 400 Lines

Reviewer rejects the PR with comment: "Split required per AGENTS.md §1.1"
Jules splits the file and resubmits as two PRs.

### 11.2 If Jules Imports a Disallowed Package

CI will catch this via: `pip check` + import auditing in GitHub Actions.
Reviewer rejects with: "Disallowed package per AGENTS.md §1.3"
Jules removes the import and finds an alternative from the approved list.

### 11.3 If Jules Breaks an Interface

If Jules changes a function signature in prism/interfaces/:
CI catches this via interface compliance tests in tests/unit/interfaces/.
Reviewer rejects: "Interface modification not permitted per AGENTS.md §9.3"
Jules reverts the interface change and implements within the existing contract.

### 11.4 If Jules Skips Tests

PR will show: tests/unit/[module]/test_[file].py missing.
Reviewer comments: "Tests required per AGENTS.md §3.1"
Jules adds tests as a follow-up PR on the same branch before merge.

### 11.5 If Jules Confuses Phases

If Jules implements a Phase 4 file while Phase 2 is incomplete:
Reviewer comments: "Phase ordering violation per AGENTS.md §7"
Jules opens a new PR targeting the correct phase file instead.

---

## SECTION 12 — THE CRITIC INTEGRATION

Jules has a built-in critic that reviews code before submission.
The critic is most effective when Jules provides it specific criteria.

In the task description, always include:
Critic checklist for this file:

All public functions have complete type hints
All public functions have Google-style docstrings
All external calls have explicit exception handling
Scope check is present before any HTTP request
No bare except clauses
No magic numbers (use prism/constants.py)
No logging of token values (use token[:8] + "...")
Tests cover happy path, error path, and boundary cases


This gives the critic specific criteria to flag, producing higher-quality
output before the PR even reaches human review.

---

## SECTION 13 — MEMORY SETTINGS FOR JULES

Jules has memory for user preferences. These must be set on first use:
Preferences to set in Jules memory:

"Always include tests in the same PR as implementation"
"Always use structured logging with keyword arguments"
"Never use bare except clauses"
"Always check scope before HTTP requests"
"Maximum 400 lines per file"
"Project is PRISM security framework — output quality is safety-critical"
"Use Python 3.11+ syntax (str | None, list[str], etc.)"
"Always update PHASE_STATUS.md when completing a file"


---

## SECTION 14 — QUICK REFERENCE FOR TASK CONSTRUCTION

When assigning Jules a task, use this template:
BUILD: prism/[module]/[file].py
PHASE: [N]
IMPLEMENTS: [Protocol class name from prism/interfaces/]
DEPENDS ON: [list existing files this imports from]
WHAT IT DOES:
[2-3 sentences. What is this file's responsibility?]
FUNCTION SIGNATURES REQUIRED:
[list each function with exact signature]
BUSINESS RULES:
[list any invariants or constraints the code must enforce]
EDGE CASES TO HANDLE:
[list specific error conditions]
TESTS REQUIRED: tests/unit/[module]/test_[file].py
TEST SCENARIOS:
[list the specific scenarios to test]
CRITIC CHECKLIST:

All public functions have complete type hints
All public functions have Google-style docstrings
All external calls have explicit exception handling
[add file-specific items]


This template, combined with AGENTS.md, gives Jules everything it needs
to produce production-quality output on the first attempt.

---

## SECTION 15 — WHAT "DONE" MEANS FOR PRISM

A file is DONE when:
  ✓ Implements its Protocol interface completely
  ✓ All functions have type hints
  ✓ All public functions have Google-style docstrings
  ✓ All external calls have explicit error handling
  ✓ structlog used for all logging
  ✓ No magic numbers (uses prism/constants.py)
  ✓ No token values logged
  ✓ Scope check present in all HTTP-sending code
  ✓ Tests written with 80%+ coverage
  ✓ Tests use respx mocking (no real HTTP)
  ✓ Tests cover happy path, errors, boundaries
  ✓ CI passes (mypy, ruff, pytest all green)
  ✓ PHASE_STATUS.md updated
  ✓ PR body filled with template

A file is NOT done if ANY of the above is missing.
Jules marks incomplete files with [WIP] prefix and inline comments.
