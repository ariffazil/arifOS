---
sidebar_position: 2
title: Installation
description: Detailed installation options for arifOS
---

# Installation

## From PyPI (Recommended)

```bash
pip install arifos
```

### With Development Tools

```bash
pip install arifos[dev]
```

### All Dependencies

```bash
pip install arifos[all]
```

---

## From Source

```bash
# Clone the repository
git clone https://github.com/ariffazil/arifOS.git
cd arifOS

# Install in development mode
pip install -e .

# Or with dev tools
pip install -e ".[dev]"
```

---

## Requirements

- **Python:** 3.10+
- **Dependencies:** numpy, pydantic, anyio, starlette, fastmcp

---

## Running the Server

### Stdio Mode (Local Clients)

For Claude Desktop, Cursor, and other local MCP clients:

```bash
python -m arifos.mcp
```

### SSE Mode (Remote Connections)

For remote connections or self-hosting:

```bash
python -m arifos.mcp sse
```

Default port: `8000` (configurable via `PORT` environment variable)

---

## Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY . .
RUN pip install -e .

EXPOSE 8000
CMD ["python", "-m", "arifos.mcp", "sse"]
```

```bash
docker build -t arifos .
docker run -p 8000:8000 arifos
```

---

## Verify Installation

```bash
# Check version
python -c "import arifos; print(arifos.__version__)"

# Run health check
curl http://localhost:8000/health
```
