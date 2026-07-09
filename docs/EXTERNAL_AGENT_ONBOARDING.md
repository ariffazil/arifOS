# External Agent Onboarding Protocol v1

> **Status:** Executable (code) + operational checklist  
> **Modules:** `arifosmcp.runtime.agent_onboarding` · `arifosmcp.core.enforcement.sfag` · `governance_alerts`  
> **Rule:** Unknown actors may observe. Mutation requires commission.

## Why

Hermes (Telegram), OpenClaw, VPS agents are not "aligned" by prompt.
They become subjects under arifOS only when:

1. **Card** — AAA agent-card exists  
2. **Key** — Ed25519 public PEM registered  
3. **Handshake** — `arif_init` with `actor_signature`  
4. **Scar** — SFAG tracks cumulative scar; `governance_alerts.log` records every G_threshold raise  

## Status lattice

| Status | Card | Key | Mutation |
|--------|------|-----|----------|
| COMMISSIONED | ✓ | ✓ | lease-gated only |
| CARD_ONLY | ✓ | ✗ | OBSERVE_ONLY |
| KEY_ONLY | ✗ | ✓ | quarantine |
| UNKNOWN | ✗ | ✗ | HOLD on mutate |

## Operator steps

```bash
# 1. Ensure keys dir
python -c "from arifosmcp.runtime.agent_onboarding import ensure_keys_dir; print(ensure_keys_dir())"

# 2. Drop public key
#    /root/.local/share/arifos/agent_keys/hermes-asi.pem

# 3. Assess fleet
python -c "from arifosmcp.runtime.agent_onboarding import commission_checklist; import json; print(json.dumps(commission_checklist(), indent=2))"

# 4. Weekly worst agents (scar / G_threshold raises)
python -c "from arifosmcp.core.enforcement.governance_alerts import worst_agents; print(worst_agents())"
```

## Handshake (required before mutate)

```
arif_init(
  mode="init",
  actor_id="<commissioned_id>",
  actor_signature=<Ed25519 over session nonce>,
  requested_authority="EXECUTE_APPROVED"  # never self-SOVEREIGN
)
→ session_id bound
→ SFAG evaluate_sfag on any mutation proposal
→ IRREVERSIBLE still F13
```

## Alerts path

`/root/.local/share/arifos/governance_alerts.log` (JSONL, append-only)

Event: `G_THRESHOLD_RAISE` when dynamic G rises with cumulative scar S_w.

## Iron rule

Never open production mutation to UNKNOWN.  
Card without key is not commission.  
Commissioned is not sovereign.
