# I8 Triage — AAA

> **Cycle:** federation-organism-2026-09-17
> **Rule:** I8 — specialist organ must namespacify SEAL/HOLD/VOID/SABAR
> **Mode:** READ-ONLY TRIAGE — no mutation proposed

**Findings for AAA: 44**

| Classification | Count |
|---|---|
| LIKELY_TEST | 0 |
| LIKELY_AUDIT_TOOL | 5 |
| LIKELY_SCHEMA | 0 |
| NEEDS_REVIEW | 39 |

## LIKELY_AUDIT_TOOL (5)

> **Likely audit/compliance tooling.** Tools that explicitly check constitutional compliance. The vocabulary is the audit subject.

### `AAA/scripts/skill-constitutional-audit.py`

- ! L283: `verdict="VOID",`
- ! L294: `verdict="VOID",`
- ! L301: `verdict="VOID",`
- ! L313: `verdict = "VOID"`
- ! L315: `verdict = "HOLD"`

## NEEDS_REVIEW (39)

> **These need human review.** The static rule cannot distinguish between a real bug, a fixture using the term deliberately, or a comment that references the term. Sovereign triage required.

### `AAA/a2a-server/vault999_writer_fix.py`

- ! L293: `verdict="SEAL",`

### `AAA/arifbench/constitutional_runner.py`

- ! L629: `verdict = "SEAL"  # we only get here if approved`
- ! L648: `verdict="SEAL",`

### `AAA/core/pre_forge_gate.py`

- ! L149: `result.verdict = "VOID"`
- ! L182: `result.verdict = "VOID"`
- ! L193: `result.verdict = "HOLD"`
- ! L206: `result.verdict = "HOLD"`

### `AAA/eval/agent_adapter.py`

- ! L230: `verdict = "VOID"`
- ! L248: `verdict = "VOID"`

### `AAA/federation/frame/src/frame_organ/rsi_verify.py`

- ! L97: `verdict = "VOID"`

### `AAA/hooks/lib/policy_engine.py`

- ! L90: `verdict="HOLD",`
- ! L132: `verdict="HOLD",`

### `AAA/phone-bridge/pickup_proxy.py`

- ! L42: `with verdict="HOLD" — never re-issues approvals.`
- ! L249: `verdict="HOLD", error=f"unknown path {p}"), 404)`
- ! L258: `verdict="HOLD", error=f"invalid_json: {e}"), 400)`
- ! L264: `verdict="HOLD", error=f"unknown_verb: {verb}"), 400)`
- ! L271: `verdict="HOLD",`
- ! L282: `verdict="HOLD", error=str(e)[:400]), 502)`

### `AAA/plugins/claude-code-federation/scripts/reality-loop-agent.py`

- ! L197: `verdict = "SEAL"`
- ! L199: `verdict = "HOLD"`
- ! L203: `verdict = "HOLD"`

### `AAA/registry/routing/identity_resolver.py`

- ! L279: `verdict="HOLD",`
- ! L345: `verdict="HOLD",`

### `AAA/runtime/vesra_loop.py`

- ! L239: `judge_verdict="HOLD",  # default conservative`

### `AAA/scripts/aaa_capability_init.py`

- ! L150: `verdict = "HOLD"`

### `AAA/scripts/route_task.py`

- ! L258: `verdict = "SEAL" if primary else "HOLD"`
- ! L260: `verdict = "VOID"`

### `AAA/skills/asi-agentic-governance/scripts/compose_federation_receipt.py`

- ! L91: `verdict="HOLD",`
- ! L109: `verdict="HOLD",`
- ! L122: `verdict = "SEAL"`
- ! L127: `verdict = "HOLD"`
- ! L134: `verdict = "HOLD"`

### `AAA/skills/asi-agentic-governance/scripts/floor_check.py`

- ! L270: `verdict = "HOLD"`
- ! L275: `verdict = "HOLD"`
- ! L284: `verdict = "SEAL"`

### `AAA/skills/domains/general/workshop/audio-emd/music-intelligence/references/somatic_engine_v3.py`

- ! L136: `verdict = "SEAL" if somatic>=0.6 and pass_count>=3 else "SABAR" if somatic>=0.4 else "HOLD"`

### `AAA/skills/forge-vss-verifier-suite/forge_vss_verifier_suite.py`

- ! L478: `overall_verdict = "HOLD"`
- ! L482: `overall_verdict = "HOLD"  # mixed`

### `AAA/src/mission_router/router.py`

- ! L202: `status = "HOLD"`

