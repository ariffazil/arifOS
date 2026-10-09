# vision.invoke — Versioning Policy v1 → v2

**Schema ID:** `https://arifos.org/schemas/vision/invoke/v{major}.{minor}.{patch}`
**Contract type:** JSON Schema Draft 2020-12 + Pydantic v2

---

## Versioning Semantics

| Segment | Increment when... | Compatibility guarantee |
|---------|-------------------|------------------------|
| **major** (v1→v2) | Breaking change to input/output contract | New version is NOT backward-compatible; clients must explicitly opt in |
| **minor** (v1.0→v1.1) | Additive: new optional fields, new enum values | Backward-compatible — v1 clients work unchanged |
| **patch** (v1.0.0→v1.0.1) | Bug fixes, documentation, error-message text | Fully compatible — drop-in replacement |

---

## v1 → v2 Migration Triggers (examples)

A major bump to v2 would be warranted if any of these occur:

1. **New artifact source types** — e.g. adding `lidar_pointcloud` or `neuroimaging` as first-class artifact inputs that change the intake pipeline semantics.
2. **Removing or renaming** an existing required input field (`task`, `question`, `artifact`).
3. **Changing verdict enum** — adding/removing verdict tags changes downstream reasoning contracts.
4. **Restructuring provenance** — adding mandatory new provenance fields that break v1 parsers.
5. **Introducing mandatory structured-output** — making `structured_data` required would break v1 text-only callers.

---

## Compatibility Rules

### Server-side (adapter implementation)
- The server MUST accept v1 requests indefinitely (no forced deprecation).
- The server MAY return v2 responses to v2 callers (via `$schema` URI or `Accept` header negotiation).
- A v2 request with `version: "2.0.0"` in the `provenance` field signals the caller understands v2.
- Default behavior: always return the version the caller requested (echo `$schema` from input, or v1.0.0 if absent).

### Client-side
- Clients identify their schema version via:
  - Input `$schema` URI (preferred)
  - HTTP `Accept: application/vnd.arifos.vision-invoke.v2+json` header (MCP transport)
  - Pydantic model version class attribute (`class VisionInvokeRequestV2(...)`)

### Deprecation policy
- No version is deprecated without a 2-minor-version notice period (e.g., v1 deprecated only after v1.3.0 ships).
- Deprecated versions return a `warning` field in the response: `{"warning": "vision.invoke v1 deprecated, migrate to v2 by <date>"}`.
- After deprecation deadline, requests return `error: {"code": "capability_mismatch", "message": "v1 no longer supported"}`.

---

## Schema Version Registry

| Version | Status   | $schema URI                                      | Key Features                                          |
|---------|----------|---------------------------------------------------|-------------------------------------------------------|
| v1.0.0  | Current  | `.../vision/invoke/v1.0.0`                       | Initial release: single artifact, 13 tasks, 5 verdicts |
| v2.0.0  | Reserved | `.../vision/invoke/v2.0.0`                       | (Not yet defined — reserved for multi-artifact, streaming) |

---

## Future v2 Candidate Features (backlog, not committed)

- **Multi-artifact input** — `artifact: oneOf | array[oneOf]` for compare/verify tasks
- **Streaming response** — `output_mode: "stream"` for long-running video/OCR analysis
- **Interactive follow-up** — conversational vision with `session_id` and turn history
- **Grounded bounding boxes** — structured output with pixel-coordinates for detected objects
- **Confidence calibration** — per-observation calibration curves via model-registry metadata
