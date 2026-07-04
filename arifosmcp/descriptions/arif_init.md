# arif_init — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/arif_init.md
# Organ: arifos
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Start or resume a governed constitutional session. Now requires `symbolic_context` (actor_identity, role_claims, cultural_frame, session_mode, symbolic_risk_profile).

## do_not_use_when
- actor identity is not verifiable
- session is in opt_out mode and symbolic_context cannot be collected
- previous session hash is broken or unrecorded

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
