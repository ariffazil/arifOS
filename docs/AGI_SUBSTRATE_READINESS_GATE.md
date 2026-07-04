# AGI Substrate Readiness Gate

## Verdict

This gate does **not** claim arifOS is AGI.

It defines the minimum machine-checkable substrate conditions a governed agentic kernel must satisfy before AGI-like execution language is admissible.

Plain rule:

```text
No substrate proof, no AGI claim.
```

## Why this exists

arifOS already has the shape of a governed intelligence kernel:

```text
init → observe → think → route → judge → act → seal
```

But architecture alone is not enough. A real kernel must prove that:

1. Public agents see only the canonical seven verbs.
2. Internal sovereign machinery does not leak to public `tools/list`.
3. Every public verb exists in the capability graph.
4. Irreversible effects are restricted to `arif_act` and `arif_seal`.
5. Mutating capabilities are audited.
6. Irreversible capabilities require external witness, external evidence anchor, or `888_HOLD`.
7. No tool silently falls back to generic Python execution.

## New module

```text
arifosmcp/kernel/substrate_readiness.py
```

Primary entrypoint:

```python
from arifosmcp.kernel.substrate_readiness import assess_substrate_readiness

report = assess_substrate_readiness()
print(report.to_dict())
```

## Verdict vocabulary

```text
READY = all substrate gates pass
HOLD  = at least one gate fails
```

`READY` does not mean AGI. It means the kernel is coherent enough to continue agentic execution work without hantu authority claims.

## Gate list

| Gate | Meaning |
|---|---|
| `SURFACE_7_PUBLIC_VERBS` | Default MCP public surface is exactly the canonical seven tools. |
| `CAPABILITY_GRAPH_COVERS_CORE_SEVEN` | Capability graph contains the seven public tools and has a graph hash. |
| `ONLY_ACT_AND_SEAL_COMMIT_IRREVERSIBLY` | Only `arif_act` and `arif_seal` may commit irreversible public effects. |
| `MUTATIONS_ARE_AUDITED_NO_UNIVERSAL_FALLBACK` | Mutating tools require audit and cannot fall back to unconstrained Python. |
| `IRREVERSIBLE_ACTIONS_REQUIRE_EXTERNALITY_OR_HOLD` | Irreversible tools need externality or `888_HOLD`. |
| `NO_UNIVERSAL_PYTHON_ESCAPE_HATCH` | No capability silently degrades to generic Python execution. |

## Operator meaning

If the report returns `HOLD`, agents should not expand tools, add features, or claim AGI progress. They should fix the failed gates first.

If the report returns `READY`, agents may continue with controlled kernel work, still under F13 review for irreversible action.

## Non-negotiable

```text
arifOS becomes more real by reducing unearned authority, not by adding more tool names.
```
