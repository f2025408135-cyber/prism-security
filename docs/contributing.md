# Contributing to PRISM

We welcome contributions from security researchers and developers!

## The AGENTS.md Contract

If you are developing for PRISM, you **must** adhere strictly to the rules defined in the root `AGENTS.md` file. PRISM is a production-grade tool, meaning we enforce strict formatting and architecture boundaries.

1. **Immutability**: All Pydantic models must use `model_config = ConfigDict(frozen=True)`.
2. **Typing**: Python 3.11+ union typing (`str | None`) is required everywhere. No bare `Any` allowed without documented comments.
3. **No Magic Numbers**: All constants must go in `prism/constants.py`.
4. **Testing**: You must write tests using `respx` for mock HTTP responses. PRISM engines must never hit real networks during test suites.
5. **File Size Limits**: No module may exceed 400 lines of code.

### Pull Requests
Ensure you run the pre-commit checks locally before submitting a PR:
```bash
pytest tests/ --cov=prism
mypy prism/ --strict
ruff check prism/
```
