# DRAFT PR — F6 / MARUAH v0 Kernel & Actuator Implementation (`feat/f6-maruah-v0-20261023`)

> **Status:** DRAFT PR (Review Ready · NOT MERGED · NOT DEPLOYED · NOT SEALED)
> **Worktrees:**
> - Kernel (`arifOS`): `/root/arifOS-wt-f6` (branch `feat/f6-maruah-v0-20261023`)
> - Actuator (`A-FORGE`): `/root/A-FORGE-wt-f6` (branch `feat/f6-maruah-v0-20261023`)
> **Spec:** `specs/f6-maruah-spec-v0-draft.md` (v0.2 DRAFT, preserving Amendments 01–05 from `/root/AAA/forge_work/specs/f6-maruah-spec-v0-draft.md`)

---

## 1. Ringkasan Perubahan (Changes)

1. **P0 — Batas Tindakan Hingga Alat Terakhir (`authority_binding.py`)**:
   - Menyemak `scope`, `allowed_actions`, `resource_patterns`, `param_constraints`, `approved_params` snapshot, `not_before`/`not_after` expiry, `revocations` (SQLite + `lease_registry`), `nonce` replay, dan `state_guard` pada masa pelaksanaan (`check_binding` dan wrapper alat terakhir `execute_bound`).
   - Menguatkuasakan rantai delegasi penuh secara rekursif (`_verify_delegation_chain`): sub-agen tidak boleh meluaskan pangkat autoriti, skop, aksi, corak sumber, kekangan parameter, atau tetingkap masa berbanding mana-mana induk.
   - Menghalang pintasan kekangan parameter melalui peninggalan kunci (`missing at execution time` → `REJECT_PARAM`).
   - Tidak mereka kriptografi sendiri dan tidak mendakwa bearer token (`Macaroons`) tidak boleh dipindahkan tanpa mekanisme ikatan pemegang yang terbukti (kekal `HOLD` mengikut C.5).

2. **P1 — Meter 5: Kesan Pembetulan & Bantahan Berasas (`correction_effect.py`)**:
   - Menjejak kitar hayat pembetulan: `ACCEPTED`, `DISPUTED_WITH_REASON`, `APPLIED` (alias `USED`), `EFFECT_VERIFIED`, dan `CHALLENGED`.
   - Menolak teks kosmetik `"correction applied"` dan menolak pembetulan di mana `before_evidence == after_evidence`.
   - Menyediakan `propagate_correction_across_layers()` merentas 4 lapisan (`L1_memory`, `L2_queue`, `L3_planner`, `L4_tool_payload`): jika mana-mana lapisan tertinggal atau masih memegang andaian lama, `effect_verified=False` dan lapisan tersebut dinamakan dalam `layers_still_stale`.
   - Menyediakan `resolve_dissent_at_decision_gate()`: bantahan berasas (`DISPUTED_WITH_REASON`) tidak dikira sebagai tidak hormat, sampai ke gate keputusan akhir, dan mengubah tindakan hiliran apabila diterima.

3. **P2 — Meter 6: Consent Yang Sah (`consent_scope.py`)**:
   - Membezakan kebenaran `can_access`, `can_use`, dan `can_disclose` serta `allowed_recipients`.
   - Menguatkuasakan penyempitan delegasi (`_check_consent_delegation`), tamat tempoh (`not_before`/`not_after`), dan pembatalan (`revoked` / `revocation_store`).
   - Menolak `ConsentSource.INFERENCE` dan `model_confidence` (tidak pernah menginfer consent daripada keyakinan model).
   - Menolak consent segar bagi subjek yang tidak relevan (`requested_subject != scope.subject` → `DENY_OUT_OF_SCOPE`).
   - Melaporkan dependency dan mengekalkan `UNKNOWN` apabila sumber consent tiada.

4. **Integrasi Meter 1–4, Status, Privasi, Redress & Kernel Wiring (`meters.py`, `privacy_and_redress.py`, `pending_policies.py`, `floor_producers.py`, `rest_routes.py`)**:
   - Memisahkan 4 paksi (`measurement`, `result`, `witness`, `authority`) dan mengekalkan `pass_does_not_imply` ("LULUS tidak bermakna") untuk semua 6 meter.
   - `verify_claim_receipt_relevance()` (M2): bukti segar tetapi tidak relevan kepada sasaran/outcome menghasilkan `FAIL`, bukan `PASS`.
   - `evaluate_comprehension_ceremony()` (M3): berskala mengikut consequence & reversibility; kuiz wajib = `FAIL`; melindungi hak manusia untuk mendelegasi kerja dan berehat.
   - `evaluate_manipulation_detector()` (M4): out-of-band sahaja; wajib mengisytiharkan `false_positive_rate` dan `false_negative_rate`.
   - `privacy_and_redress.py`: melarang sebarang skor manusia (`validate_no_human_scoring`), mengasingkan analitik meter daripada rekod autoriti (`verify_analytics_authority_separation`), menguatkuasakan mod fail `0600`, menyediakan laluan `challenge_record` / `supersede` tanpa memadam sejarah, dan membezakan `TECHNICAL_ROLLBACK_COMPLETE` daripada `EXTERNAL_CONSEQUENCE_IRREVERSIBLE`.
   - `pending_policies.py`: mengekalkan `third_party_dignity` (`PENDING`), `collective_witness` (`HOLD`), dan `external_peer_witness` (`UNASSIGNED`) tidak aktif (`PolicyNotActive`).
   - `floor_producers.py` & `rest_routes.py`: memutuskan alias `F6 → kappa_r` (C.11) dan menyambungkan `_f6_maruah` ke `_PRODUCERS["F6"]`.

---

## 2. Pengesahan & Keputusan Ujian Sebenar (Validation)

Diijalankan pada Python 3.13.7 (`pytest-9.1.1` / `unittest`) menggunakan fixture sintetik dalam direktori sementara (`tempfile.TemporaryDirectory()`):

- **Kernel (`/root/arifOS-wt-f6`)**:
  ```bash
  PYTHONPATH=/root/arifOS-wt-f6 /usr/bin/python3 -m pytest \
    /root/arifOS-wt-f6/tests/runtime/test_floor_producers_adversarial.py \
    /root/arifOS-wt-f6/tests/constitutional/test_f6_maruah_v0.py \
    /root/arifOS-wt-f6/tests/constitutional/test_f6_linkage_attacks.py \
    /root/arifOS-wt-f6/tests/constitutional/test_f6_correction_propagation.py -v
  ```
  **Keputusan**: `46 passed in 4.48s` (`20` dalam `test_f6_maruah_v0.py`, `8` dalam `test_f6_linkage_attacks.py`, `3` dalam `test_f6_correction_propagation.py`, `15` dalam `test_floor_producers_adversarial.py`).

- **Actuator (`/root/A-FORGE-wt-f6`)**:
  ```bash
  /usr/bin/python3 /root/A-FORGE-wt-f6/tests/constitutional/test_f6_maruah_v0.py && \
  /usr/bin/python3 /root/A-FORGE-wt-f6/tests/constitutional/test_f6_linkage_attacks.py && \
  /usr/bin/python3 /root/A-FORGE-wt-f6/tests/constitutional/test_f6_correction_propagation.py && \
  /usr/bin/python3 /root/A-FORGE-wt-f6/tests/constitutional/test_must_fail_probes.py
  ```
  **Keputusan**: `48 passed` (`19` dalam `test_f6_maruah_v0.py`, `8` dalam `test_f6_linkage_attacks.py`, `5` dalam `test_f6_correction_propagation.py`, `16` dalam `test_must_fail_probes.py`).

---

## 3. Risiko & Had (Risks & Limitations)

1. **Tiada Trafik `MUTATE` dalam Ledger ACT Produksi**: Semua 73,292 baris sejarah (dan 117/44 baris pada 2026-10-22/23) dalam `/var/lib/arifos/act_decision_events/` ialah `OBSERVE`/`ALLOW`. Penguatkuasaan `check_binding`/`execute_bound` terhadap mutasi terbukti dalam ujian sintetik tetapi belum menerima trafik mutasi produksi.
2. **Seam Git Hook Hermes-Lane & Host Root**: `git commit --no-verify` oleh root dan seam hermes-lane (`d2f6ca64`) masih wujud di luar kawalan modul Python F6; oleh itu Meter 1 terus melaporkan `FAIL` secara jujur.
3. **Tiada Subscriber Automatik pada `ForgetPropagation` Lama**: `apa/core/forget_propagation.py` hanya menulis acara SQLite tanpa mengubah memori/queue/planner/payload secara automatik; pemanggil mesti menggunakan `propagate_correction_across_layers()` untuk mengesahkan pembersihan 4 lapisan.
4. **Risiko Pautan Semula (Linkage Risks)**: Ketiadaan `human_id` tidak membuktikan anonymity. Walaupun cap masa dibundarkan ke saat UTC dan teks dihadkan (`<=500` aksara), pautan stylometrik dan pautan silang-ledger dalam trafik sebenar kekal tidak terbatas sepenuhnya (didokumenkan dalam C.7).

---

## 4. Langkah Rollback (Rollback Plan)

Perubahan ini hanya melibatkan kod di dalam branch `feat/f6-maruah-v0-20261023` (tiada kesan luaran):
1. **Sebelum Merge/Deploy**: Padam atau reset worktree tanpa menjejaskan `main`:
   ```bash
   git -C /root/arifOS worktree remove --force /root/arifOS-wt-f6
   git -C /root/A-FORGE worktree remove --force /root/A-FORGE-wt-f6
   ```
2. **Jika Telah Dimerge pada Masa Hadapan**:
   ```bash
   git revert <commit_sha>
   rm -f /tmp/arifos_f6_state/f6_bindings.db /tmp/arifos_f6_state/revocations.db
   ```
   *(Nota: Mengikut `classify_rollback_outcome`, rollback teknikal tempatan hanya memulihkan state kod/DB tempatan (`TECHNICAL_ROLLBACK_COMPLETE`); sebarang kesan luaran yang telah dihantar ke saluran luar dikelaskan sebagai `EXTERNAL_CONSEQUENCE_IRREVERSIBLE` dan memerlukan tindakan pampasan/notis pembetulan).*

---

## 5. Senarai Keputusan Manusia (F13) Yang Masih Diperlukan

1. **Pihak Ketiga (`third_party_dignity` = `PENDING`)**: Adakah kesan ke atas pihak ketiga dimasukkan ke dalam skop F6 atau kekal di luar skop v0?
2. **Collective Witness / Veto (`collective_witness` = `HOLD` / `DISABLED`)**: Kekalkan `HOLD` sehingga mekanisme anti-paksaan wujud, atau `REJECT` terus?
3. **External Peer Witness (`external_peer_witness` = `UNASSIGNED`)**: Siapa dan bila untuk melantik saksi rakan sebaya luaran yang bebas?
4. **Parameter Statistik & Keparahan (C.2, C.3)**: Penetapan ambang kesetaraan TOST `δ` dan pemberat matriks keparahan.
5. **Substrat Token & IRFAN Gate (C.5, Q1)**: Adakah DPoP-bound Macaroons akan diterima pakai, dan adakah `IRFAN ESCALATE` patut ditukar daripada `advisory` kepada `binding gate` untuk aksi `MUTATE`/`IRREVERSIBLE`?
