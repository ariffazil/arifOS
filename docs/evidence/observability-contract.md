# Observability Contract — arifOS Federation

## Current State (2026-09-16)

### What Exists
- **Sovereign Postgres**: observability.observations table (201,495 rows)
- **arifFlow**: :7073 — FQ vector, receipt gravity well, 7 dimensions
- **FRAME**: :18085 — Independent observer, 7 chambers, drift detection
- **Kabarkan**: NATS JetStream + Postgres worker + Grafana (202k rows)
- **OTel Collector**: :4318 — otelcol-contrib elevated as single OTLP gateway
- **Prometheus**: tool_calls_total, floor_breaches, latency, sessions, ledger_size
- **Experience Traces**: forge_experience_query — self/env/constitutional feedback
- **World Model**: forge_wm_stats — surprise/entropy/gap per tool

### What Was Broken (Fixed 2026-09-16)
- **P0-A**: /telemetry/log returned 404 — silently lost all telemetry forwarding → FIXED: redirected to /ingest
- **P0-C**: OBSERVABILITY_BACKEND defaulted to dead Langfuse → FIXED: changed to dual

### What Still Needs Wiring
- **P0-B**: trace_id = fresh UUID per row (0% correlation) → FIX IN PROGRESS
- **G-03**: Verdict grammar pollution (12 values, 23.9% valid)
- **G-09**: Zero consumers of observability table
- **G-05**: FQ vector never reaches Kabarkan

## Evidence Thresholds

| Claim | Minimum Proof |
|---|---|
| "Sovereign telemetry operational" | Postgres receiving correlated traces |
| "Distributed tracing operational" | parent_span_id > 0% across sinks |
| "Observability independently verified" | External clean-room trace reproduction |
| "Production observability" | 30-day continuous operation + SLOs met |

## SLOs (Initial Targets)

| SLO | Target | Rationale |
|---|---|---|
| Receipt persistence | ≥99.9% | Governance evidence must survive |
| Trace correlation | ≥99% | Causal reconstruction required |
| P95 latency | ≤500ms | No governance-path drag |
| Sensitive field leakage | 0 | Non-negotiable |
| Degraded alert time | <5min | No silent darkness |
