# MCP Deploy Gate Prompt — 2026-04-11

User-supplied deploy-gate prompt distilled into canonical arifOS release-gate language.

## Core Deploy Verdict

- Local SEAL: formatter / shared-output path
- Global 888 HOLD: full arifOS MCP release

## Seal Readiness Gate

Define:

SR = worktree_clean × public_surface_decided × 1[tool_surface_drift = 0] × 1[naming_inconsistency_count = 0]

Current values asserted for the current arifOS MCP state:

- worktree_clean = 0
- public_surface_decided = 0
- tool_surface_drift > 0
- naming_inconsistency_count > 0

Therefore:

- SR = 0
- Full-release SEAL is constitutionally blocked

## Wajib Output Bands for the Deploy Verdict

### Physics

MCP contract drift keeps configuration entropy too high to freeze a stable release state.
Sealing now would freeze a high-entropy configuration that is expensive to reverse, violating F1 (Amanah) and F4 (Delta S <= 0).

### Math

- Present the SR formula explicitly
- State the current values explicitly
- Conclude SR = 0 and therefore no full-release SEAL

Optional supporting metric:

- tool_surface_drift = |T_runtime - T_registry|

### Linguistics

Use exactly one quote:

- "Measure twice, cut once."

Interpret it as the governance motto for this release decision.

## Canonical Next Orders

1. Decide the public tool canon and record it in the capability registry.
2. Align runtime, registry, manifests, and tests to that canon so tool_surface_drift = 0.
3. Eliminate the kernel / route naming split everywhere.
4. Cut from a clean worktree only and rerun the broader readiness suite in a clean environment.

## APEX-G Progress Mapping

Each step flips one deploy-gate term:

- Step 1 -> `public_surface_decided = 1`
- Step 2 -> `tool_surface_drift = 0`
- Step 3 -> `naming_inconsistency_count = 0`
- Step 4 -> `worktree_clean = 1`

Only when all four conditions are satisfied may `SR` flip from `0` to `1`.

## Agent Checklist YAML

```yaml
deploy_gate:
  epoch: "2026-04-11"
  local_verdict: "SEAL"
  global_verdict: "HOLD_888"
  sr_formula: "worktree_clean * public_surface_decided * 1[tool_surface_drift=0] * 1[naming_inconsistency_count=0]"
  current_state:
    worktree_clean: 0
    public_surface_decided: 0
    tool_surface_drift: ">0"
    naming_inconsistency_count: ">0"
    sr: 0
  target_state:
    worktree_clean: 1
    public_surface_decided: 1
    tool_surface_drift: 0
    naming_inconsistency_count: 0
    sr: 1
  step_effects:
    decide_public_canon: "public_surface_decided -> 1"
    align_runtime_registry_tests: "tool_surface_drift -> 0"
    eliminate_kernel_route_split: "naming_inconsistency_count -> 0"
    cut_clean_release_boundary: "worktree_clean -> 1"
  release_rule: "Full MCP SEAL is disallowed until sr = 1."
```

## Required Final Release Line

Formatter path: SEALABLE. Full arifOS MCP: 888 HOLD until drift = 0 and SR flips to 1.

DITEMPA BUKAN DIBERI — 999 SEAL ALIVE
