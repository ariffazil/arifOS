# arif_observe — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/arif_observe.md
# Organ: arifos
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Search the web, ingest URLs, check system vitals. Now classifies source_symbol_class (legal_document, corporate_statement, ritual_text, etc.) and emits interpretation_warning.

## do_not_use_when
- source is already classified and observation is redundant
- interpretation_warning has not been emitted (always emit for non-trivial sources)
- request is performative rather than informational

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
