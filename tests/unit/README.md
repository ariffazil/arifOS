# Unit Tests

**Scope:** API Layer, Memory Layer, MCP Server
**Target:** FastAPI, L7 Memory, Server Operations

This directory contains **unit tests** for individual components isolated from the full system.

---

## Test Files

| File | Description |
|------|-------------|
| `test_api_app.py` | FastAPI application endpoints and routing |
| `test_l7_memory.py` | L7 memory layer operations |
| `test_mcp_server.py` | MCP server unit operations |

---

## Key Concepts

### API Layer (FastAPI)
Tests for HTTP interface:
- Endpoint routing
- Request/response validation
- Error handling
- Health checks

### L7 Memory
Seventh layer of memory hierarchy:
- Session-specific memory
- Query context
- Working memory for current task

### MCP Server
Model Context Protocol server:
- Tool registration
- Request handling
- Response formatting
- Connection management

---

## Running Tests

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run API tests
pytest tests/unit/test_api_app.py -v

# Run memory tests
pytest tests/unit/test_l7_memory.py -v

# Run MCP server tests
pytest tests/unit/test_mcp_server.py -v
```

---

## Test Markers

```bash
# Run unit tests by marker
pytest -m unit
```

---

**Constitutional Floor:** N/A (Unit level - no floor enforcement)
**DITEMPA BUKAN DIBERI**
