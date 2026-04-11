FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install poetry or pip requirements
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Copy source code
COPY . .

# Set up volume for workspace
VOLUME ["/app/.prism"]

# Default entrypoint
ENTRYPOINT ["python", "-m", "prism.cli.main"]
CMD ["--help"]
