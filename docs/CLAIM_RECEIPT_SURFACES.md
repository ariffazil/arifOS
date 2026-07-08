# Claim Receipt — Human and Agent Surfaces

See: GENESIS/020_ARIFOS_TRUTH_RECEIPT_DOCTRINE.md  
Schema: schemas/arifos_claim_receipt.schema.json  
Model: arifosmcp/arifos_vault/claim_receipt.py (ArifOSClaimReceipt)

## Human Surface (plain + challenge rights)

Use `receipt.to_human_proof()` or the template:

```
Claim:
<exact statement>

Why this is true:
<claim_type> at <evidence_layer> (L1=sealed canon, L2=live verified, L3=cached, L4=inference/analysis).

Authority:
<issuer> (<authority_level>) scope=<scope list>.

Evidence:
source=<uri> hash=<sha256 prefix> at <timestamp>.

Consequence:
Agents may prepare/execute only within verified layer + authority scope. L4 never irreversible.

How to challenge:
<falsification.challenge_method>. Correction: append-only (scar over erasure).

Verdict / Receipt:
<verdict> · <claim_id> v<receipt_version>
Replay: <replay_command>
```

If arifOS cannot answer the six questions (verify, disprove, authority, source, change-since, failure consequence) → degrade to UNKNOWN/HOLD.

## Agent Surface (verification contract)

Use `receipt.to_agent_contract()` or `verify_claim_receipt(receipt)`:

```json
{
  "claim_id": "claim-2026-07-08-001",
  "evidence_layer": "L2",
  "authority_scope": ["WEALTH", "A-FORGE", "arifOS"],
  "allowed_action": "prepare_only",
  "blocked_action": "execute_without_f13",
  "requires": ["valid_signature", "canon_hash_match", "not_expired", "not_superseded"],
  "on_fail": "HOLD",
  "replay_command": "verify_claim_receipt(claim_id)",
  "execution_gate": {
    "prepare": true,
    "irreversible": false,
    "reason_if_blocked": "L4 inference cannot trigger irreversible action"
  }
}
```

Execution rule (in model + kernel enforcement):

```
IF valid receipt AND layer sufficient AND scope matches AND not superseded/expired
THEN execute within band
ELSE HOLD
```

L4 inference is analysis only. Never canon. Never irreversible.

## Usage

```python
from arifosmcp.arifos_vault.claim_receipt import (
    create_claim_receipt, verify_claim_receipt, ArifOSClaimReceipt
)

rec = create_claim_receipt(
    claim_id="claim-2026-07-08-001",
    statement="WEALTH must not execute irreversible capital movement without F13 approval.",
    claim_type="governance_rule",
    evidence_layer="L2",
    issuer="ARIF / F13",
    authority_level="F13",
    scope=["WEALTH", "A-FORGE", "arifOS"],
    source_uri="arifOS/constitution/sections/irreversible.md",
    content_hash="sha256:deadbeef...",
    timestamp_utc="2026-07-08T12:00:00Z",
    valid_from="2026-07-08T12:00:00Z",
    verdict="VALID",
    # signature=...  # supply real sig from kernel seal
)

ok, msg, contract = verify_claim_receipt(rec)
human = rec.to_human_proof()
agent = rec.to_agent_contract()
```

All consequential claims must resolve to a receipt. No receipt = no canon.
