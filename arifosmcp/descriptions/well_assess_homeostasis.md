# well_assess_homeostasis — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/well_assess_homeostasis.md
# Organ: well
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Assess biological and psychological homeostasis. Now emits `homeostasis_symbolic_layer` so vitality numbers don't become identity symbols.

## do_not_use_when
- telemetry is stale or degraded (status != available)
- vitality read would become a public identity claim without consent

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
