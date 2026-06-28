# geox_claim_seal — Hardened Description
# MCP-SYMBOLIC-HARDEN-v1 §7
# Real path: /root/arifOS/arifosmcp/descriptions/geox_claim_seal.md
# Organ: geox
# Mode: APPEND-ONLY — do not edit the canonical tool description; append this block.

## purpose
Seal a geological claim with proper domain disambiguation. **MANDATORY** seal_disambiguation block — ties to Rule Zero.

## do_not_use_when
- seal_disambiguation is missing (Rule Zero violation)
- claim is still under challenge (cannot seal a contested claim)
- claim is a trap_seal_lithology but constitutional_SEAL is being requested

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
