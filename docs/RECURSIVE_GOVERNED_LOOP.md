# Recursive Governed Loop — INIT ↔ SEAL Alignment

**Authority:** F13 SOVEREIGN  
**Canon:** `docs/000-999_CANONICAL_MAPPING.md`  
**Driver:** `commands/scripts_deploy/recursive_governed_loop.py`  
**Motto:** DITEMPA BUKAN DIBERI

---

## One geometry, two resolutions

| Resolution | Stages | Use when |
|------------|--------|----------|
| **11-stage constitutional** | 000→999 full paradox path | Audit, human review, high blast |
| **5-stage metabolic** | PERCEIVE→PROPOSE→EVALUATE→SOVEREIGN→SEAL | Runtime pump, agents, recursion |

They are the **same law** at different zoom. Never invent a third numbering.

---

## Live tool alignment (Hermes aliases fixed)

| Stage | Canon name | **Live tool** | Do not use |
|-------|------------|---------------|------------|
| 000 | INIT | `arif_init` | `arif_session_init` |
| 111 | SENSE | `arif_observe` | — |
| 222 | EVIDENCE | `arif_observe` / organ via `arif_route` | `evidence_fetch` |
| 333 | REASON | `arif_think` | `agi_reason` |
| 444 | ROUTE | `arif_route` | `kernel_route` |
| 555 | MEMORY | `arif_memory` | `memory_recall` alone |
| 666 | GOVERN | `arif_critique` | `heart_critique` |
| 777 | MEASURE | inside `arif_judge` | — |
| 888 | JUDGE | `arif_judge` | self-judge |
| 889 | PROOF | `arif_verify` | invented SEAL validity |
| 999 | SEAL | `arif_seal` | `arif_vault_seal` |
| ACT | EXECUTE | `arif_forge` **after** SEAL | ungoverned shell |

---

## ART → APA → ACT (recursive)

```
┌──────── ART ────────┐   ┌──── APA ─────┐   ┌────── ACT ──────┐
│ 000–444             │ → │ verified     │ → │ forge / seal    │
│ classify, observe,  │   │ session +    │   │ only if 888=SEAL│
│ reason, route       │   │ arif_verify  │   │ + F13 ack       │
└─────────────────────┘   └──────────────┘   └─────────────────┘
         ▲                                            │
         └──────── recursion on HOLD/SABAR ───────────┘
                   (prior receipt becomes evidence)
```

**F13:** Hermes may **use** a sovereign-bound session. Hermes never **is** SOVEREIGN.

---

## SEAL validity (non-negotiable)

| Gate | Rule |
|------|------|
| Judge | Verdict must be **SEAL** (not HOLD/SABAR/VOID) |
| G | `G = A·P·E·X·Φ ≥ 0.80` (estimate labeled ESTIMATE until measured) |
| C_dark | `< 0.30` |
| W³ | Human × AI × External — none zero for high-stakes |
| Actor | `actor_verified=true` for irreversible |
| Ack | `ack_irreversible=true` from Arif for vault append |
| Padlock | `arif_verify` for IRREVERSIBLE shell before A-FORGE |

No SEAL if any gate fails. STOP is always lawful.

---

## How to run

```bash
# Dry path (no vault write) + sovereign crypto bind
python3 /root/arifOS/commands/scripts_deploy/recursive_governed_loop.py \
  --intent "Your governed intent" \
  --sign-sovereign \
  --no-seal \
  --max-depth 2

# Real seal only after judge SEAL + your F13 ack
python3 /root/arifOS/commands/scripts_deploy/recursive_governed_loop.py \
  --intent "Your governed intent" \
  --sign-sovereign \
  --ack-irreversible
```

Receipts land in `/root/A-FORGE/forge_work/YYYY-MM-DD/RECURSIVE_GOVERNED_LOOP_RECEIPT.json`.

---

## Recursion rule

1. Complete metabolic pass.  
2. If **VOID** → stop.  
3. If **SEAL** + ack → `arif_seal` once → stop.  
4. If **HOLD/SABAR** and depth < max → re-enter PERCEIVE with prior stages as evidence (ΔS ≤ 0 target).  
5. Cap depth (default 2–3). Infinite loops are VOID (F4/F9).

---

*Aligned 2026-07-10 — Wire Init+Seal into recursive governed agentic intelligence.*
