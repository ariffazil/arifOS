# vision.invoke — Adapter Specifications

This document defines how existing vision capabilities adapt to the `vision.invoke` MCP tool contract.

---

## Adapter 1: `vision_analyze` (Hermes Built-in Tool)

### Current Interface

```python
vision_analyze(image_url: str, question: str, region: Optional[list[int]] = None) -> str
```

Returns a plain text transcript of the model's visual analysis.

### Adapter Contract: `vision_analyze → vision.invoke`

| vision.invoke field | Mapping |
|---------------------|---------|
| `artifact.uri` | ← `image_url` |
| `artifact.expected_mime` | Inferred from URL extension or HTTP Content-Type |
| `task` | Inferred from `question` keywords (default: `describe`) |
| `question` | ← `question` (verbatim) |
| `selector.region` | ← `region` as `[x, y, x2, y2]` → `{x, y, width: x2-x, height: y2-y}` |
| `selector.page` | Not supported by `vision_analyze` (images only) |
| `selector.frame` | Not supported |
| `output_mode` | Always `"text"` (current tool returns prose only) |
| `risk_tier` | Default `"low"` (no policy layer exists) |
| `policy` | Not enforced by `vision_analyze` — adapter adds default `{prompt_injection_guard: true, redact_exif: true}` |
| `trace` | Populated from calling session if available |

### Response Mapping (`str` → `VisionInvokeResponse`)

| VisionInvokeResponse field | Source |
|---------------------------|--------|
| `request_id` | Minted by adapter: `vis_hermes_{timestamp_ms}` |
| `status` | `"success"` if text returned, `"failed"` if exception |
| `verdict` | Always `"CLAIM"` (vision_analyze has no confidence scoring) |
| `answer` | ← raw text from vision_analyze |
| `observations` | `[{label: "OBS", content: answer}]` (single synthetic observation) |
| `interpretations` | `[]` (no separation capability) |
| `confidence` | `null` (not available) |
| `limitations` | `["vision_analyze does not provide confidence scores", "observations not separated from interpretations"]` |
| `structured_data` | `null` |
| `provenance.artifact_hash` | Computed by adapter from downloaded image bytes |
| `provenance.route` | `["intake:download", "adapter:vision_analyze", "model:<active_model>"]` |
| `provenance.model` | Resolved from active model config at call time |
| `provenance.version` | `"1.0.0"` |
| `provenance.prompt_profile` | `"vision.default.v1"` |
| `provenance.timestamps` | Filled from call lifecycle |
| `provenance.duration_s` | Computed from start/end |
| `provenance.cost` | `null` (vision_analyze has no cost tracking) |
| `policy_outcomes` | `{prompt_injection_defused: true, exif_redacted: false}` (defaults) |
| `human_review` | `null` |
| `errors` | Populated on failure with appropriate ErrorCode |

### Limitations Noted

- No structured output support
- No confidence scoring
- No policy enforcement (budget, egress, classification)
- Single artifact only (no compare task)
- Image only (no PDF, video)

### Adapter Implementation Notes

```python
def adapt_vision_analyze_to_invoke(
    request: VisionInvokeRequest,
    vision_analyze_fn: callable
) -> VisionInvokeResponse:
    """
    1. Resolve artifact URI → download image bytes
    2. Compute SHA-256 hash
    3. Call vision_analyze(image_url, question, region)
    4. Wrap result in VisionInvokeResponse with provenance
    5. Return response with status=success or error
    """
```

---

## Adapter 2: `image-analyzer-vision` (Federation Skill)

### Current Interface

This is a **skill** (not a tool) that routes text-only models to vision-capable models.
It delegates by spawning a subagent with a vision model.

### Adapter Contract: `image-analyzer-vision → vision.invoke`

| vision.invoke field | Mapping |
|---------------------|---------|
| `artifact.uri` | ← image path/URL passed in skill invocation |
| `artifact.inline_data` | Supported — skill reads image and delegates |
| `task` | Always `"describe"` (skill has no task taxonomy) |
| `question` | Default: `"Describe this image in detail."` unless user overrides |
| `output_mode` | Always `"text"` |
| `risk_tier` | Inferred from skill's own `risk_tier: low` frontmatter |
| `policy` | Skill enforces F2 TRUTH (honesty about model capabilities) |
| `trace` | Caller session context available |

### Response Mapping

Same pattern as `vision_analyze` adapter, with differences:

| VisionInvokeResponse field | Difference from vision_analyze adapter |
|---------------------------|--------------------------------------|
| `provenance.route` | `["intake:hash", "skill:image-analyzer-vision", "delegate:<vision_model>", "postflight:wrap"]` |
| `provenance.model` | The **delegated** vision model (e.g., `qwen3.7-plus`), not the parent's text-only model |
| `limitations` | Includes `["Delegated via image-analyzer-vision skill — two Token Plan invocations"]` |
| `provenance.cost` | Should reflect both parent + delegate invocation if trackable |

### Adapter Implementation Notes

The adapter transforms the skill's freeform delegation into a structured `vision.invoke` call:

```python
def adapt_skill_to_invoke(
    request: VisionInvokeRequest,
    skill_delegate_fn: callable  # The skill's delegation mechanism
) -> VisionInvokeResponse:
    """
    1. Resolve artifact (file path or URL)
    2. Hash artifact bytes
    3. Delegate to vision-capable model via skill
    4. Wrap in VisionInvokeResponse
    5. Annotate provenance with delegation chain
    """
```

### Deprecation Path

Per `fed-vision-architecture` skill, `image-analyzer-vision` **should become a thin wrapper** over `vision.invoke`:

```
Before (current):
  user → text-only model → image-analyzer-vision skill → vision model → text response

After (target):
  user → vision.invoke MCP tool → router → vision model → structured VisionInvokeResponse
```

The skill should be updated to:
1. Detect `vision.invoke` availability
2. If available, call `vision.invoke` directly instead of spawning subagent
3. If not available, fall back to current delegation behavior
4. Return `VisionInvokeResponse`-shaped output instead of raw text

---

## Adapter Summary Matrix

| Feature | vision_analyze | image-analyzer-vision | vision.invoke (target) |
|---------|---------------|----------------------|----------------------|
| Artifact sources | URL only | URL, file path | URL, file, inline base64, fed:// ID |
| Supported MIME | image/* | image/* | image/*, PDF, video/* |
| Task taxonomy | Implicit | Implicit | 13 explicit task types |
| Output mode | text only | text only | text, structured, both |
| Confidence | None | None | Full confidence band |
| Provenance | None | Partial | Full (hash, route, model, cost, timestamps) |
| Policy enforcement | None | F2 honesty only | Full (egress, budget, classification, injection guard) |
| Error taxonomy | Implicit | Implicit | 10 explicit error codes |
| Human review gate | None | None | Integrated (888_HOLD) |
| Versioning | None | None | SemVer with $schema URI |
