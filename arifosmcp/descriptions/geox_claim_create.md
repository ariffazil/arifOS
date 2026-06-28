# geox_claim_create — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/geox_claim_create.md
# Organ: geox
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Create a new geological claim. Now requires `symbolic_consequence` (map_symbol, reserve_booking_risk, investment_signal, institutional_liability, confidence_symbol.p10_p50_p90_present).

## do_not_use_when
- reserve_booking_risk=true and confidence_symbol.p10_p50_p90_present is false
- institutional_liability=true and no maruah check has been performed
- the claim is purely speculative without L1 evidence_layer

## universal_pre_action_block
Before invoking this tool, complete the 9-axis symbolic pass:
1. literal_request
2. symbolic_meaning
3. authority_implied
4. authority_verified
5. symbol_owner
6. reversibility
7. social / cultural consequence
8. correct existing tool route
9. whether HOLD is required

If any of the above cannot be completed, do **not** invoke the tool.
Apply Rule Zero: a bare `seal` token without domain qualifier triggers
seal_token_guard quarantine.

DITEMPA BUKAN DIBERI — Forged, Not Given.
