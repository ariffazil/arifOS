# arif_think — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/arif_think.md
# Organ: arifos
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Multi-step reasoning, planning, and reflection with explicit confidence labeling. Now requires the 6-axis symbolic_reasoning_pass for any non-trivial task.

## do_not_use_when
- task is trivial and the 6-axis pass would be theatre
- no symbolic_reasoning_pass was completed (degraded reasoning mode)
- structural reasoning is collapsing — fall back to arif_observe for grounding

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
