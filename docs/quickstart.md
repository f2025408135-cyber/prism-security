# Quickstart Guide

Get up and running with PRISM in minutes.

## Prerequisites

- Python 3.11+
- Katana (ProjectDiscovery) installed in your PATH (for active crawling)
- Docker (optional, but recommended)

## Installation

### Via Docker

The easiest way to run PRISM without dependency conflicts is via Docker.

```bash
git clone https://github.com/f2025408135-cyber/prism-security.git
cd prism-security
docker-compose run --rm prism scan https://api.target.com
```

### Local Installation

For developers or researchers who want to modify engines:

```bash
git clone https://github.com/f2025408135-cyber/prism-security.git
cd prism-security
pip install -e ".[dev]"
```

## Running Your First Scan

1. Initialize your workspace:
```bash
prism config init --workspace-dir .my-target
```

2. Run a scan against a swagger spec:
```bash
prism scan start https://api.target.com --workspace-dir .my-target
```

3. Generate your report:
```bash
prism report generate --format html --output target_report.html
```
