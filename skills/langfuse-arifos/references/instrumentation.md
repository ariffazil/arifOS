# arifOS + Langfuse Instrumentation Reference

## Current State

arifOS has Langfuse SDK wired in `arifosmcp/runtime/telemetry.py`.
Currently tracing: `arif_judge_deliberate` only (pilot).

## Telemetry Module Architecture

```python
# arifosmcp/runtime/telemetry.py
class Telemetry:
    def _init(self):
        self._lf = _get_langfuse()  # returns Langfuse client or None

    def record_tool_call(self, tool, verdict, latency, ...):
        if self._lf:
            with self._lf.start_as_current_observation(
                as_type="span",
                name=f"arifOS::{tool}",
                metadata={...}
            ) as span:
                span.update(input={...}, output={...})
        # Prometheus counters update here too

def get_telemetry() -> Telemetry:
    # singleton pattern
```

## Adding Tracing to Another Tool

### Option A: Via trace_tool_call() (recommended)

After tool execution in `tools.py`:

```python
from arifosmcp.runtime.telemetry import trace_tool_call

async def arif_mind_reason(...):
    result = await _run_reasoning(...)
    trace_tool_call(
        tool_name="arif_mind_reason",
        arguments={"mode": mode, "query": query},
        result=result,
        session_id=session_id,
        actor_id=actor_id,
        latency_ms=elapsed * 1000
    )
    return result
```

### Option B: Direct span in tool handler

```python
from arifosmcp.runtime.telemetry import get_telemetry

async def arif_mind_reason(**kwargs):
    t = get_telemetry()
    with t._lf.start_as_current_observation(
        as_type="span",
        name="arifOS::arif_mind_reason",
        metadata={"mode": kwargs.get("mode"), "actor": kwargs.get("actor_id")}
    ) as span:
        # ... tool logic ...
        span.update(
            input={"query": kwargs.get("query")},
            output={"verdict": result.get("verdict"), "decision": result.get("decision_packet")}
        )
    return result
```

## Langfuse API Quick Reference

```bash
# List traces
GET /api/public/traces?limit=20

# Trace detail
GET /api/public/traces/{trace_id}

# Spans for a trace
GET /api/public/traces/{trace_id}/observations

# Create score on trace
POST /api/public/scores
{
  "trace_id": "...",
  "name": "verdict_score",
  "value": 1.0,
  "comment": "SEAL — all floors passed"
}
```

## arifOS Span Naming Convention

```
arifOS::arif_session_init
arifOS::arif_sense_observe
arifOS::arif_evidence_fetch
arifOS::arif_mind_reason
arifOS::arif_kernel_route
arifOS::arif_reply_compose
arifOS::arif_memory_recall
arifOS::arif_heart_critique
arifOS::arif_gateway_connect
arifOS::arif_ops_measure
arifOS::arif_judge_deliberate  ← currently traced
arifOS::arif_forge_execute
arifOS::arif_vault_seal
```

## Redaction — What Goes Into Spans

Input metadata (redacted by `_redact()`):
- tool name
- actor_id
- session_id
- input_hash (not raw content)
- delta_S, latency_ms

Output metadata:
- verdict (SEAL/HOLD/VOID)
- output_hash
- reasons[] (if HOLD)
- next_safe_action (if HOLD)
- vault_receipt (if SEAL)

What is NEVER in spans:
- raw prompts or responses
- API keys or secrets
- personal operator data
- full session content
