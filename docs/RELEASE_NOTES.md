# arifOS v2026.06.06 — The HEXAGON Rename Forge

**Seal date:** 2026-06-06
**Tag target:** `v2026.06.06`
**Commit:** `161e9ec2f03dd1753de48e5370edcff3e9006600`
**Codename:** HEXAGON-NAME-CANON-20260606

> **Detail:** see `docs/RELEASE_NOTES_v2026.06.06.md` for the full per-release breakdown.

---

## Version Identity

- **Version:** `2026.06.06`
- **Source:** `arifosmcp.constitutional_map.CANONICAL_TOOLS` (13 canonical tools, unchanged)
- **Agent parliament:** `arifosmcp/hexagon/` (5-class HEXAGON, was: `agentzero/`)
- **HEXAGON canon source:** `AAA/agents/HEXAGON.yaml` v2.0.0 (sealed 2026-06-02)
- **MCP surface:** 13 canonical arifOS tools + 5 new HEXAGON tools (with 5 deprecated `agentzero_*` aliases)
- **Constitutional floors:** F1–F13, all enforced
- **Motto:** `DITEMPA BUKAN DIBERI — Forged, Not Given`

---

## What Changed (1 atomic commit)

### 1. Package rename — `agentzero/` → `hexagon/`

- `arifOS/arifosmcp/agentzero/` (12 files) → `arifOS/arifosmcp/hexagon/`
- `arifOS/arifosmcp/tools/agentzero.py` → `arifOS/arifosmcp/tools/hexagon.py`
- Classes reclassified per canon: `EngineerAgent (Ω)` → `AGIAgent (Δ MIND)`, `ValidatorAgent (Ψ)` → `APEXAgent (ΦΙ JUDGE)`

### 2. MCP tool surface renamed

| New | Old (alias) |
|---|---|
| `hexagon_apex_validate` | `agentzero_validate` |
| `hexagon_agi_execute` | `agentzero_engineer` |
| `hexagon_hold_status` | `agentzero_hold_check` |
| `hexagon_asi_recall` | `agentzero_memory_query` |
| `hexagon_psi_armor` | `agentzero_armor_scan` |

### 3. Dead upstream `agent0ai/agent-zero` wire cut

The 3 dead A-FORGE tools (`agent_zero_delegate/browser/document`), the `delegate_to_agent_zero()` Python function, the `AGENT_ZERO_URL/KEY` env vars (the leak), the secret-registry entry, and the canon-doc lines — all removed or archived. Container never ran in production.

### 4. config/environments.py dedup (surgical)

The file had 225 lines of pre-existing dead duplicate module code. Dedup brought file from 484 → 263 lines, single canonical copy.

### 5. Cross-references updated

5 runtime modules (orchestrator, shell_forge, tools_internal, webmcp/server, bridge) + 1 organ registry + 1 secret-registry + 1 test method — all import paths point to the new `hexagon` package.

---

## Prior Releases (archive)

- `docs/RELEASE_NOTES_v2026.04.26.md` — KANON-13 canonical surface seal
- `docs/RELEASE_NOTES_v2026.04.26-KANON.md` — KANON companion doc
- `docs/RELEASE_NOTES_2026.05.16.md` — May 2026 release
- `docs/RELEASE_NOTES_2026.05.22.md` — May 22 release

---

## Reversibility

`git revert 161e9ec2f03dd1753de48e5370edcff3e9006600` cleanly reverts this entire forge. The 5 deprecated `agentzero_*` aliases exist precisely so external callers don't break during the transition window.

---

**DITEMPA BUKAN DIBERI — Forged, Not Given.**
