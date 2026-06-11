# arifOS — PROBE_PYPI

> **What a stranger sees when they `pip install arifos` today.**
> Probe-only document. No fixes proposed here. This is a snapshot of
> the current state so the next agent has receipts.
> Generated: 2026-06-11.

---

## 1. The wheel exists

```
$ ls -1 /root/arifOS/dist/
arifos-2026.6.11-py3-none-any.whl
arifos-2026.6.11.tar.gz
```

The wheel name is `arifos` (lowercase, no separator). The version is
`2026.6.11`. The format is `py3-none-any` — pure Python, no platform
tag. This is what `pip install` will fetch from PyPI once published.

## 2. The package imports

```python
$ python3 -c "import arifosmcp; print(arifosmcp.__file__)"
/root/arifOS/arifosmcp/__init__.py
```

The **importable namespace is `arifosmcp`**, not `arif`. This is a
known mismatch with the wheel name. A stranger doing
`pip install arifos` will not find a top-level `arif` import; they
have to know to write `arifosmcp`. See PACKAGE_RENAME_ROADMAP.md
(888_HOLD — not yet forged).

## 3. The 13 canonical tools are present

```python
$ python3 -c "
from arifosmcp.constitutional_map import CANONICAL_TOOLS
print(len(CANONICAL_TOOLS), 'tools')
"
13 tools
```

`CANONICAL_TOOLS` is the registry. The kernel exposes all 13.

## 4. The transport is FastMCP

```python
$ grep -E "fastmcp" /root/arifOS/pyproject.toml | head -3
"fastmcp[tasks]==3.4.2",
```

The kernel uses `fastmcp[tasks]`. It supports stdio, SSE, and HTTP via
the FastMCP server. The `tasks` extra is the long-running operation
extension (MCP 2025-11-25 spec).

## 5. The state model

| Layer | Where |
|---|---|
| L1 (ephemeral) | Process memory |
| L2 (session) | Process memory + Redis (optional) |
| L3 (fuzzy) | Qdrant (optional, 127.0.0.1:6333) |
| L4 (official) | Postgres (optional) |
| L5 (graph) | Graphiti / FalkorDB (optional) |
| L6 (sealed) | VAULT999 (append-only, hash-chained) |

The kernel ships with L1/L2 in-process by default. L3–L5 are
optional and connect to the federated services. L6 is always
available — it's the kernel's own audit trail.

## 6. The seal path is split

- **Canonical seal path** (where SEAL should land): `vault999-writer`
  service on `127.0.0.1:5001`, backing to `vault_sealed_events`
  table in Supabase.
- **Local mirror**: `/root/VAULT999/outcomes.jsonl` — append-only
  JSONL, sha256-chained.
- **Chain state at probe time**: 61 seals, 120 gaps, `chain_integrity:
  BROKEN`. The chain is **broken** as of this snapshot. A
  `git filter-repo` + backfill script is needed to repair it. This
  is **888_HOLD** territory.

## 7. The estate mixes with the kernel

| Type | Count | Examples |
|---|---|---|
| Kernel | 8 | `arifOS/`, `arifosmcp/`, `VAULT999/`, `core/`, `contracts/`, `tests/`, `build/`, `docs/`, `deploy/`, `scripts/` |
| Estate | 58 | `HUMAN/`, `supabase/`, `authentik/`, `governor_mcp/`, `arifbrain/`, `arif-identity-broker/`, `arifos_plan/`, `arifos_wiki_tools/`, `blueprints/`, `agentzero/`, `infra/`, `journal/`, `playwright-mcp/`, `telegram-bot/`, `secrets/` (containing a compromised key), ... |

A stranger cloning the repo cannot tell at a glance which directory
is the product. **The monorepo estate extraction is required before
`pip install arifos` is honest.** See 8-step forge order in the brief.

## 8. The compromised key in `secrets/`

```
$ ls /root/arifOS/secrets/
README.md
did_ed25519_private.key.COMPROMISED_PEM_EXPOSED
did_ed25519_public.key
did_multikey.txt
verify.sh
```

The file `did_ed25519_private.key.COMPROMISED_PEM_EXPOSED` is a
private identity key that has been exposed. **Renaming the directory
fixes nothing — the key is in git history.** The structural fix is
`git filter-repo` + force-push, plus key rotation on the identity
side. This is **888_HOLD** territory and F11 (AUTH) floor territory.
Do not `pip install arifos` and ship it to a customer before this
is resolved.

## 9. The end-to-end stranger experience

```
$ pip install arifos
... installs ...

$ python -c "import arifos"
ModuleNotFoundError: No module named 'arifos'

$ python -c "import arifosmcp; print(len(arifosmcp.constitutional_map.CANONICAL_TOOLS))"
13

$ python -m arifosmcp.runtime.server   # the FastMCP server
# starts on stdio, or 8088 if --transport http
```

The stranger imports `arifosmcp`, not `arifos`. The 13 tools work.
The server starts. **What they don't see is the 58 estate dirs and
the compromised key in the source they cloned** — those are git
history, not wheel contents.

## 10. What this probe does NOT cover

- Whether the wheel is signed.
- Whether the source distribution is reproducible.
- Whether the wheel matches the source byte-for-byte.
- Whether PyPI credentials exist for publishing.
- Whether the AGPL-3.0 obligation is satisfied by redistributors.
- Whether the dependency tree is free of known vulnerabilities.

These are all 888_HOLD items.

---

**DITEMPA BUKAN DIBERI** — *Forged, not given.*
