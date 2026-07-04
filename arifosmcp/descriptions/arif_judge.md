# arif_judge — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/arif_judge.md
# Organ: arifos
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Render final constitutional verdict on a proposed action. Now requires `symbol_owner` to be verified — unknown → refused.

## do_not_use_when
- symbol_owner == unknown (spec §3.E hard rule: refuse judgment)
- no prior arif_triage lane assignment
- verdict is requested but evidence_receipt.symbolic_context is incomplete
- the action is irreversible and authority_verified is False

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
