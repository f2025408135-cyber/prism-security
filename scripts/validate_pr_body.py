#!/usr/bin/env python3
"""CI gate: Checks that PR body contains required sections.

Enforces AGENTS.md §10.2 Template.
"""

import sys
import os

REQUIRED_SECTIONS = [
    "What this implements",
    "Interface it satisfies",
    "Design decisions",
    "Test coverage",
    "Dependencies added",
    "Ambiguities or stubs",
    "Phase status update"
]

def main() -> None:
    # In a real GitHub action, the PR body is provided via environment variable
    # e.g., GITHUB_EVENT_PATH containing a JSON payload with pull_request.body
    
    pr_body = os.environ.get("PR_BODY", "")
    
    # If run locally without PR_BODY, we just exit 0 to allow standard local pushes
    if not pr_body:
        print("✓ PR body validation skipped (no PR_BODY env var provided)")
        sys.exit(0)

    pr_body_lower = pr_body.lower()
    missing_sections = []

    for section in REQUIRED_SECTIONS:
        # Check if the header exists (e.g. "## What this implements")
        if section.lower() not in pr_body_lower:
            missing_sections.append(section)

    if missing_sections:
        print("PR BODY VALIDATION FAILED — Missing required sections per AGENTS.md §10.2:")
        for missing in missing_sections:
            print(f"  ✗ ## {missing}")
        sys.exit(1)

    print("✓ PR body validation passed")
    sys.exit(0)

if __name__ == "__main__":
    main()
