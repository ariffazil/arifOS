# arif_seal — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/arif_seal.md
# Organ: arifos
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Seal a verdict or outcome to the immutable audit ledger. The input MUST carry `seal_disambiguation` distinguishing geological_seal / constitutional_SEAL / vault_seal / trap_seal_lithology.

## do_not_use_when
- input contains a bare 'seal' token without domain qualifier (Rule Zero)
- symbol_owner is not verified
- no prior arif_judge verdict exists for this outcome
- the outcome is reversible — seal only when irreversibility has been declared

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
