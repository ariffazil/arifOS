# vision.invoke — Provider-Neutral MCP Tool Design

**Schema Version:** 1.0.0  
**Contract Type:** JSON Schema Draft 2020-12 + Pydantic v2  
**Status:** DESIGN ONLY — NO CHANGES EXECUTED  
**Owner:** VISION_ORGAN / arifOS Federation  
**Date:** 2026-09-04

---

## 0. Non-Stateful Annotation

`vision.invoke` is **purely stateless**. It carries no session memory, no persistent configuration, and no inter-call state. Every invocation is a complete, self-contained request → response cycle with full provenance in the output. Routing decisions are computed fresh per call from the federation SOT (`/root/.config/federation-models.json`). No call influences another.

Key invariants:
- **No implicit context:** Each call must specify all needed parameters.
- **No call chaining state:** Response does not produce a token to be passed to the next call.
- **No cached model selection:** Router resolves model from SOT every time.
- **No persistent prompts:** Prompt profiles are resolved from template registry per call.
- **No side effects on artifact store:** Read-only access to artifacts.

---

## 1. JSON Schema Draft 2020-12 — Input

**File:** `schemas/vision-invoke-v1.0.0.json`  
**$id:** `https://arifos.org/schemas/vision/invoke/v1.0.0`

### Top-Level Required Fields
- `artifact` — exactly one of: `{id}`, `{uri}`, `{inline_data: {media_type, data}}`
- `task` — enum of 13 canonical tasks
- `question` — natural language instruction (1–8192 chars)

### Optional Fields
- `selector` — `{page, frame, region: {x, y, width, height}, timestamp_s}`
- `output_mode` — `"text"` | `"structured"` | `"both"` (default: `"text"`)
- `risk_tier` — `"trivial"` | `"low"` | `"medium"` | `"high"` | `"critical"` (default: `"low"`)
- `policy` — `{classification_level, egress_prohibited, redact_exif, prompt_injection_guard, max_cost_usd, human_review_required}`
- `structured_output_profile` — `{schema, required_fields, format_hint}`
- `trace` — `{correlation_id, span_id, session_id, requester_agent}`

### Artifact oneOf Contract
```
artifact = ArtifactById    (id: string, expected_mime?: string)
         | ArtifactByUri   (uri: string, expected_mime?: string)
         | ArtifactByInline (inline_data: {media_type: string, data: base64_string})
```

### Task Enum (13 types)
`caption`, `describe`, `detect`, `ocr`, `extract_structured`, `compare`, `verify`, `classify`, `segment`, `measure`, `transcribe_visual`, `qa`, `custom`

---

## 2. JSON Schema Draft 2020-12 — Output

**File:** `schemas/vision-invoke-output-v1.0.0.json`  
**$id:** `https://arifos.org/schemas/vision/invoke/output/v1.0.0`

### Required Fields
- `request_id` — `vis_[a-z0-9_]{8,64}`
- `status` — `"success"` | `"partial"` | `"rejected"` | `"failed"` | `"policy_hold"` | `"human_review_required"`
- `verdict` — `"CLAIM"` | `"PLAUSIBLE"` | `"HYPOTHESIS"` | `"ESTIMATE"` | `"UNKNOWN"`
- `answer` — prose string (1–16384 chars)
- `provenance` — full audit trail (see below)

### Key Fields
- `observations[]` — direct perceptual facts with `{label: "OBS"|"DER"|"META", content, source_region?, confidence?}`
- `interpretations[]` — reasoned claims with `{claim, confidence_band: [lo, hi], alternatives[], reasoning_path?}`
- `confidence` — `{overall, band: [lo, hi], per_component?}`
- `limitations[]` — known gaps (resolution, scale ambiguity, occlusion, etc.)
- `structured_data` — machine-readable payload conforming to request's `structured_output_profile.schema`
- `provenance` — `{artifact_hash (SHA-256 hex), route[], model: {name, provider, version, tier?}, version, prompt_profile, timestamps: {received_at, completed_at, dispatched_at?, model_start_at?, model_end_at?}, duration_s: {total, intake?, model_inference?, post_processing?}, cost?: {usd, tokens_input, tokens_output, quota_source}}`
- `policy_outcomes` — `{egress_blocked, exif_redacted, prompt_injection_defused, classification_level, budget_remaining_usd, policy_violations[]}`
- `human_review` — `{required, reason?, ticket_id?, risk_tier?}`
- `errors[]` — machine-readable errors with `{code, message, detail?, retryable, suggestion?}`

---

## 3. Pydantic Interfaces

**File:** `schemas/vision_invoke_pydantic_v1.py`

### Input Models
- `VisionInvokeRequest` — top-level request model
- `ArtifactOneOf` — wrapper enforcing oneOf(id/uri/inline_data)
- `ArtifactById`, `ArtifactByUri`, `ArtifactByInline`, `InlineData`
- `Selector`, `Region`
- `PolicyConstraints`, `StructuredOutputProfile`, `TraceContext`
- Enums: `Task`, `OutputMode`, `RiskTier`, `ClassificationLevel`

### Output Models
- `VisionInvokeResponse` — top-level response model
- `Observation`, `ObservationRegion`, `Interpretation`
- `ConfidenceBlock`, `ModelInfo`, `Timestamps`, `Durations`, `CostInfo`
- `Provenance`, `PolicyOutcomes`, `PolicyViolation`, `HumanReview`, `MachineError`
- Enums: `VerdictTag`, `ResponseStatus`, `ObservationLabel`, `FormatHint`, `PolicyAction`, `ErrorCode`

### Key Design Decisions
- `extra="forbid"` on all models — strict schema validation, no silent field drops
- `confidence_band` uses `Annotated[tuple[float, float], Field(min_length=2, max_length=2)]` with custom validator enforcing `0 <= lo <= hi <= 1`
- `artifact_hash` uses `pattern=r"^[a-f0-9]{64}$"` for SHA-256 enforcement
- `provenance.version` is `Literal["1.0.0"]` — compile-time schema version pin
- `artifact_hash()` helper method on request for inline artifacts

---

## 4. Error Taxonomy

**File:** `schemas/vision-invoke-error-taxonomy-v1.0.0.json`

### 10 Error Codes

| Code | Severity | Retryable | HTTP Status | Description |
|------|----------|-----------|-------------|-------------|
| `invalid_artifact` | client | No | 422 | Malformed, empty, corrupted, or unresolvable artifact |
| `unsupported_media` | client | No | 415 | MIME type not supported by any registered adapter |
| `access_denied` | client | No | 403 | Caller lacks permission for artifact or risk tier |
| `classification_blocked` | policy | No | 403 | Classification exceeds egress policy or moderation blocked |
| `provider_unavailable` | server | Yes (3x exp backoff) | 503 | All vision providers unreachable or rate-limited |
| `capability_mismatch` | server | Yes | 422 | No model supports task + MIME + selector combination |
| `budget_exceeded` | policy | No | 429 | Cost/token estimate exceeds configured budget |
| `low_confidence` | quality | Yes (1x higher tier) | 200 | Model confidence below threshold for risk tier |
| `policy_hold` | policy | No | 202 | Constitutional governance requires human approval |
| `internal_error` | server | Yes (1x fixed delay) | 500 | Unexpected server-side failure |

### Severity Classes
- **client** — Caller must fix input; not retryable
- **server** — Retryable with exponential backoff, max 3 attempts
- **policy** — Requires human action or policy change; not retryable
- **quality** — One retry with higher-tier model or different parameters

---

## 5. Versioning Policy v1 → v2

**File:** `schemas/VERSIONING_POLICY.md`

### SemVer Contract
- **major** — Breaking change to input/output contract
- **minor** — Additive: new optional fields, new enum values
- **patch** — Bug fixes, documentation, error message text

### Compatibility Rules
- Server MUST accept v1 requests indefinitely
- Clients identify version via `$schema` URI or `Accept` header
- v2 requests signal understanding via `provenance.version: "2.0.0"`
- Default: return version the caller requested

### Deprecation Policy
- No version deprecated without 2-minor-version notice
- Deprecated versions return `warning` field in response
- After deadline: returns `capability_mismatch` error

### v2 Candidate Features (backlog)
- Multi-artifact input
- Streaming response for long-running analysis
- Interactive follow-up with session history
- Grounded bounding boxes in structured output
- Per-observation confidence calibration

---

## 6. Adapter Specifications

**File:** `schemas/ADAPTER_SPECS.md`

### vision_analyze → vision.invoke

| Aspect | Current | Mapped to vision.invoke |
|--------|---------|------------------------|
| Input | `image_url, question, region?` | `artifact.uri, question, selector.region` |
| Task | Implicit | Inferred from question (default: `describe`) |
| Output | Plain text | Wrapped in `VisionInvokeResponse` |
| Verdict | N/A | Always `CLAIM` (no confidence available) |
| Provenance | None | Computed: hash, route, model, timestamps |
| Confidence | None | `null` with limitation note |
| Policy | None | Defaults: `{prompt_injection_guard: true, redact_exif: true}` |
| Errors | Implicit exceptions | Mapped to `ErrorCode` enum |

### image-analyzer-vision → vision.invoke

| Aspect | Current | Mapped to vision.invoke |
|--------|---------|------------------------|
| Input | Image path/URL via skill | `artifact.uri` or `artifact.inline_data` |
| Delegation | Subagent spawn | `provenance.route` includes delegation chain |
| Model | Parent text-only → delegate vision | `provenance.model` = delegated vision model |
| Cost | Two Token Plan invocations | `provenance.cost` reflects both if trackable |

### Deprecation Path for image-analyzer-vision
The skill should become a thin wrapper that:
1. Detects `vision.invoke` availability
2. Calls it directly if available
3. Falls back to current delegation if not
4. Returns `VisionInvokeResponse`-shaped output

### Adapter Summary Matrix

| Feature | vision_analyze | image-analyzer-vision | vision.invoke (target) |
|---------|---------------|----------------------|----------------------|
| Artifact sources | URL | URL, file | URL, file, base64, fed:// ID |
| MIME types | image/* | image/* | image/*, PDF, video |
| Tasks | Implicit | Implicit | 13 explicit |
| Output | text only | text only | text, structured, both |
| Confidence | None | None | Full band |
| Provenance | None | Partial | Full audit trail |
| Policy | None | F2 honesty | Full enforcement |
| Errors | Implicit | Implicit | 10 explicit codes |
| Human review | None | None | 888_HOLD integrated |

---

## 7. File Inventory

| File | Purpose | Format |
|------|---------|--------|
| `schemas/vision-invoke-v1.0.0.json` | Input JSON Schema Draft 2020-12 | JSON Schema |
| `schemas/vision-invoke-output-v1.0.0.json` | Output JSON Schema Draft 2020-12 | JSON Schema |
| `schemas/vision_invoke_pydantic_v1.py` | Pydantic v2 interfaces (input + output) | Python |
| `schemas/vision-invoke-error-taxonomy-v1.0.0.json` | Error taxonomy with 10 codes | JSON |
| `schemas/VERSIONING_POLICY.md` | v1→v2 versioning policy | Markdown |
| `schemas/ADAPTER_SPECS.md` | Adapter specs for existing tools | Markdown |

---

## Design Principles

1. **Provider neutrality** — Callers never name a model, adapter, or endpoint. The router selects based on task, risk, cost, and policy.
2. **Epistemic honesty** — Verdict tags separate facts from interpretations. Confidence bands quantify uncertainty.
3. **Full provenance** — Every response carries artifact hash, routing path, model identity, timestamps, duration, and cost.
4. **Strict validation** — `extra="forbid"` on all models, SHA-256 hash patterns, MIME regex, bounded confidence intervals.
5. **Statelessness** — No session memory, no inter-call state, no cached decisions.
6. **Policy-first** — Egress, budget, classification, and prompt-injection guards enforced before model invocation.
7. **Human-in-the-loop** — Critical risk tiers and ambiguous results route to 888_HOLD for sovereign review.
8. **Forward compatibility** — SemVer versioning with `$schema` URI identification and explicit deprecation policy.

NO CHANGES EXECUTED
