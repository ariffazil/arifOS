# arifOS MCP Tool Clarity Checklist (CANONICAL)

**Date:** 2026-07-08 (draft) · **Promoted:** 2026-07-12  
**Owner:** Arif (F13) / FORGE  
**Status:** CANONICAL — Phase B promote 2026-07-12
**Supersedes:** DRAFT forge_work/2026-07-08/ARIFOS-MCP-TOOL-CLARITY-SPEC.md  
**Trigger:** Runtime geometry audit of 12 public tools + `arif_init` light NameError

---

## 1. One-line law

**MCP “tools” are not tools — they are kernel verbs.**  
MCP is only the transport envelope. The 12 public names are constitutional stages of the arifOS metabolic loop (000→999).  
**MCP visibility ≠ arifOS authority.** Seeing a verb in the client ≠ being allowed to call it at that tier.

Wire copy lives in:
- `arifosmcp/runtime/public_registry.py` → `_TOOL_DESCRIPTIONS` (live tools/list)
- `arifosmcp/constitutional_map.py` → `CANONICAL_TOOLS` + `_TOOL_ANNOTATIONS` titles

---

## 2. UI must split three layers (never “Set all tools Always”)

| Layer | Meaning | Client label |
|-------|---------|--------------|
| **Visible** | Tool appears in tools/list | eye / list |
| **Callable L0–L2** | Allowed under current session authority | green / amber |
| **888_HOLD only** | Requires SOVEREIGN / HIGH / sealed chain | lock |

“Set all tools Always” confuses **client auto-approve** with **kernel authority**. Keep client auto-approve separate; always show authority badge from the last `arif_init` receipt.

---

## 3. Public 12 tools — badge + tier

| Wire name | Title | Badge | Default tier | Notes |
|-----------|-------|-------|--------------|-------|
| `arif_init` | Init Session | 🔐 | L0 pre-session | **Must succeed first** |
| `arif_triage` | Arif triage | 🧭 | L0–L1 | Session/preflight only — not intent router |
| `arif_observe` | Sense & Observe | 🔍 | L0 | Reality / vitals |
| `arif_think` | Mind Reason | 🧠 | L0 | Reason/plan — not verdict |
| `arif_route` | Route | 🗺️ | L0 | Intent → organ/tool (**preferred path**) |
| `arif_bridge_connect` | Bridge Connect | 🔗 | HIGH / internal | Direct organ call — **subset of route** |
| `arif_critique` | Heart Critique | ❤️ | L1 | Needs non-empty target |
| `arif_memory` | Memory Governor | 🧬 | L0–L1 | Recall free; write gated |
| `arif_judge` | Judge Deliberate | ⚖️ | 888_HOLD | Constitutional verdict |
| `arif_forge` | Forge Execute | 🔨 | 888_HOLD | Needs prior SEAL + lease |
| `arif_compose` | Arif compose | ✍️ | L0–L1 | Final response shape |
| `arif_seal` | Vault Seal | 🛡️ | 888_HOLD | VAULT999 append |

---

## 4. Redundancy rulings (keep, don’t merge blindly)

| Pair | Ruling |
|------|--------|
| **route vs bridge_connect** | Overlap, not clone. `route` may take `organ_tool` (bridge-like). **Agents use `route` only.** Mark `bridge_connect` **internal / HIGH** — not agent default. |
| **triage vs route** | Keep both. Triage = session status/preflight. Route = intent→organ. **Do not alias “route” into triage.** |

---

## 5. Agent embodiment order

```
arif_init(mode=light|init)  →  capture session_id + authority
arif_triage / arif_observe   →  ground state
arif_route                   →  pick organ/tool
arif_think / arif_critique   →  plan + heart (if needed)
arif_judge                   →  only when consequence requires verdict
arif_forge                   →  only with SEAL + lease
arif_seal                    →  only after valid SEAL path
arif_compose                 →  last, human-facing
```

Without verified `session_id`, expect **OBSERVE_ONLY / SYUBHAH / RETAK** even when tools are healthy. That is correct degradation, not “broken tools.”

---

## 6. Bug fixed this cycle (must land before UI polish)

| Bug | Cause | Fix |
|-----|-------|-----|
| `arif_init(mode=light)` → `Delegate init failed: name 'sess' is not defined` | `_project_light` clarity_contract read free var `sess` | Pass explicit `intent=` param; compute `_clarity_intent` before return dict |

**File:** `arifosmcp/tools/session.py` (`_project_light` + both call sites)  
**Deployed:** live `/opt/arifos/app` + `systemctl restart arifos` (2026-07-08)  
**Verify:** `arif_init(mode=light)` → `status=OK`, `verdict=SEAL`, `session_id=SEAL-*`, `actor_verified=true` (known principals → LIMITED_MUTATE)

---

## 7. Client UX acceptance criteria

1. No single “Always for all tools” that hides authority.
2. Each tool row: badge + tier + last deny reason if 888_HOLD.
3. Session chip always visible: `session_id` short + authority + actor_verified.
4. Default agent path never lists `bridge_connect` unless HIGH lease.
5. Empty critique target → soft hold message (“name a proposal”), not silence.

---

## 8. Next (optional)

- [ ] Hide `bridge_connect` from public `tools/list` (internal-only) after agent migration to `route`
- [ ] AAA cockpit badges matching §3
- [ ] Claude/Grok MCP permission UI copy: “auto-approve client ≠ kernel SEAL”

---

---

## 9. Affordance badge contract (cockpit / client)

| Badge | Meaning | Client must show |
|-------|---------|------------------|
| Visible | Present in tools/list | List row |
| Callable | Session authority allows | Green/amber chip |
| 888_HOLD | Needs SEAL / sovereign path | Lock + deny reason |

Rule: **client auto-approve ≠ kernel SEAL**. Always render last `arif_init` authority.

## 10. Phase B verification

- [x] Status ≠ DRAFT (this file)
- [x] Canonical path: `arifOS/docs/ARIFOS-MCP-TOOL-CLARITY-CHECKLIST.md`
- [x] AAA mirror: `AAA/docs/ARIFOS-MCP-TOOL-CLARITY-CHECKLIST.md`
- [ ] AAA cockpit UI badges (optional follow-on)

*Promoted 2026-07-12 Phase B. Does not change F1–F13. UI badges remain AAA surface work.*

