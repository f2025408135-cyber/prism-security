#!/usr/bin/env python3
"""CI gate: fail if any prism/ file exceeds 400 lines."""

import sys
from pathlib import Path

MAX_LINES = 400
VIOLATIONS = []

for path in Path("prism").rglob("*.py"):
    lines = path.read_text().count("\n")
    if lines > MAX_LINES:
        VIOLATIONS.append(f"{path}: {lines} lines (max {MAX_LINES})")

if VIOLATIONS:
    print("FILE SIZE GATE FAILED — per AGENTS.md §1.1:")
    for v in VIOLATIONS:
        print(f"  ✗ {v}")
    sys.exit(1)

print(f"✓ All files within {MAX_LINES} line limit")
