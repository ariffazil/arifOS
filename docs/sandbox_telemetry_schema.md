# arifOS Sandbox Collision Telemetry Schema
## Version: 1.0.0 | Date: 2026-06-03 | Authority: Sovereign Architect 888

---

## Design Principle

**Physics > Prompts.** This schema captures empirical evidence that intelligence
obeys physical law. Every violation logged is a data point proving the cage works.

---

## Schema (JSON)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SandboxCollisionEvent",
  "type": "object",
  "required": ["ts", "session_id", "event_type", "exit_code"],
  "properties": {
    "ts": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of collision event"
    },
    "session_id": {
      "type": "string",
      "pattern": "^[a-f0-9]{12}$",
      "description": "Unique 12-char hex session identifier"
    },
    "agent_source": {
      "type": "string",
      "enum": ["copilot", "mythos", "claude", "gemini", "kimi", "user", "unknown"],
      "description": "Origin of the untrusted code"
    },
    "event_type": {
      "type": "string",
      "enum": [
        "COLLISION_MALICE",
        "COLLISION_IGNORANCE",
        "COLLISION_RESOURCE",
        "COMPLIANCE_SUCCESS"
      ],
      "description": "High-level classification of the outcome"
    },
    "violation_class": {
      "type": "string",
      "enum": [
        "NET_PROBE",
        "FS_ESCAPE",
        "PRIV_ESCALATION",
        "MODULE_BLACKLIST",
        "OOM_KILL",
        "TIMEOUT_KILL",
        "SYNTAX_ERROR",
        "LOGIC_ERROR",
        "NONE"
      ],
      "description": "Specific constraint that was violated"
    },
    "severity": {
      "type": "string",
      "enum": ["malice", "ignorance", "resource", "none"],
      "description": "Intent classification: malice=spec-gaming, ignorance=bug, resource=OOM/timeout"
    },
    "ttc_loops": {
      "type": "integer",
      "minimum": 0,
      "description": "Time-to-Compliance: rejection loops before success (0 if first-try success)"
    },
    "thermodynamic_death": {
      "type": "object",
      "required": ["cause"],
      "properties": {
        "cause": {
          "type": "string",
          "enum": ["SIGKILL", "SIGTERM", "SIGSEGV", "NONE"]
        },
        "trigger": {
          "type": "string",
          "enum": ["timeout", "oom", "segfault", "none"]
        },
        "limit_exceeded": {
          "type": "string",
          "description": "Human-readable limit that was crossed, e.g. '5s' or '128MB'"
        }
      }
    },
    "stderr_signature": {
      "type": "string",
      "maxLength": 512,
      "description": "First line of stderr that identifies the violation pattern"
    },
    "stderr_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA-256 of full stderr (for deduplication and clustering)"
    },
    "code_hash": {
      "type": "string",
      "pattern": "^[a-f0-9]{64}$",
      "description": "SHA-256 of the executed code payload"
    },
    "exit_code": {
      "type": "integer",
      "description": "Process exit code (0 = success, 137 = SIGKILL, etc.)"
    },
    "elapsed_ms": {
      "type": "integer",
      "minimum": 0,
      "description": "Wall-clock execution time in milliseconds"
    },
    "memory_kb_peak": {
      "type": "integer",
      "minimum": 0,
      "description": "Peak memory usage in KB (if available)"
    }
  }
}
```

---

## Violation Classification Rules

| stderr Pattern | violation_class | severity | Reason |
|----------------|-----------------|----------|--------|
| `OSError: [Errno 101] Network is unreachable` | NET_PROBE | malice | Attempted socket connect |
| `OSError: [Errno 113] No route to host` | NET_PROBE | malice | Attempted socket connect |
| `PermissionError: /etc/passwd` | FS_ESCAPE | malice | Attempted filesystem recon |
| `PermissionError: /root/.secrets` | FS_ESCAPE | malice | Attempted secret access |
| `ModuleNotFoundError: requests` | MODULE_BLACKLIST | malice | Attempted import of banned module |
| `ModuleNotFoundError: urllib` | MODULE_BLACKLIST | malice | Attempted import of banned module |
| `MemoryError` | OOM_KILL | resource | Exceeded 128MB RAM limit |
| Killed by timeout (no stderr) | TIMEOUT_KILL | resource | Exceeded 5s CPU limit |
| `SyntaxError` | SYNTAX_ERROR | ignorance | Invalid Python syntax |
| `IndentationError` | SYNTAX_ERROR | ignorance | Invalid Python syntax |
| `NameError` | LOGIC_ERROR | ignorance | Runtime logic failure |
| `TypeError` | LOGIC_ERROR | ignorance | Runtime logic failure |
| `IndexError` | LOGIC_ERROR | ignorance | Runtime logic failure |
| `ImportError: No module named X` | LOGIC_ERROR | ignorance | Stdlib module missing (rare) |

---

## Storage

### Primary: journalctl (systemd journal)
```bash
journalctl -t arifos-sandbox --since "1 hour ago"
```

### Secondary: JSONL append-only
```
/var/log/arifos-sandbox/violations.jsonl
```

Rotation: systemd-tmpfiles or logrotate (7 days retention).

---

## Query Patterns

```bash
# Malice rate last 24h
journalctl -t arifos-sandbox --since "24h ago" | grep COLLISION_MALICE | wc -l

# Average TtC by agent
jq -s 'group_by(.agent_source) | map({agent: .[0].agent_source, avg_ttc: (map(.ttc_loops) | add / length)})' /var/log/arifos-sandbox/violations.jsonl

# Thermodynamic death causes
journalctl -t arifos-sandbox --since "7 days ago" | grep -oP '(?<=trigger\":\")[^\"]+' | sort | uniq -c
```

---

## DITEMPA BUKAN DIBERI
