# F13 FINAL CHECKLIST — PREDICATE DOMINANCE MAP (2026-10-23)

Question: for each enforcement predicate, which execution paths does it
DOMINATE, and which paths reach consequences WITHOUT passing it?
Defect class: 'gate tidak berada di semua laluan consequence'.

## Predicates found (file:line verified on arifOS @ 257c146bf)

| Predicate | Lokasi | Apa ia gate-kan |
|---|---|---|
| `check_laws()` | `arifosmcp/runtime/law.py` (def ~632-area) | tool wrappers di `arifosmcp/tools/*` yang memanggilnya secara eksplisit (kernel_canonical ×5, forge_ladder ×3, base ×2, memory ×2, shadow_geometry ×2, appeal/evidence/forge/gateway/metabolize/ops/reason/reply/resource_audit/sense/session ×1 setiap satu) + `arifosmcp/core/governance_kernel.py` + `runtime/governance_pipeline.py` + `runtime/memory_gate.py` ×6 |
| `check_floor_constraint()` | `arifosmcp/runtime/law.py:632` | RECALL intent pada memory yang bawa floor constraint: `runtime/memory_store.py:1468` dan `runtime/memory_handlers_v5.py` (×4). Ia gate AKSES kepada memory ber-Δ; ia TIDAK memadam apa-apa |
| `_check_floors()` | `arifosmcp/runtime/kernel/judge.py:306` | kernel judge path (`kernel/judge.py:102`) + rasa wiring (`rasa/rasa_integration.py`, `rasa_wiring.py`, `rasa/__init__.py`) |
| session auth + irreversible ack | `runtime/tools.py:22631` (`validate_session` dalam `_arif_vault_seal_tool`) | arif_seal / arif_vault_seal semua mode; kernel eval untuk seal bukan-RECORD (tools.py ~21431-21445); RECORD seal (ack=False) skip constitution kernel secara reka bentuk |
| IRFAN | `runtime/irfan_review.py` | TIADA. Advisory sahaja — lihat verdict di bawah |

## Paths NOT gated (bypass paths — dokumentasi, bukan dakwaan exploit)

1. **`runtime/tools.py::_arif_ops_measure`** (baris 19195-19577): TIADA
   `check_laws`, TIADA `validate_session` dalam function body. `_hold` hanya
   untuk input validation (estimate<0, unknown mode). Semua mode health/
   vitals/topology/drift/frame_* berjalan tanpa floor gate. (Dalam
   `arifosmcp/tools/ops.py:113`, wrapper `arif_measure` PUNYA check_laws —
   dua permukaan untuk tool yang sama, satu gated satu tidak.)
2. **`runtime/chatgpt_integration/apps_sdk_tools.py`** (369 baris): TIADA
   rujukan check_laws/check_floor/gate. Tiga tool (`vault_seal_card`,
   `render_vault_seal`, `get_constitutional_health`) — semua
   `readOnlyHint: true` dan pembina widget, jadi consequence terhad;
   `vault_seal_card` menerima `verdict` + `floors` sebagai INPUT bebas
   (caller boleh bina kad seal dengan verdict lesen) — paparan, bukan
   pengesahan. Bukan pada wire lalai: `register_chatgpt_app_tools` tidak
   diimport oleh `arifosmcp/server.py` (hanya test memanggilnya) — LATENT.
3. **ChatGPT shim** (`tools/chatgpt_shim.py`): `arif_search`/`arif_fetch`
   route ke `_arif_sense_observe`, yang juga TIADA check_laws/validate_session
   (hold hanya untuk bridge error F2). Read-only, idempotent — consequence
   rendah, tapi terkeluar dari floor gate.
4. **~30 lagi tools/*.py tanpa check_laws** (browser, telegram, somatic,
   stage, commit, heal, drift_check, judge, kernel, planner, vault, dsb.):
   sebahagian read-only, sebahagian ada mekanisme auth sendiri — setiap satu
   perlu audit berasingan; TIDAK diambil di sini sebagai bukti pelanggaran,
   hanya sebagai jurang liputan yang diukur.

## IRFAN VERDICT (final checklist #4)

**IRFAN = advisory (finding ignored without consequence).**

Kod yang memutuskan:
- `irfan_review.py:33-37, 83-85`: ADVISORY INVARIANT binding — verdict IRFAN
  TERLARANG menjadi SEAL/SABAR/HOLD/VOID; `_guard_advisory_output` (baris
  ~947-958) raise jika cuba.
- `runtime/tools.py:4171-4195`: IRFAN dikira SELEPAS `_CORE.evaluate(ctx)`
  dan "NEVER fed back into it"; exception → `IRFAN_LAST_REVIEW.set(None)`.
- `runtime/tools.py:9584-9590, 10017-10022`: hasil IRFAN dilampirkan sebagai
  `meta_payload['irfan_review']` — metadata sahaja.
- `runtime/verdict.py:717-733`: `meta.irfan_review.verdict` tersenarai dalam
  `_NON_VERDICT_AXIS_PATHS_SUF` — laluan ini dikecualikan daripada closed-token
  verdict check, jadi ESCALATE tidak boleh menjana HOLD.
- `runtime/reality_loop.py:427-437`: `annotate_with_irfan` dalam try/except
  pass — "advisory — the receipt above stands unchanged". Fail-open.

ESCALATE (severe dignity breach, weakest-stakeholder displacement —
irfan_review.py:156, 437, 453, 896) mengalir ke meta dan berhenti di situ.
Tiada satu baris kod pun menukar ESCALATE menjadi HOLD/blocked mutation.

**Apa yang menjadikannya binding (SPESIFIKASI SAHAJA — TIDAK diimplement,
keputusan kelas F13):** dalam `_CORE.evaluate` path (tools.py ~4160),
sebelum verdict dimuktamadkan: jika `IRFAN_LAST_REVIEW` (atau panggilan
semula `irfan_review_for_action`) == ESCALATE DAN action_class ∈
{MUTATE, EXTERNAL_SIDE_EFFECT, IRREVERSIBLE} → verdict dipaksa HOLD dengan
reason `IRFAN_ESCALATE_DIGNITY`. Read-only path dikecualikan (elak
paternalisme ke atas observe). Risk: IRFAN jadi single-point-of-failure dan
false-positive ESCALATE menyekat kerja sah — perlu threshold + override
berlainan-signing F13. Inilah perbezaan 'witness' vs 'gate'.
