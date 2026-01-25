# Seal + Memory (999 Vault)

## Purpose
Close the loop: record what happened, what changed, and why it is safe to deliver.

## Human-Language Rule
"Do not seal what cannot be justified; log what you changed."

## Constitutional Mapping
- Floors: F1 Amanah, F8 Tri-Witness, F10 Ontology Lock
- Trinity role: Vault / Seal (Lock)
- Physics constraint: Immutable audit trail

## Required Actions
1. Summarize the final state and key changes.
2. Capture verification status (tests run, checks skipped, risks remaining).
3. Preserve an auditable trail (file paths, decisions, rationale).
4. If incomplete, do not seal; return PARTIAL or SABAR.

## Optional Commit and Log
If using git and you have approval to commit:
- `git add -A`
- `git commit -m "[SEAL] <short description>"`
- `git push origin <branch>`

If a session memory file exists:
- Append a short seal note to `.codex/codexbrain.md`.

## Output Contract
- A final seal statement with what was done and what remains.
- Clear traceability to files or actions.

## Failure Conditions (Do NOT proceed)
- No audit trail.
- Unjustified sealing of uncertain work.
- Blurring real vs assumed information.
