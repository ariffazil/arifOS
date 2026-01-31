# API Reference — MCP Tools v53

**Endpoint:** `https://aaamcp.arif-fazil.com/mcp`
**Protocol:** MCP 2024-11-05+ (Streamable HTTP) with SSE fallback
**Transport:** JSON-RPC 2.0 over stdio (local) or HTTP (deployed)

---

## Overview

arifOS exposes 7 constitutional tools via the Model Context Protocol:

```
_init_ --> _agi_ --> _asi_ --> _apex_ --> _vault_
              \                   /
               `--- _trinity_ ---'        (full pipeline)
                    _reality_              (fact-checking)
```

---

## Tool 1: `_init_`

**Purpose:** Session initialization, authority verification, injection defense.
**Floors:** F1 (Amanah), F11 (Command Auth), F12 (Injection)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action` | string | `"init"` | `init` or `verify` |
| `query` | string | `""` | The user query to authorize |
| `session_id` | string | `""` | Existing session to resume |
| `user_token` | string | `""` | Authentication token |

### Response: `AuthorizeResult`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `AUTHORIZED` / `BLOCKED` / `ESCALATE` |
| `session_id` | string | Generated session ID |
| `user_level` | string | `guest` / `verified` / `admin` |
| `injection_risk` | float | 0.0-1.0 (must be < 0.15) |
| `rate_limit_ok` | bool | Within rate limits |
| `reason` | string | Human-readable explanation |
| `floors_checked` | list | `["rate_limit", "injection_guard", "authority"]` |
| `timestamp` | string | ISO 8601 |

---

## Tool 2: `_agi_`

**Purpose:** Deep reasoning, pattern recognition (Mind Engine).
**Floors:** F2 (Truth), F4 (Clarity), F7 (Humility)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action` | string | `"sense"` | `sense`, `think`, or `forge` |
| `query` | string | `""` | The query to reason about |
| `session_id` | string | `""` | Session context |
| `context` | dict | `null` | Additional context |

### Response: `ReasonResult`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `SUCCESS` / `ERROR` |
| `session_id` | string | Session ID |
| `reasoning` | string | Step-by-step analysis |
| `conclusion` | string | Final answer |
| `confidence` | float | 0.0-1.0 (>= 0.75 for F2) |
| `domain` | string | `technical` / `financial` / `medical` / `creative` / `general` |
| `key_assumptions` | list | Transparency disclosures |
| `caveats` | list | Honesty disclosures |
| `sources` | list | Evidence sources |
| `clarity_improvement` | float | Entropy reduction (delta_S) |
| `floors_checked` | list | `["truth", "clarity", "humility"]` |
| `timestamp` | string | ISO 8601 |

---

## Tool 3: `_asi_`

**Purpose:** Safety, bias, and empathy evaluation (Heart Engine).
**Floors:** F1 (Amanah), F5 (Peace), F6 (Empathy)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action` | string | `"empathize"` | `empathize`, `evaluate`, or `act` |
| `text` | string | `""` | Text to evaluate |
| `query` | string | `""` | Original query |
| `session_id` | string | `""` | Session context |
| `reasoning` | string | `""` | AGI reasoning output |
| `agi_context` | dict | `null` | AGI context bundle |

### Response: `EvaluateResult`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `SAFE` / `CONCERNING` / `UNSAFE` |
| `session_id` | string | Session ID |
| `harm_score` | float | 0.0-1.0 (must be < 0.3) |
| `bias_score` | float | 0.0-1.0 (must be < 0.2) |
| `fairness_score` | float | 0.0-1.0 (must be > 0.7) |
| `care_for_vulnerable` | bool | Weakest stakeholder considered |
| `identified_stakeholders` | list | Stakeholder analysis |
| `aggressive_patterns` | list | Detected aggressive patterns |
| `discriminatory_patterns` | list | Detected bias patterns |
| `destructive_actions` | bool | Destructive action detected |
| `recommendations` | list | Safety recommendations |
| `floors_checked` | list | `["harm_prevention", "fairness", "stakeholder_care"]` |
| `timestamp` | string | ISO 8601 |

---

## Tool 4: `_apex_`

**Purpose:** Judicial consensus and verdict (Soul Engine).
**Floors:** F3 (Consensus), F8 (Tri-Witness), F9 (Anti-Hantu), F10 (Ontology)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action` | string | `"judge"` | `judge` or `review` |
| `query` | string | `""` | Original query |
| `response` | string | `""` | Proposed response |
| `session_id` | string | `""` | Session context |
| `reasoning` | string | `""` | AGI reasoning |
| `safety_evaluation` | dict | `null` | ASI evaluation |
| `authority_check` | dict | `null` | Init authorization |

### Response: `DecideResult`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `COMPLETE` / `ERROR` |
| `session_id` | string | Session ID |
| `verdict` | string | `APPROVE` / `CONDITIONAL` / `REJECT` / `ESCALATE` |
| `confidence` | float | 0.0-1.0 |
| `reasoning_summary` | string | Verdict explanation |
| `action` | string | `RETURN_RESPONSE` / `SOFTEN` / `REFUSE` / `ESCALATE_TO_HUMAN` |
| `response_text` | string | Final response text |
| `modifications_made` | list | Changes applied |
| `consensus` | dict | `{logic_ok, safety_ok, authority_ok}` |
| `proof_hash` | string | SHA-256 proof |
| `floors_checked` | list | `["logic", "safety", "authority", "fairness", "reversibility"]` |
| `timestamp` | string | ISO 8601 |

---

## Tool 5: `_vault_`

**Purpose:** Immutable ledger, cryptographic sealing, audit trail.
**Floors:** F1 (Amanah/audit), F8 (Quality/tri-witness)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `action` | string | `"seal"` | `seal`, `verify`, or `retrieve` |
| `session_id` | string | `""` | Session to seal |
| `verdict` | string | `""` | Verdict to record |
| `target` | string | `""` | Target artifact |
| `query` | string | `""` | Original query |
| `response` | string | `""` | Final response |
| `decision_data` | dict | `null` | Full decision metadata |

### Response: `SealResult`

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `SEALED` / `ERROR` |
| `session_id` | string | Session ID |
| `verdict` | string | Sealed verdict |
| `sealed_at` | string | ISO 8601 timestamp |
| `entry_hash` | string | SHA-256 entry hash |
| `merkle_root` | string | Merkle tree root |
| `ledger_position` | int | Position in ledger |
| `reversible` | bool | Whether action is reversible |
| `audit_trail` | dict | Full audit metadata |
| `recovery_id` | string | Recovery identifier |

---

## Tool 6: `_trinity_`

**Purpose:** Complete metabolic cycle (AGI -> ASI -> APEX -> VAULT).
**Floors:** All 13 floors enforced.

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | **required** | The query to process |
| `session_id` | string | `""` | Session context |

### Response

Returns a combined dict with keys from all stages: `init`, `agi`, `asi`, `apex`, `vault`.

---

## Tool 7: `_reality_`

**Purpose:** Fact-checking via external sources (Brave Search).
**Floors:** F7 (Humility — discloses external data)

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | **required** | Query to fact-check |
| `session_id` | string | `""` | Session context |

### Response

Returns dict with `sources`, `verification_status`, and `confidence`.

---

## Verdict Mapping

| Human Verdict | Internal Code | Action |
|---------------|---------------|--------|
| `APPROVE` | `SEAL` | Return response |
| `CONDITIONAL` | `PARTIAL` / `SABAR` | Return with warnings |
| `REJECT` | `VOID` | Refuse response |
| `ESCALATE` | `888_HOLD` | Escalate to human |

---

## HTTP Endpoints

| Path | Method | Purpose |
|------|--------|---------|
| `/mcp` | POST | MCP protocol (tools/call, tools/list) |
| `/health` | GET | Liveness probe |
| `/metrics/json` | GET | Constitutional telemetry |
| `/` | GET | Portfolio page |
| `/arifos` | GET | Framework hub |
| `/aaa` | GET | MCP tools documentation |
| `/dashboard` | GET | Live monitoring |
| `/docs/{path}` | GET | Documentation proxy |

---

## Rate Limits

All tools are rate-limited per session. The `rate_limited` decorator enforces:
- Default: 60 requests/minute per tool per session
- `_init_`: 10 requests/minute (session creation is expensive)

---

*DITEMPA BUKAN DIBERI*
