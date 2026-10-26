# Lane B Gate Prep — ARIF GO required (branch fix/honest-green-2026-10-25)

Prepared 2026-10-25 03:0x +08. NOTHING below has been executed. Ordered by
recommended GO sequence. Each entry: plan (diff/artifact ready) · risk · rollback.

## B2' — Sign-fail annotation consumption (RECOMMEND GO FIRST — smallest, pure add)
- Plan: extend canonical_vault_chain annotation consumption so a signed supersede
  (or explicit signed annotation) reclassifies a target SIGNATURE_FAIL gap as
  explained — same pattern as existing CHAIN_BREAK annotations (test:
  test_chain_annotation_consumption.py gets the signature-gap case). The keyless
  WRITE guard itself is ALREADY deployed (e62a940, default ON, tested) — no new
  write-path change.
- Risk: an explained-but-unverified signature gap could read greener than it is
  → mitigation: reclassification requires a SIGNED annotation record, display
  keeps gap_class visible with explained_by set.
- Rollback: revert the single commit; annotations are append-only sidecars
  (existing rows untouched).

## B1 — Deploy fix/honest-green to production
- Plan: rebuild wheel from branch head (arifOS `17b678129`+), install to
  /opt/arifos, `systemctl restart arifos` (kernel unit — R5/F13 lane), copy
  `scripts` branch `pulse/index.html` → `/var/www/html/arif/pulse/index.html`,
  verify /health owner_summary shows presence_only-YELLOW behaviour + pulse
  page shows governance line. Deploy-state-delta receipt required.
- Risk: kernel restart kills in-flight sessions (sovereign lanes) — schedule
  quiet window; capability row now 9 rows → any consumer assuming 8 rows needs
  the A5 note.
- Rollback: reinstall previous wheel (e62a940 build retained), restore served
  index.html from pre-copy backup, restart.

## B3 — P1-5/P1-6 failure-mode retest on target release
- Plan: settlement record (binari-settlement row 4) — 4 failure-mode tests
  (retry, duplicate, restart, writer-failure) are the release gate; run them on
  the target release AFTER B1 (branch code live), each with receipt; base canary
  already PASS 04:20Z (2026-10-24 per settlement).
- Risk: test harness touches chain append paths → run only with SIG_ENFORCE ON
  and vault isolation fixtures; writer-failure test must be proven non-destructive
  (no chain drop).
- Rollback: each test is scenario-scoped; restore fixture state from test tmp;
  release rollback = same as B1 rollback.

## B4 — OS-1 wiring arifOS → arifFLOW
- Plan: OS-1 (edge overlay + executor receipt hook) is recorded as a PARALLEL
  AGENT's active lane with explicit "DO NOT DUPLICATE — coordinate via A-FORGE
  dirty state before touching" (open_loops 2026-10-23) and settlement row 5
  "Terikat wiring OS-1; OS-1 = kerja bina". Prepare = coordinate with owner lane
  + read A-FORGE dirty state first; no diff drafted here by design (ownership).
- Risk: duplicate/conflicting wiring if built blind — the reason it's gated.
- Rollback: n/a (no change made); ownership check is the control.

## B5 — Threshold decision (from A4)
- Plan: Arif picks: (1) SOT file (proposal: contracts/floor_policy.yaml promoting
  core/shared/laws.py values unchanged), (2) F3 binding value 0.75 vs 0.95,
  (3) TRM 0.94 tag retag-or-retune. Machine change = one-table edit after the
  ruling + table/verdicts.py alignment.
- Risk: lowering any threshold to pass a floor is FORBIDDEN (invariant 2) — only
  ratified alignment, values chosen by sovereign.
- Rollback: revert alignment commit (values unchanged in this branch).

## B6 — Thaw AAA / auth-hardening Phase 2 push
- Plan: read /root/work/aaa-auth-preservation/PHASE2-HANDOFF.md (3 Phase-1
  artifacts) → clean-clone ariffazil/AAA@180ec14c, apply witnessed auth delta,
  4 commits A-D, A1/A2/A3 gates, push branch preserve/live-auth-hardening-2026-10-24.
  THIS entry includes the AAA THAW decision (invariant: AAA currently frozen
  immutable) — two sovereign acts: thaw authorization + push authorization.
- Risk: AAA is constitutional substrate — thaw window must be time-boxed; push
  target branch only (never main).
- Rollback: re-freeze (chattr +i) after push; branch deletion if delta wrong.

## B7 — arif_judge → arif_seal (VAULT999 append)
- Plan: 888-APEX verdict (Gödel: author ≠ judge — 333-AGI may not self-judge)
  over the branch outcome → arif_seal with judge_state_hash, ack_irreversible.
- Risk: append is permanent (no unseal); content must be final.
- Rollback: none by design — superseding append is the only correction path
  (which is exactly why B2' matters first).

## STOP conditions re-checked before any GO
- new chain gap beyond the 5 known: NONE observed (set stable, 277 rows).
- credential/key material: only kid labels read (ed25519:sha256:698cc1ab…,
  vault-hmac-1) — no key material touched.
- production state: unchanged by Lane A (no deploy, no restart, no push, no
  external action, branch-only files, suite ran with vault isolation).
