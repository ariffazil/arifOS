# PREFECT_TELEMETRY_ROADMAP.md
## arifOS — Prefect Observability Stack

---

## Current State

- `prefect.yaml` exists at the repo root — defines flow deployment configuration.
- Telemetry is **batch file-based**: Prefect flow runs write logs to local files
  (or stdout buffering) which are then shipped asynchronously.
- No structured streaming sink is wired into the Prefect handler system.
- Observability output is essentially: stdout → log file → manual inspection or
  a cron-based file shipper.

```
[Flow Run] → stdout / file → log aggregate → (manual or batch shipper)
```

---

## Gap Analysis

### What exists
- `prefect.yaml` — deployment manifest (flows, work pools, schedules)
- File-based log buffering (default Prefect behavior)
- Basic Prefect Cloud / server connection (if `PREFECT_API_URL` is set)

### What is missing (streaming gap)

| Gap | Description | Severity |
|-----|-------------|----------|
| Structured JSON stdout | Prefect tasks emit unstructured text logs | High |
| Loki sink | No Grafana Loki integration for log aggregation | High |
| Vector / Grafana Agent | No vector.yaml or equivalent log pipeline | High |
| Prefect handler wiring | No custom Prefect handler that routes to Loki/Vector | Medium |
| Metrics sidecar | No Prometheus metrics emitted from flow runs | Medium |
| Trace propagation | No OpenTelemetry trace context across flows | Low |

---

## What's Needed

### 1. Structured JSON stdout from Prefect

Prefect flows/tasks should emit JSON lines instead of plain text.

```python
# In a base task or flow decorator wrapper
import logging
import json

class JSONLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = {
            "timestamp": record.created,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "flow_name": getattr(record, "flow_name", None),
            "task_name": getattr(record, "task_name", None),
        }
        print(json.dumps(log_entry))
```

Wire this into Prefect's logging config in `prefect.yaml` or a `logging.yml`.

### 2. Grafana Loki sink (or Vector → Loki)

**Option A — Direct Loki (Grafana Agent as sidecar):**
```yaml
# grafana-agent.yaml (per node)
logging:
  configs:
    - name: prefect
      scrape_interval: 10s
      clients:
        - url: http://loki:3100/loki/api/v1/push
      target:
        - job: prefect
          json:
            timestamp: timestamp
            level: level
            message: message
```

**Option B — Vector (more flexible):**
```toml
# vector.toml
[sources.prefect_logs]
  type = "file"
  include = ["/var/log/prefect/*.log"]

[sinks.loki]
  type = "loki"
  inputs = ["prefect_logs"]
  endpoint = "http://loki:3100"
  encoding.codec = "json"
```

### 3. Prefect Handler Wiring

Prefect's `visit_task` / `on_flow_run` hooks need to route to the structured logger:

```python
from prefect import flow, task
from prefect.logging.handlers import PrefectHandler

# Custom handler that writes structured JSON
class StructuredPrefectHandler(PrefectHandler):
    def emit(self, record):
        # Convert to JSON and write to stdout (picked up by Vector/Fluentd)
        pass
```

This is the **critical wiring** — without it, even if Loki is available,
Prefect logs won't go there.

### 4. Prometheus Metrics (stretch)

Expose a `/metrics` endpoint from the Prefect worker process.
Use `prometheus_client` to export:
- `prefect_flow_run_duration_seconds`
- `prefect_task_run_duration_seconds`
- `prefect_flow_run_count` (by status)

---

## What's Blocked

### Loki Stack Not Available

The primary blocker is that **Loki + Grafana is not currently deployed** in the
target environment. Until that stack is stood up, all log aggregation efforts
are constrained to file-based buffering.

**Prerequisites before Loki wiring is possible:**
- [ ] Grafana Loki deployed (or_cloud: Grafana Cloud with Loki)
- [ ] Grafana Agent or Vector deployed on all Prefect worker nodes
- [ ] `LOKI_ENDPOINT` env var available to worker nodes
- [ ] Network connectivity from worker nodes to Loki (port 3100)

---

## Roadmap

```
Phase 1 (Immediate — no external deps)
├── [x] prefect.yaml exists
├── [ ] JSONLogHandler wired into Prefect logging config
├── [ ] Prefect base task emits structured JSON to stdout
└── Status: IN PROGRESS — unblocked, no external services needed

Phase 2 (Requires Loki stack — BLOCKED)
├── [ ] Loki / Grafana Cloud provisioned
├── [ ] Vector or Grafana Agent deployed on workers
├── [ ] vector.yaml written and tested
├── [ ] Prefect JSON logs flowing to Loki
└── Status: BLOCKED — waiting on Loki stack

Phase 3 (Stretch — observability completeness)
├── [ ] Prometheus metrics from Prefect workers
├── [ ] OpenTelemetry trace propagation across flows
└── Status: STRETCH
```

---

## Current Action Items

| # | Action | Owner | Blocked by |
|---|--------|-------|-----------|
| 1 | Wire JSONLogHandler into prefect.yaml | arifOS eng | None |
| 2 | Verify JSON stdout from test flow run | arifOS eng | None |
| 3 | Stand up Loki stack (infra) | infra team | Budget / cluster |
| 4 | Deploy Vector on Prefect nodes | infra team | Loki stack |
| 5 | Wire Vector → Loki | infra team | Vector deployed |

---

*Last reviewed: 2026-04-19*
*Owner: arifOS engineering*
