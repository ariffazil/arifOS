# Observability Spans

Use this reference when instrumenting traces across the federation.

## Span taxonomy (OTel-aligned)

These span names are canonical for arifOS federation telemetry. They map to the OpenTelemetry GenAI/MCP semantic conventions where applicable.

| Span name | When to emit | Attributes |
|---|---|---|
| `run` | Top-level request / session | `actor_id`, `session_id`, `organ`, `trace_id` |
| `policy.decision` | Policy evaluation (floor check, risk classifier) | `policy_version`, `floors_checked`, `verdict` |
| `approval.request` | Durable approval object created | `approval_id`, `subject`, `action`, `scope` |
| `approval.resolve` | Approval granted/declined/modified | `resolver`, `resolution_status`, `resolution_reason` |
| `tool.list` | MCP tools/list call | `server_name`, `tool_count`, `filter_applied` |
| `tool.call` | Individual tool invocation | `tool_name`, `tool_class`, `risk_tier`, `duration_ms` |
| `resource.read` | MCP resource read | `resource_uri`, `mime_type`, `size_bytes` |
| `model.call` | LLM / model inference | `model_id`, `provider`, `input_tokens`, `output_tokens` |
| `handoff` | Agent-to-agent transfer | `source_agent`, `target_agent`, `handoff_reason` |
| `incident.trigger` | Kill switch, circuit break, degrade | `incident_type`, `trigger_floor`, `degraded_mode` |
| `audit.replay` | Evidence replay initiated | `run_id`, `replay_depth`, `evidence_sources` |

## Correlation

All spans MUST carry:
- `trace_id` — federation-wide trace
- `session_id` — governing session
- `actor_id` — who triggered the action
- `policy_version` — which policy bundle was active

## Evidence linkage

Span `event` annotations (not just attributes) SHOULD include:
- `verdict` at `policy.decision` end
- `approval_id` at `tool.call` start if approval was required
- `degraded_mode` at `incident.trigger` if mode changed

## Backward compatibility

Existing Prometheus metrics are preserved. OTel spans are additive. Do not replace existing metric surfaces; supplement them.
