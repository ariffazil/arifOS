# ACLIP_CAI Integration Documentation

## Overview

ACLIP_CAI (arifOS Console Intelligence & Perception Console) is the **9-Sense Nervous System** that provides infrastructure observability for arifOS. It integrates with the aaa-mcp 9-law constitutional pipeline as the sensory layer.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    aaa-mcp 9-Law Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Law 1: INIT          → Session initialization                  │
│                                                                 │
│  Law 2: SENSE         → Intent classification                   │
│                                                                 │
│  Law 3: GROUND        → Evidence gathering                      │
│                       ├─▶ aclip_system_health                   │
│                       ├─▶ aclip_fs_inspect                      │
│                       └─▶ aclip_config_flags                    │
│                                                                 │
│  Law 4: THINK         → Hypothesis generation                   │
│                                                                 │
│  Law 5: SEARCH        → Information retrieval                   │
│                       ├─▶ aclip_chroma_query                    │
│                       └─▶ aclip_log_tail                        │
│                                                                 │
│  Law 6: EMPATHIZE     → Stakeholder impact                      │
│                                                                 │
│  Law 7: GUARD         → Action gating                           │
│                       └─▶ aclip_forge_guard ★                   │
│                                                                 │
│  Law 8: ALIGN         → Ethics reconciliation                   │
│                                                                 │
│  Law 9: VERDICT       → Final judgment                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## The 9 Tools

| Tool | Purpose | Pipeline Stage |
|------|---------|----------------|
| `aclip_system_health` | CPU, memory, disk, load metrics | Law 3 (Ground) |
| `aclip_process_list` | Process inspection and filtering | Diagnostics |
| `aclip_fs_inspect` | Filesystem traversal and analysis | Law 3 (Ground) |
| `aclip_log_tail` | Log file monitoring and search | Law 5 (Search) |
| `aclip_net_status` | Network connectivity and diagnostics | Diagnostics |
| `aclip_config_flags` | Configuration validation | Law 3 (Ground) |
| `aclip_chroma_query` | Vector DB semantic search | Law 5 (Search) |
| `aclip_cost_estimator` | Resource usage and cost projection | Planning |
| `aclip_forge_guard` | Gating decisions | Law 7 (Guard) |

## Key Characteristics

- **Console-only**: No ethics/ASI layer in tools
- **Read-only**: 8 of 9 tools are strictly read-only
- **Fast**: < 100ms target response time
- **Structured**: JSON output with consistent schema
- **Integrated**: Registered as MCP tools with `aclip_` prefix

## MCP Registration

ACLIP_CAI tools are automatically registered with the aaa-mcp server:

```python
# In aaa_mcp/server.py
from aclip_cai.mcp_bridge import register_aclip_tools

# Register all 9 tools
register_aclip_tools(mcp)
```

## Usage Examples

### CLI

```bash
# System health
aclip-cai health

# Process inspection
aclip-cai processes --filter python --limit 20

# Filesystem inspection
aclip-cai fs --path /root/arifOS --pattern "*.py"

# Log tailing
aclip-cai logs --path /var/log/syslog --grep "error"

# Forge guard
aclip-cai guard --action deploy --target /app --risk medium
```

### Python API

```python
from aclip_cai import system_health, forge_guard

# Health check
health = await system_health()
print(health.data['cpu']['load_1m'])

# Forge guard
verdict = await forge_guard(
    action="deploy",
    target="/app/production",
    session_id="sess-123",
    risk_level="medium",
    dry_run=True
)
print(verdict.data['verdict'])  # SEAL, SABAR, PARTIAL, VOID, 888_HOLD
```

### MCP Tool Call

```json
{
  "name": "aclip_system_health",
  "arguments": {
    "include_swap": true,
    "include_io": false
  }
}
```

## Forge Guard

The only non-read tool. Provides gating decisions for system modifications:

- **Verdicts**: SEAL (approved), SABAR (repair needed), PARTIAL (warning), VOID (blocked), 888_HOLD (human required)
- **Constitutional Floors**: F1, F7, F11
- **Danger Detection**: Blocks rm -rf /, mkfs, fork bombs, etc.

## Integration with 9-Law Pipeline

### Law 3: Ground

When the pipeline needs evidence about system state:

```python
# Evidence gathering stage
health = await aclip_system_health()
config = await aclip_config_flags(config_path="/app/config.yaml")
fs_state = await aclip_fs_inspect(path="/app/data")

# Store as evidence for tri-witness
evidence.append({
    "type": "system_grounding",
    "health": health.data,
    "config": config.data,
    "fs": fs_state.data
})
```

### Law 5: Search

When the pipeline needs to search logs or vector DB:

```python
# Semantic search
results = await aclip_chroma_query(
    query_text="constitutional AI safety",
    collection_name="docs",
    n_results=5
)

# Log investigation
logs = await aclip_log_tail(
    log_path="/var/log/app.log",
    lines=100,
    grep_pattern="ERROR|CRITICAL"
)
```

### Law 7: Guard

Before executing any action that modifies state:

```python
# Gate the action
gate = await aclip_forge_guard(
    action="deploy",
    target="/production/app",
    session_id=session_id,
    risk_level="high",
    justification="Security patch deployment",
    dry_run=dry_run
)

if gate.data['verdict'] != 'SEAL':
    return {'verdict': gate.data['verdict'], 'hold': True}
```

## Testing

```bash
# Run all ACLIP_CAI tests
pytest tests/aclip_cai/ -v

# Specific tool tests
pytest tests/aclip_cai/test_console_tools.py::test_system_health_basic -v

# MCP bridge tests
pytest tests/aclip_cai/test_mcp_bridge.py -v
```

## Directory Structure

```
aclip_cai/
├── __init__.py          # Package exports
├── __main__.py          # Module entry point
├── cli.py               # Command-line interface
├── console_tools.py     # 9 tool implementations
├── mcp_bridge.py        # MCP registration
└── README.md            # Full documentation
```

## References

- [ACLIP_CAI README](/root/arifOS/aclip_cai/README.md)
- [aaa-mcp Server](/root/arifOS/aaa_mcp/server.py)
- [Constitutional Floors](/root/arifOS/000_THEORY/CONSTITUTION.md)
