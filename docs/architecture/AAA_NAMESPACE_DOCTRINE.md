<!-- SOT-MANIFEST
owner: Arif
last_verified: 2026-06-02
valid_from: 2026-06-02
valid_until: 2026-07-02
confidence: high
scope: /root/arifOS
epistemic_status: DOCTRINE
-->

# AAA Namespace Doctrine

> **AAA is polymorphic by design. When precision matters, qualify the surface.**

---

## Why AAA Has Multiple Meanings

AAA is not a single organ. It is a **sovereign acronym** that maps to multiple valid surfaces across the federation. Each surface has a distinct role, a distinct repo or dataset, and a distinct authority boundary.

Forcing one meaning onto AAA would collapse real distinctions. Instead, every reference to AAA in documentation, code, and communications should be **qualified** when ambiguity matters.

---

## The Five AAA Surfaces

| Term | Surface | Role |
|------|---------|------|
| **AAA-HF** | Hugging Face dataset `ariffazil/AAA` | Doctrine corpus, constitutional floors, verdicts, schemas, gold eval records, memory hardening, AAA-Supabase doctrine |
| **AAA-Cockpit** | GitHub repo `ariffazil/AAA` | Operations control plane, A2A gateway, agent registry, routing dashboard, mission control |
| **AAA-Doctrine** | Conceptual/abstract layer | Constitutional meaning: alignment, authority, accountability; appears in specs, governance docs, arifOS docs |
| **AAA-Interface** | Operator-facing surface | Human visibility chamber; lets Arif inspect actions, agents, records, approvals, seals |
| **AAA-Eval** | Benchmark/evaluation layer | Gold records and evaluation harness for testing whether agents obey arifOS law |

---

## Detailed Surface Descriptions

### AAA-HF — Hugging Face Dataset

- **Location:** https://hf.co/datasets/ariffazil/AAA
- **Role:** The constitutional substrate and doctrine corpus of arifOS.
- **Contains:** 13 floors (F1–F13), 186 canon records, 111 gold benchmark records, verdict labels (SEAL / VOID / HOLD / REFUSE / SABAR / PARTIAL), memory hardening specs, A-RIF constitutional RAG design, Supabase alignment schemas, GEOX doctrine links.
- **Human meaning:** The book of law your agents are supposed to obey.
- **Authority:** AAA-HF defines what "correct," "safe," "governed," and "sealed" mean.
- **It does NOT:** Execute, route, display, or judge. It defines.

### AAA-Cockpit — GitHub Repo / Control Plane

- **Location:** https://github.com/ariffazil/AAA
- **Role:** Operations cockpit. The mission control room for the AI agent federation.
- **Contains:** React 19 cockpit UI, A2A protocol server, agent registry (`registries/agents.yaml`), routing contracts, observability configs, Supabase panel integration.
- **Human meaning:** Airport control tower — sees all agents, their status, their routes, who handles what next.
- **Authority:** AAA-Cockpit consumes and displays doctrine and records. It does NOT own F1–F13 judgment. It does NOT replace AAA-HF as constitutional authority.
- **It does NOT:** Define the law, apply constitutional floors, or execute irreversible actions.

### AAA-Doctrine — Constitutional Concept

- **Location:** Referenced in arifOS docs, Hugging Face README, governance specs.
- **Role:** The abstract constitutional meaning of AAA — the idea that every agent action must be accountable to alignment, authority, and auditability.
- **Use when:** Writing governance prose, constitutional analysis, or cross-organ reasoning about what "governed behavior" means.
- **It does NOT:** Map to a single repo. It is a conceptual layer, not a runtime surface.

### AAA-Interface — Operator Visibility Layer

- **Location:** Implemented via AAA-Cockpit (`aaa.arif-fazil.com`).
- **Role:** The human-facing surface that shows Arif what agents did, what is waiting for approval, what got refused, what got sealed, and what evidence was used.
- **Belongs to:** GitHub AAA repo (the UI layer).
- **Authority:** Display only. It does not override arifOS judgment or Supabase records.

### AAA-Eval — Benchmark and Evaluation Layer

- **Location:** Hugging Face dataset `ariffazil/AAA`, `eval/` directory.
- **Role:** Gold records and test harness for verifying whether agents obey arifOS constitutional law.
- **Use when:** Running benchmark tests, evaluating agent discipline, or checking floor compliance.
- **Belongs to:** AAA-HF primarily.

---

## Invariant Role Map

The following invariants must hold across all documentation and code:

```
AAA-HF       defines doctrine.
arifOS       applies doctrine.
MCP tools    execute only if allowed.
Supabase     records what happened under doctrine.
VAULT999     seals what must be permanent.
AAA-Cockpit  displays the governed state to Arif.
Arif         remains F13 final sovereign authority.
```

These roles must never be swapped:

- **Supabase is NOT the router, judge, or brain.** It is the court record.
- **AAA-Cockpit is NOT the constitutional authority.** F1–F13 and 888_JUDGE live in arifOS.
- **AAA-HF is NOT the cockpit.** It is the doctrine corpus.
- **arifOS is NOT just a tool server.** It is the runtime constitutional kernel.

---

## When to Qualify

Use the qualified term (`AAA-HF`, `AAA-Cockpit`, `AAA-Doctrine`, `AAA-Interface`, `AAA-Eval`) whenever:

1. Referring to a specific surface in technical documentation.
2. Distinguishing between the Hugging Face dataset and the GitHub repo.
3. Writing governance contracts or Supabase schema specs.
4. Documenting agent authority boundaries.
5. Any context where "AAA" alone could be interpreted two or more ways.

Use bare `AAA` only when the context makes the surface unambiguous (e.g., within the AAA-Cockpit README itself, referring to the cockpit by its own name).

---

## Quick Reference

```
AAA-HF        = the law book
AAA-Cockpit   = the control tower
AAA-Doctrine  = the constitutional principle
AAA-Interface = the viewing chamber
AAA-Eval      = the test harness

arifOS        = the judge and executive
MCP tools     = the hands
Supabase      = the court record
VAULT999      = the sealed archive
Arif          = the sovereign
```

---

## Memory Ecology (for completeness)

| Layer | Role |
|-------|------|
| Redis | Now — live session state |
| Qdrant | Similar — semantic recall |
| Graphiti | Related — relationship map |
| Supabase | Official — constitutional court record |
| VAULT999 | Final — immutable sealed archive |
| AAA-HF | Lawful — doctrine corpus and evaluation substrate |

---

## See Also

- [`docs/architecture/AAA_SUPABASE_RECORD_DOCTRINE.md`](./AAA_SUPABASE_RECORD_DOCTRINE.md) — How Supabase records trace back to AAA-HF authority
- [`docs/00_META/CONSTITUTION.md`](../00_META/CONSTITUTION.md) — F1–F13 constitutional floors
- [`docs/REPO_AUTHORITY_MATRIX.md`](../REPO_AUTHORITY_MATRIX.md) — Full organ authority map
- [Hugging Face dataset](https://hf.co/datasets/ariffazil/AAA) — AAA-HF doctrine corpus

---

*DITEMPA BUKAN DIBERI — Forged, not given.*
