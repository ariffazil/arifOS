# arifOS Chapter 6 Upgrade — Agent Collaboration Log

**Authority:** F13 SOVEREIGN (Arif Fazil)
**Branch:** `feat/ch6-wakefulness`
**Started:** 2026-06-05
**Agents:** Kimi (primary) + OpenCode (parallel)

---

## Shared Contract: FederationEnvelope v1.1

All tool handlers may now optionally accept an `envelope: FederationEnvelope` parameter.
The envelope is injected by `IngressToleranceMiddleware` and forwarded by `_wrap_handler`.

```python
from arifosmcp.schemas.federation_envelope import FederationEnvelope

async def my_tool_handler(..., envelope: FederationEnvelope | None = None):
    if envelope:
        actor_id = envelope.actor_id
        risk_tier = envelope.risk.tier
        # ... use envelope fields
```

Legacy handlers without `envelope` param work unchanged.

---

## Work Division

### Kimi (Completed / In Progress)
- [x] `schemas/federation_envelope.py` — Add lineage fields (judge_state_hash, vault_entry_id, constitutional_chain_id)
- [x] `runtime/ingress_middleware.py` — Inject validated envelope into msg.arguments
- [x] `runtime/tools.py` — `_inject_envelope_into_kwargs` helper, forward envelope to envelope-aware handlers
- [x] `runtime/kernel.py` — Prefer envelope fields for session_id/actor_id extraction
- [ ] `schemas/evidence.py` — Add `CertaintyCap` enum
- [ ] `runtime/organ_governance.py` — Enforce certainty caps per tool
- [ ] `runtime/kernel.py` — Pre-dispatch wakefulness gate (WELL integration)
- [ ] `tools/ops.py` — `human_wakefulness` mode

### OpenCode (Requested)
- [ ] `runtime/ingress_middleware.py` — Host attestation parsing (x-host-attestation header)
- [ ] `runtime/organ_governance.py` — Dynamic CAN/MAY/SHOULD capability map
- [ ] `tools/heart.py` — `meaning_boundary` mode
- [ ] `runtime/shadow_defense.py` — P6 certainty overclaim, P7 meaning capture patterns
- [ ] `deploy/vault999-writer/main.py` — Sync responsibility ledger fields
- [ ] Supabase migration — `vault_sealed_events` new columns

---

## Daily Sync Protocol

1. Each agent commits to their own branch:
   - Kimi: `feat/ch6-p0-envelope-kimi`
   - OpenCode: `feat/ch6-p0-envelope-opencode`
2. End of day: merge both into `feat/ch6-wakefulness` integration branch.
3. Update this COLLAB.md with status.
4. Run `pytest tests/constitutional/ -q` before any merge.

---

## Blockers / Questions for Arif

1. **WELL biometric injection** — `state.json` is stale. Wakefulness gate needs live data.
2. **VAULT999 chain repair** — 120 gaps. Responsibility ledger needs clean chain before P3.
3. **F14 MEANING_BOUNDARY** — New floor or fold into F6 DIGNITY?

---

*Last updated: 2026-06-05 | DITEMPA BUKAN DIBERI*
