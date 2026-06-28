# arif_forge — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/arif_forge.md
# Organ: arifos
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Execute approved builds, deployments, or system changes only after a verified arif_judge SEAL. Now requires the `forge_precheck` gate — if symbolic authority is uncertain, FORGE must dry_run only.

## do_not_use_when
- symbolic approval is present but constitutional approval is absent
- user says 'seal' ambiguously (must run seal_token_guard first)
- authority chain is missing (no prior arif_judge verdict)
- action is irreversible and ack_irreversible is false
- false_symbol_risk=high and dry_run_only is not set
- forge_precheck.judge_verdict_present is false
- forge_precheck.symbolic_authority_verified is false

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
