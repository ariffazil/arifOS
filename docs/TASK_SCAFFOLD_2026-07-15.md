# arifOS Task Scaffold — Entropy Reduction, APEX Refactor & Alignment

> **Epoch:** 2026-07-15 | **Status:** Active | **Sovereign:** Arif (F13)
> **Source:** Sovereign directive via OpenCode session 2026-07-15

## Execution Order

| Phase | Task | Blocking? | Status |
|---|---|---|---|
| P0 | P0-01 Floor coverage matrix | Blocks P1-03 | QUEUED |
| P0 | P0-02 VAULT chain verify | Blocks P4-02 | QUEUED |
| P0 | P0-03 smithery ↔ registry sync | Blocks P3-02 | QUEUED |
| P1 | P1-01 ZEN.md entry point | No | QUEUED |
| P1 | P1-02 Test coverage gap scan | Blocks P1-03 | QUEUED |
| P1 | P1-03 Hard floor tests | Depends P1-02 | QUEUED |
| P1 | P1-04 Memory audit | No | QUEUED |
| P1 | P1-05 Provider fallback verify | No | QUEUED |
| P2 | P2-01 ATP scaffold | Blocks P2-02 | QUEUED |
| P2 | P2-02 Wire ATP to forge [F13 GATE] | **F13 required** | BLOCKED |
| P2 | P2-03 Scalar feed protocol | Blocks P4-01 | QUEUED |
| P2 | P2-04 Anti-Calhoun in heart_critique | No | QUEUED |
| P3 | P3-01 Supabase schema align | No | QUEUED |
| P3 | P3-02 GitHub Actions floor gate CI | No | QUEUED |
| P3 | P3-03 copilot-instructions.md | No | QUEUED |
| P3 | P3-04 A2A federation mesh health | No | QUEUED |
| P4 | P4-01 apex_scalars in /health | After P2-03 | QUEUED |
| P4 | P4-02 Audit trail completeness | After P0-01 | QUEUED |

## Key Architecture Notes

- Floor enforcement is in `core/shared/laws.py` (check_all_floors), NOT `core/floors.py`
- Judge floor check: `arifosmcp/runtime/kernel/judge.py` (_check_floors)
- RASA floor check: `arifosmcp/rasa/rasa_integration.py` (rasa_check_floors)
- 52 tool files in `arifosmcp/tools/`
- Constitutional tests: `tests/constitutional/` (~7 files)
- smithery.yaml at repo root, tool_registry.json at arifosmcp/

## Full scaffold preserved in sovereign session memory (2026-07-15)
