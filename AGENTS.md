---
compartment: A2M
authority_ceiling: 666_JUDGE / 888_APEX
organ: arifOS
port: 8088
vault_port: 8100
role: Constitutional Kernel & Immutable Ledger
canonical_ref: /root/AGENTS.md
---

# AGENTS.md — arifOS Constitutional Kernel

> **CANONICAL INVARIANT:** REALITY > EVERYTHING.  
> **APEX ZEN:** A2A delegates ⊥ MCP equips ⊥ ACT mutates ⊥ arifOS governs ⊥ F13 decides.  
> **MOTTO:** DITEMPA BUKAN DIBERI ⚒️

---

## 1. The Witness & Attention Quintet
```text
Chat preserves attention.
Markdown preserves witness.
Graphs preserve relationships.
Governance preserves consequence.
Reality determines survival.
```

---

## 2. What arifOS Is and Owns

arifOS is the **Constitutional Kernel** of the federation. It is the sole authority that evaluates claims against the 13 Constitutional Floors (F1–F13) and issues binding verdicts.

* **Port 8088:** Live kernel REST/HTTP & FastMCP interface (`/health`, `/tools`, `/mcp`, `/status`).
* **Port 8100:** VAULT999 internal viewer (append-only immutable ledger with 342,000+ sealed records).
* **Canonical 8-Verb Chain:**
  ```text
  arif_init → arif_observe → arif_think → arif_route → arif_memory
            → arif_judge → arif_forge → arif_seal
  ```
* **Only `arif_seal` writes to VAULT999.**
* **Only `arif_judge` issues constitutional verdicts:** `SEAL`, `HOLD`, `VOID`, `SABAR`.

---

## 3. Constitutional Boundaries (Can & Cannot)

| Layer | Can | Cannot |
|:---|:---|:---|
| **arifOS** | Judge evidence, enforce F1–F13 floors, seal immutable receipts to VAULT999, issue verdicts | **Execute code mutations**, run arbitrary shell commands, bypass human sovereign (F13) |

* **Invariant: Capability ≠ Authority.** Identity, capability, availability, callability, permission, and wisdom are strictly separate.
* **Separation of Powers:** arifOS governs and judges; A-FORGE executes; Domain organs (GEOX, WEALTH, WELL) witness; arif-fazil.com hosts the surface; F13 sovereign (Arif) decides.

---

## 4. Governed Witness Mutation Protocol

Any mutation to canonical kernel code or state must follow the 8-stage protocol:
```text
1. AUTHORIZE → Verify F13 lease or ratified verdict.
2. BACKUP    → Create timestamped snapshot (.bak-<timestamp>).
3. MUTATE    → Apply surgical, minimal diff.
4. VERIFY    → Run python test suite and `arif_init` deterministic probe.
5. REINDEX   → Recompute kernel SOT hashes (`kernel-sot.yaml`).
6. RELINK    → Re-verify inter-organ schema links.
7. WITNESS   → Append audit receipt to VAULT999.
8. NOTIFY    → Report status in concise human language.
```

---

## 5. Local Verification Commands

```bash
# Verify kernel health and live SOT
curl -s http://127.0.0.1:8088/health | jq .

# Verify MCP tools list
curl -s -X POST http://127.0.0.1:8088/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | jq .
```
