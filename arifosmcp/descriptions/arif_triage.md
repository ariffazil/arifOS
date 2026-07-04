# arif_triage — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/arif_triage.md
# Organ: arifos
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Classify an inbound action into a triage lane (constitutional, domain, observational, ritual, exploratory) before any tool is called.

## do_not_use_when
- symbolic context is unclear — must HOLD until the 9-axis pre-action pass is complete
- user says 'seal' or 'approve' without domain qualifier
- authority chain (arif_judge verdict → arif_seal → arif_forge) is broken
- social_blast_radius implies irreversibility but symbol_owner is unknown

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
