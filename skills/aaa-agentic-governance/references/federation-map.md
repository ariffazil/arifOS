# Federation map

Use this file when deciding which organ, repository, surface, or authority owns a task.

## Source-of-truth hierarchy

1. Live runtime health, tool registry, or test output.
2. `ariffazil/arifos/FEDERATION_STATUS.md` for cross-organ status when available.
3. Individual repo README, AGENTS.md, CONSTITUTION, INVARIANTS, schemas, and contracts.
4. User/F13 instruction, when explicit and safe.
5. Inference from architecture only as HYPOTHESIS.

## Organ table

| Organ | Repo | Role | Owns | Does not own |
|---|---|---|---|---|
| AAA | `ariffazil/AAA` | control plane, cockpit, A2A gateway, AREP declarations | routing, visibility, task state, registry | constitutional verdicts, domain computation, execution |
| arifOS | `ariffazil/arifos` | constitutional kernel | F1-F13, 888_JUDGE, VAULT999, canonical MCP authority | domain calculations, arbitrary repo execution without gates |
| A-FORGE | `ariffazil/A-FORGE` | governed execution shell | approved builds, shell/tool orchestration, telemetry | self-approval, final judgment, domain decisions |
| GEOX | `ariffazil/geox` | earth evidence | wells, seismic, petrophysics, prospect risk, claim limits | drilling/capital decision |
| WEALTH | `ariffazil/wealth` | capital evidence | NPV, IRR, EMV, macro, portfolio assumptions, downside | unilateral capital allocation |
| WELL | `ariffazil/well` | human readiness/substrate evidence | readiness, fatigue, dignity, reliability warnings | diagnosis, coercion, final decision |
| profile | `ariffazil/ariffazil` | public/professional context | bio/profile facts when sourced | unsupported personal inference |

## AAA namespace distinctions

- **AAA-Control Plane**: cockpit, A2A, AREP, registry, task status.
- **AAA-Doctrine**: abstraction, attestation, abduction; alignment, authority, accountability.
- **AAA-Interface**: operator display and reality console.
- **AAA-Eval**: benchmark/gold-record and quality checks.
- **AAA-HF**: Hugging Face doctrine corpus or model/data artifacts when present.

Invariant chain:

```text
AAA abstracts intent -> attests evidence -> abduces route -> arifOS judges -> A-FORGE executes approved work -> VAULT999 records final artifacts -> AAA displays state -> Arif/F13 decides high-consequence outcomes.
```
