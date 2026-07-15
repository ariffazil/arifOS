---
atlas_class: 400
tier: core33
source_type: spec
authority: official
why_in_kernel: "Observability substrate: traces, metrics, logs. arifOS chains through arifOS-NATS-heartbeat, A-FORGE heartbeat, GEOX heartbeat, plus Netdata/Grafana/Prometheus/Cadvisor. The federation's telemetry is OTel-shaped."
freshness_policy: release-tracked
paradox_zone: "VI-SYSTEM"
scar_link: []
vault_anchor: null
---

# OpenTelemetry (OTel)

**Citation:** OpenTelemetry project (CNCF). *OpenTelemetry Specification*. https://opentelemetry.io

**Components:** API, SDK, semantic conventions, exporters (OTLP), collectors, auto-instrumentation libraries for many languages.

## Why in kernel

OpenTelemetry is the **observability spine** of the federation. arifOS organs expose heartbeat services that emit OTel-shaped telemetry; A-FORGE aggregates; Netdata/Grafana/Prometheus visualize.

For ATLAS333:

1. **Trace propagation** — when an agent reads `arifos://atlas333/paradox/1`, the call gets a `trace_id` and `span_id`; if the call triggers a paradox_gate check, the gate's span becomes a child of the resource read span. End-to-end visibility.
2. **Metrics** — ATLAS333 resource read counts, latency histograms, error rates. Surface on Grafana.
3. **Logs** — every resource read produces a structured log: `{trace_id, span_id, uri, actor_id, session_id, verdict}`. Compatible with VAULT999 audit chain.
4. **Semantic conventions** — OTel defines `gen_ai.*` attributes for LLM/agent calls. ATLAS333 resources should declare themselves via these conventions so cross-vendor tooling works.

## ATLAS333 activation

- **Zone:** VI — SYSTEM
- **Floors:** F2 (deterministic spans), F4 (clarity), F11 (audit trail)
- **Quote sites:** J1–J5

## How to use

When a federation call goes wrong, OTel traces let you walk the call graph: MCP request → resource read → paradox gate → verdict. When measuring federation health, OTel metrics expose latency p99s and error rates.

When a paradox between **observability and execution** appears (Zone VI), invoke OTel — it provides the visibility without altering the call semantics.

## Pair with

- `01-mcp-spec.md` — MCP calls are OTel-instrumented by convention
- `04-json-rpc-2.md` — JSON-RPC envelopes can carry trace context via headers
- `core/shared/ATLAS333_BRIDGE.md` — federated org map

## Cross-references

- `arifOS/arifosmcp/runtime/fiqh_of_floors.py` — emits structured telemetry for F-floor events
- `arifOS-NATS-heartbeat.service` — runs OTel exporter
- `membrane-jaeger` (Docker) — Jaeger UI for trace visualization (port 16686)
- `grafana-server.service` + `prometheus.service` — metrics dashboards

## Scar links

_None yet._

## Vault anchor

_None yet._