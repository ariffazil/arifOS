# arifOS Kernel ABI — `model_registry.json` (measured-competence artifact)

> This README accompanies `arifosmcp/abi/model_registry.json` and exists
> to prevent the recurring confusion that this file is a stale copy of
> `arifosmcp/config/model_registry.json` (the deployment capability
> registry). **It is not.** They are two intentionally distinct artifacts.

## Two different registries

| Artifact | Path | Schema | Purpose | Author |
|---|---|---|---|---|
| **Kernel ABI measured-competence registry** | `arifosmcp/abi/model_registry.json` | `arifos://schema/model-registry/v1` | The kernel ABI's reserved slot for *measured* model competencies. Per its own `admission_rule`: "A model may propose intent only for measured competencies; `policy_registry` remains authoritative." Empty by design until competencies are measured. | `arifOS` kernel (ABI v1.0.0) |
| **Deployment capability registry** | `arifosmcp/config/model_registry.json` | `arifos-capability-registry/v5` (2026.07.04-v5) | The live, versioned registry of model capabilities, risk tiers, forbidden actions, and human-ack gates. 34 models. Referenced (not duplicated) by `AGENT_MODEL_MAP.json`. | `arifOS` deployers |
| **Federation routing & governance law** | `/root/AAA/registries/models/AGENT_MODEL_MAP.json` | `arifos-agent-model-map-v2` v2.0.3 | The canonical routing + governance law. 13 agents, 31 models, 21 routing rules, judge/seal restriction. | FORGE (F13-ratified) |

## Why the empty `models: []` is intentional

The ABI stub is consumed by `arifosmcp.abi.kernel_abi.model_registry()` and
the `validate_abi()` integrity check. Its `admission_rule` encodes the
design intent: only *measured* competencies earn a slot. The deployment
capability registry is the *declared* set; the kernel ABI is the
*measured* set. They are not the same list and must not be conflated.

The earlier recon (2026-07-24) incorrectly flagged the empty ABI stub
as a divergence from the config registry. The two are siblings, not
copies. A symlink would break the kernel ABI's empty-by-design semantics
and corrupt `validate_abi()`.

## Consumers

- `arifosmcp/abi/kernel_abi.model_registry()` (loader).
- `arifosmcp/tools/session.py`, `registry_query.py` (compiled-registry
  view; the ABI stub is not their primary source — they read
  `/root/AAA/registry/compiled/FEDERATION_MODEL.json`).
- `arifosmcp/tools/health.py:_check_model_registry` checks the
  **runtime profile mount** (`/root/arifos-model-registry/...`), NOT
  the ABI stub. Health telemetry is therefore not lied to by the
  empty ABI list.

## Consequence

- **Do not** symlink `abi/model_registry.json` →
  `config/model_registry.json`. The two have different schemas and
  the ABI one is empty by intent.
- **Do** populate `models[]` here as kernel-level measured competencies
  become available (separate effort, requires F13 review per the
  admission rule).
- **Do** keep `config/model_registry.json` as the deployment capability
  source of truth, referenced by `AGENT_MODEL_MAP.json`.
