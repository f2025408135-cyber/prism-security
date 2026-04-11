#!/usr/bin/env bash

# PRISM CLI wrapper
# Makes it easy to run `prism scan ...` directly from the repo root

python -m prism.cli.main "$@"
