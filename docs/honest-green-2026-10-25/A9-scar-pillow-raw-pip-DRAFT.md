# A9 — DRAFT SCAR: Pillow raw-pip (branch fix/honest-green-2026-10-25 — NOT canon)

status: DRAFT (branch file per brief; canonization is a separate sovereign act)
drafted_at: 2026-10-24T18:58Z (2026-10-25 03:00 +08) by 333-AGI (executor)

## Scar — SCAR-DRAFT-2026-10-24-PILLOW-RAW-PIP

**What happened (witnessed):** on 2026-10-24 a raw pip/uv dependency
intervention was attempted against the PM-managed HERMES environment during the
pillow/browser-harness validator deadlock; the raw-pip regression was
**cancelled** and 3 venvs were returned to pillow 13.0.0 (CVE basis) via the
PM/vendor path instead (hermes fork commit `2445a85bbf`, vendor
browser-harness with relaxed pin).

**Why it mattered:** HERMES environments are PM-owned
(`~/.hermes/installs/<sha>/…`); raw pip writes bypass
selection metadata (`facts.json`/`pm-runtime/selected.json`), desync
`uv.lock` validation, and re-open the exact permanent-sync failure class now
filed upstream as NousResearch/hermes-agent#144110 (GH API observed open,
created 2026-10-24T18:08:13Z).

**Rule (behaviour change):** never raw-pip into managed hermes envs; the only
repair lanes are `hermes pm install` / `hermes pm repair` / vendor-patch source
pyproject + `uv lock` — then restart gateway to pick it up.

**Evidence chain (lane search, observed 2026-10-25 02:5x +08):**
- CAPABILITY-CONTRACT-GAPS lane: `/root/work/staged-aaa/CAPABILITY-CONTRACT-GAPS-2026-10-24.md`
  L61-65 "ADDENDUM — pillow/PMD (2026-10-25, selesai) … Regresi raw-pip 2026-10-24
  dibatalkan; 3 venv kembali pillow 13.0.0 (dasar CVE)." ← the cancellation record
- HERMES memory lane: `/root/.hermes/state.db` messages — 15 matches
  ('raw pip' / 'pip install pillow', count-only probe, no content read)
- EUREKA lane: `/root/.local/share/arifos/eureka-entries.jsonl` — 1 'pillow'
  mention, 0 raw-pip entries
- AAA scars lane: `/root/AAA/scars/*.md` + `/root/AAA/knowledge/` — 0 pillow/raw-pip
  scars (content grep) — i.e. **no canon scar existed**, which is why this draft
  exists instead of a canon pointer.

**Not merged into canon (invariant 5 + AAA freeze):** this file lives only on
branch `fix/honest-green-2026-10-25`.

## A9b — HERMES cold boot timing (same lane, read-only)

Method: `hermes --version` timed ×3 from a shell, no service restart, no
mutation markers in output ('installing|repair|sync|update' = 0 on all runs),
rc=0 all runs. observed_at 2026-10-25 02:54 +08.

| run | wall |
|---|---|
| 1 | 1215 ms |
| 2 | 612 ms |
| 3 | 613 ms |

Verdict: the dependency boot tax is GONE (pre-fix: ~30s launcher retry/sync on
every launch, gateway start-to-warm ~60s incl. drain). The literal PDF claim
"10s boot (from ~60s)" is a different measurement axis (gateway full start) and
is **NOT measured here → UNPROVEN**; what IS verified: CLI cold launch ≤1.2s,
zero dependency work, on running source `+4042.g2445a85` (+9 carried commits).
