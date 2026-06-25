---
name: arifOS-Langfuse
description: Instrument arifOS constitutional AI kernel with Langfuse LLM tracing. Use when (1) adding Langfuse tracing to arifOS tool calls, (2) wiring arifOS telemetry to Langfuse cloud or self-hosted, (3) querying arifOS trace data from Langfuse, (4) migrating arifOS mind_reason/heart_critique calls to Langfuse spans. DITEMPA BUKAN DIBERI — Forged, Not Given.
---

# arifOS-Langfuse Skill

Instrument arifOS constitutional AI operations with Langfuse LLM tracing.

## Architecture

```
arifOS Kernel (Python)
  └── arifosmcp/runtime/telemetry.py  ← Telemetry wrapper
        ├── Prometheus metrics (counters, histograms)
        └── Langfuse v3 span tracing  ← HERE
              ├── context manager: with lf.start_as_current_observation() as span
              ├── span.update(input={...}, output={...})
              └── lf.flush()
```

arifOS uses Langfuse Python SDK v3 with **context manager pattern** — spans auto-close on exit.

## Credentials

arifOS → Langfuse (cloud Japan):

```bash
export LANGFUSE_PUBLIC_KEY=pk-lf-YOUR_PUBLIC_KEY
export LANGFUSE_SECRET_KEY=sk-lf-YOUR_SECRET_KEY
export LANGFUSE_HOST=https://jp.cloud.langfuse.com
```

arifOS → Langfuse (self-hosted on VPS):

```bash
export LANGFUSE_HOST=http://langfuse-web:3000
# same keys
```

## Key Patterns

### Correct span creation (v3 context manager)

```python
from langfuse import Langfuse

lf = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "https://jp.cloud.langfuse.com")
)

# WRONG — detached span, no active context
lf.start_as_current_observation(as_type="span", name="arifOS::tool-name")
lf.update_current_span(...)

# CORRECT — context manager, span auto-closes
with lf.start_as_current_observation(as_type="span", name="arifOS::tool-name", metadata={...}) as span:
    span.update(input={"tool": tool_name, "actor": actor_id}, output={"verdict": verdict, ...})
```

### Tool call tracing in arifOS

In `arifosmcp/runtime/telemetry.py`, `record_tool_call()` method:

```python
with self._lf.start_as_current_observation(
    as_type="span",
    name=f"arifOS::{tool}",
    metadata=_redact(span_meta),
) as span:
    span.update(input={"tool": tool, "actor": actor_id}, output={"verdict": verdict, ...})
```

After `flush()` the span appears in Langfuse dashboard under the project.

### Environment setup in arifOS container

```bash
# Install SDK
pip install langfuse

# In .env (not hardcoded — use env vars)
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://jp.cloud.langfuse.com
# or for self-hosted:
# LANGFUSE_HOST=http://langfuse-web:3000
```

## arifOS Tracing Scope

| Tool | Traced | Priority |
|-----|--------|----------|
| arif_judge_deliberate | ✅ active | P0 |
| arif_mind_reason | ⚠️ pilot | P1 |
| arif_heart_critique | ⚠️ pilot | P1 |
| arif_session_init | 🔜 next | P2 |
| Others | ❌ not wired | — |

## Workflows

### 1. Verify arifOS Langfuse wiring

```bash
# From inside arifOS container:
docker exec arifosmcp python3 -c "
from arifosmcp.runtime.telemetry import get_telemetry
t = get_telemetry()
print('Langfuse active:', t._lf is not None)
t.record_tool_call(tool='arif_judge_deliberate', verdict='SEAL', latency=0.15,
                  session_id='test', actor_id='arif', metadata={'test': True})
t.flush()
print('Trace sent — check Langfuse dashboard')
"
```

### 2. Wire a new tool to Langfuse

1. Find the tool handler in `arifosmcp/runtime/tools.py`
2. Add `trace_tool_call()` from telemetry after successful execution
3. Instrument input_hash / output_hash (redacted) + metadata dict
4. Test: send live call, check Langfuse dashboard

### 3. Inspect traces via API

```bash
export LANGFUSE_PUBLIC_KEY=pk-lf-YOUR_PUBLIC_KEY
export LANGFUSE_SECRET_KEY=sk-lf-YOUR_SECRET_KEY
export LANGFUSE_HOST=https://jp.cloud.langfuse.com

# List recent traces
curl -s "$LANGFUSE_HOST/api/public/traces?limit=10" \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" | python3 -m json.tool

# Get specific trace
curl -s "$LANGFUSE_HOST/api/public/traces/<trace-id>" \
  -u "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY"
```

### 4. Add scoring to traces

```python
lf.score_current_trace(name="arifOS-verdict", value=1.0 if verdict == "SEAL" else 0.0)
```

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ModuleNotFoundError: No module named 'langfuse'` | `pip install langfuse` in container |
| `AttributeError: 'Langfuse' object has no attribute 'trace'` | Use v3 context manager pattern, not `.trace()` |
| `Context error: No active span` | Wrap with `with lf.start_as_current_observation() as span:` |
| `401 Unauthorized` | Check API keys are correct + LANGFUSE_HOST matches region |
| Traces not appearing after flush | Check LANGFUSE_HOST network access from container |
| `langfuse-web` returns 404 | Self-hosted needs `/api/public/` path prefix |

## Documentation

- Langfuse Docs: https://langfuse.com/docs
- arifOS Observatory (public): https://arifos.arif-fazil.com/observatory/
- arifOS Langfuse tracing status: Langfuse cloud (jp region) — partial, pilot stage

## References

- Full Langfuse instrumentation guide: https://langfuse.com/docs/observability/sdk/instrumentation
- Python SDK v3: https://langfuse.com/docs/sdk/python/sdk-v3
- CLI: https://langfuse.com/docs/api-and-data-platform/features/agent-skill
