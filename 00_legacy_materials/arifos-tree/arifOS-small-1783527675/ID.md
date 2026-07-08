# arifOS — ID

> **DEPRECATED TOOL COUNTS (2026-06-23 7-tool freeze)**: "13 canonical tools" claims here are legacy. Public surface is now the 7 verbs. See arifosmcp/runtime/public_surface.py.

> **One identity. One source.** All other ID-like files in this repo
> defer to this one. If a doc says `arifOS` does X but this file says
> arifOS is Y, **this file is correct.** Generated: 2026-06-11.

---

## What `arifos` is

`arifos` is the **constitutional AI kernel** of the arifOS Federation.
It is **one PyPI package**. It exposes **13 canonical MCP tools** that
together form the floor enforcer for every AI action the federation
takes. It does not compute. It does not decide. It **refuses, gates,
and seals**.

```
pip install arifos
```

The package name is `arifos` (lowercase, no separator) on PyPI. The
importable namespace is `arifosmcp` for now — see the rename roadmap
in `docs/PACKAGE_RENAME_ROADMAP.md` (FORGE_PLAN, 888_HOLD).

## What `arifos` is not

- Not a model. It runs *next to* a model, not *as* a model.
- Not an organ. GEOX, WEALTH, WELL, A-FORGE, AAA are separate
  `arifos-*` packages or services. They call *into* the kernel.
- Not a tool runner. The kernel plans and seals. A-FORGE executes.
- Not a database. The kernel writes its own audit trail to VAULT999.
  Organ state lives in organs.
- Not a chat. The kernel has no LLM-driven surface.

## The 13 canonical tools

| Stage | Tool | Function |
|---|---|---|
| 000 | `arif_session_init` | Bind constitution hash, load receipts, set risk leash |
| 111 | `arif_sense_observe` | Ground in reality (search/ingest/vitals/repo_map) |
| 222 | `arif_evidence_fetch` | Verified external evidence with provenance |
| 333 | `arif_mind_reason` | Symbolic reasoning kernel with confidence labels |
| 444 | `arif_heart_critique` | Ethical/dignity risk check before consequential action |
| 444r | `arif_reply_compose` | Governed response composition |
| 555 | `arif_kernel_route` | Routes intent to correct tool or federation organ |
| 555m | `arif_memory_recall` | Provenance-gated memory (L1/L2/L3/L4/L5/L6) |
| 666 | `arif_forge_execute` | Build execution — code generation, artifact, deployment |
| 666g | `arif_gateway_connect` | Federated cross-agent bridge |
| 777 | `arif_ops_measure` | Machine resource health + governance telemetry |
| 888 | `arif_judge_deliberate` | Final constitutional arbitration — SEAL/SABAR/VOID/HOLD |
| 999 | `arif_vault_seal` | Immutable ledger anchoring — cryptographic Merkle chain |

## Constitutional floors (F1–F13)

The kernel enforces 13 floors. See `arifosmcp/constitutional_map.py` for
the canonical list. Floors are **invariants, not policies**. A floor
violation is not a warning; it is a structural block.

## License

**AGPL-3.0-only.** Any derivative that ships over a network must
publish its source. This is the floor's mirror at the license level:
the kernel is open, and anything built on it stays open.

## Author

Muhammad Arif bin Fazil <arifbfazil@gmail.com>
Sovereign, F13 floor.

## Canonical Links (current)

| Link | URL |
|---|---|
| Source | `https://github.com/ariffazil/arifos` |
| Public MCP endpoint | `https://mcp.arif-fazil.com/mcp` |
| Live server card | `https://arifos.arif-fazil.com/.well-known/mcp.json` |
| Wheel | `dist/arifos-2026.6.11-py3-none-any.whl` |
| PyPI | (not yet published — pre-release verification) |

## Versioning

`vYYYY.MM.DD` only. **Never** `v1.2.3` or `v55.7.0` style counters.
Real-time-space-energy: the forge date IS the version. The counter
is meaningless. This is the iron rule, not a convention.

## See also

- `arifOS/AGENTS.md` — auto-generated, lists the 13 tools
- `arifOS/PROBE_PYPI.md` — what a stranger sees when they `pip install arifos`
- `arifOS/INVARIANTS.md` — what the kernel will not do

---

**DITEMPA BUKAN DIBERI** — *Forged, not given.*
