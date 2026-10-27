# ADR-015: Composed Authority Envelope, Stage Order Disambiguation, and Governed Transition Lifecycle

- **Status:** RATIFIED_BY_ARIF_F13
- **Date:** 2026-10-28
- **Drafted By:** Antigravity (Coding Agent)
- **Review & Ratification Authority:** ARIF (F13 Sovereign) — Ratified "SAH" on 2026-10-28T03:28:04+08:00
- **Ratification Scope:** ARCHITECTURAL_DECISION_RECORD_ONLY (No production code mutation, deletion, or deployment authorized yet)
- **Scope:** `arifOS`, `A-FORGE`, `AAA`
- **Replaces / Resolves:** Bounding the Semantic Overloading of SEAL, Stage 777 vs 888 Temporal Ordering, and AuthorityState 4-Domain Decomposition

---

## 1. Context & Problem Statement

Audit P0 mendapati tiga paradoks utama dalam seni bina tadbir urus arifOS:
1. **Paradoks Autoriti:** Wujud 4 definisi berasingan bagi `AuthorityState` (`runtime/model.py`, `schemas/kernel_envelope.py`, `runtime/truth_kernel.py`, dan `contracts/four_plane_contract.py`). Keempat-empatnya membawa maksud domain berbeza dan tidak boleh dipadam atau disatukan ke dalam satu model monolit tanpa merosakkan semantik.
2. **Paradoks Urutan Masa 777 vs 888:** Teks `ZEN.md` memaparkan `777 forge → 888 judge`, tetapi peraturan runtime dan kod `A-FORGE` menuntut `888 judge → 777 forge`. Pemisahan fasa antara pembinaan pelan dan pelaksanaan fizikal belum dinomborkan secara rasmi.
3. **Paradoks SEAL:** Perkataan "SEAL" memikul beban berlebihan sebagai kelulusan awal (*authorization gate*) sekaligus resit lejar (*audit record*).

---

## 2. Keputusan Reka Bentuk (Architectural Decisions)

### Keputusan 1: Gubahan `AuthorityEnvelope` (Bukan Hapus / Bukan Monolit)
Daripada memadam variasi legasi atau memaksa satu model rata, arifOS mentakrifkan satu payung kanonikal berstruktur: **`AuthorityEnvelope`** yang menggubah 8 dimensi ortogonal:

```yaml
AuthorityEnvelope:
  identity_assurance:      # dari kernel_envelope.py (declared vs verified, Ed25519)
  constitutional_authority: # peranan perlembagaan (SOVEREIGN | OPERATOR | ANONYMOUS)
  human_mandate:           # skop mandat F13 (risk limit, acceptance requirement)
  capability_lease:        # skop masa dan fail yang dibenarkan (TTL, allowed_verbs)
  execution_grant:         # dari model.py (proposal_hash, single_use, target)
  runtime_lifecycle:       # keadaan proses (NOT_STARTED | RUNNING | COMPLETED)
  witness_status:          # rujukan saksi (receipt_refs, W3 coherence)
  acceptance_status:       # status pengesahan Arif (ACCEPTED | REJECTED | DEFERRED)
```

Kelas-kelas legasi `AuthorityState` dikekalkan sebagai **Adapter Keserasian (Compatibility Adapters)** untuk membaca dan memproyeksikan data tanpa merosakkan kod sedia ada. Tiada pemadaman dibenarkan pada fasa ini.

---

### Keputusan 2: Pemisahan Fungsian 777.PREPARE (Plan) vs 888.AUTHORIZE vs 900.EXECUTE
Urutan stesen ontologi dipisahkan secara tegas daripada garisan masa eksekusi:

```text
000 INIT          → Membina SessionEnvelope & AuthorityEnvelope.
111 OBSERVE       → Mengumpul bukti realiti mentah (EvidenceSet).
333 AGI PROPOSE   → Menjana graf cadangan & pelan alternatif (ProposalGraph).
555 ASI VERIFY    → Menguji kontradiksi & batas risiko (VerificationReport).
777 FORGE_PLAN    → A-FORGE merangka ExecutionPlan (dry-run, tiada mutasi fizikal).
888 APEX JUDGE    → arif_judge menilai & mengeluarkan JUDGE_SEAL + authorization_grant_id.
900 FORGE_EXECUTE → A-FORGE melaksanakan mutasi fizikal berpandukan authorization_grant_id sah.
980 WITNESS (E1)  → Verifier bebas menyemak kesan dunia sebenar (OutcomeWitness).
990 ACCEPTANCE    → Arif mengesahkan / menolak hasil (SovereignAttestation).
999 CLOSURE       → Merekodkan penutupan sesi dan membawa baki ke lejar VAULT999.
```

*Prinsip Masa:*  
**`777.PREPARE` berlaku SEBELUM `888.AUTHORIZE`. `900.EXECUTE` berlaku SELEPAS `888.AUTHORIZE`.**

---

### Keputusan 3: Penyahkekaburan `JUDGE_SEAL` vs `VAULT_RECEIPT`
* **`JUDGE_SEAL` (Pintu Kebenaran Pra-Tindakan):** Keputusan autoriti oleh `arif_judge` bahawa sesuatu proposal dibenarkan dalam skop dan tempoh tertentu. Ia **BUKAN** bukti bahawa kod telah dijalankan atau berjaya.
* **`VAULT_RECEIPT` (Rekod Acara Bertadbir):** Objek bukti bertaip yang merekodkan sebarang acara bertadbir ke dalam lejar berantai append-only VAULT999. Ia boleh merekodkan:
  - Kebenaran awal (`AUTH_RECORD`),
  - Pelaksanaan arahan (`EXEC_RECORD`),
  - Penerapan runtime (`DEPLOY_RECORD`),
  - Pengesahan bebas (`WITNESS_RECORD`),
  - Pengesahan manusia (`ACCEPTANCE_RECORD`), atau
  - Penutupan sesi (`CLOSURE_RECORD`).  
  *Resit merekodkan acara; ia tidak mencipta autoriti.*

---

### Keputusan 4: Penentuan Kredensial Eksekusi (`authorization_grant_id`)
A-FORGE wajib menuntut dan mengesahkan objek autoriti penuh, bukan sekadar identifier rantaian:

```yaml
execution_authorization:
  authorization_grant_id: authz_...  # Kredensial utama pra-tindakan
  proposal_hash: sha256:...
  plan_hash: sha256:...
  session_id: sess_...
  actor_id: ...
  executor_id: a-forge
  allowed_operation: ...
  target_scope: [...]
  baseline_hash: sha256:...
  issued_at: ISO-8601
  expires_at: ISO-8601
  single_use: true
  revoked_at: null
  policy_version: ...

compatibility:
  constitutional_chain_id: authz_... # Rujukan lineage legasi (deprecated)
  deprecated_meaning: AUTHORIZATION_LINEAGE_REFERENCE
```

---

### Keputusan 5: Pemisahan Keputusan Penutupan vs Resit Penutupan (Station 999)
* **Closure Determination (Keputusan Penutupan):** Keputusan tadbir urus mengenai apa yang telah lengkap, apa yang tergantung, dan apa yang perlu dibawa ke hadapan (`carry_forward`).
* **Closure Receipt (Resit Penutupan):** Operasi append deterministik oleh runtime ke lejar VAULT999 yang menyimpan bukti rujukan penutupan tersebut.

---

### Keputusan 6: Takrif Objek Penerimaan Manusia (`SovereignAttestation` di Station 990)
Penerimaan manusia bukan sekadar teks sembang, ia wajib terikat kepada objek fizikal:

```yaml
sovereign_attestation:
  decision: ACCEPTED | REJECTED | DEFERRED
  subject_type: DEPLOYMENT | ARTIFACT | CONSTITUTIONAL_MUTATION
  subject_id: ...
  subject_hash: sha256:...
  outcome_witness_ref: rcpt_...
  actor: ARIF
  assurance_level: LOW_SESSION | MEDIUM_BOUND | HIGH_CRYPTOGRAPHIC
  recorded_at: ISO-8601
  scope: ...
```

---

### Keputusan 7: Pendaftaran Versi Formula Matematik APEX & Sempadan Jacobian

#### A. Formula-Version Registry (Percanggahan Diakui & Dihadkan)
Penyeragaman formula matematik APEX **belum selesai**. Formula tidak boleh dianggap kanonikal sehingga migrasi disahkan secara berasingan:

```yaml
formula_registry:
  apex-g-v2-runtime:
    formula: "A * P * E * X * Phi"
    status: CURRENT_OBSERVED_IMPLEMENTATION
    source: "arifosmcp/geometry/eureka_zen.py:246"
    epistemic_class: heuristic_scoring
    notes: "Fungsi runtime sebenar yang berjalan hari ini. Hasil darab 5 faktor."

  apex-g-v3-proposed:
    formula: "(A * P * E * X) ** 0.25"
    status: CANONICAL_CANDIDATE
    source: "core/laws.py / ADR proposal"
    epistemic_class: heuristic_aggregate
    notes: "Min geometri 4 faktor. Phi diasingkan sebagai scar gate bebas."
```

*Ratifikasi ADR ini **TIDAK** meratifikasi pertukaran formula runtime secara automatik. Pengaktifan formula baru memerlukan audit ambang verdict dan mandat berasingan.*

#### B. Sempadan Jacobian ($J = \partial T / \partial G$)
* Jacobian dalam [`A-FORGE/src/domain/cognition/taskJacobian.ts`](file:///root/A-FORGE/src/domain/cognition/taskJacobian.ts) ialah heuristik kepekaan penjadualan semula tugasan dalam ruang J-Space.
* **INVARIANT KEKAL:** Jacobian hanya menganggarkan kepekaan. Jacobian dilarang sama sekali daripada mengeluarkan keputusan perlembagaan (*verdict*) atau memberi autoriti eksekusi.

---

## 3. Unjuran Keserasian Khusus Pengguna (Consumer-Specific Projections)

Tiada getter boolean universal tunggal dibenarkan. Penyesuai legasi wajib memproyeksikan makna mengikut keperluan consumer:

```python
class LegacySealProjection:
    @staticmethod
    def project_authorized(t: GovernedTransition) -> bool:
        """Untuk consumer yang mentafsir sealed sebagai kebenaran bertulis."""
        return t.authorization.verdict == "SEAL"

    @staticmethod
    def project_receipt_written(t: GovernedTransition) -> bool:
        """Untuk consumer yang mentafsir sealed sebagai resit lejar wujud."""
        return t.witness.receipt_id is not None

    @staticmethod
    def project_completed(t: GovernedTransition) -> bool:
        """Untuk consumer yang mentafsir sealed sebagai eksekusi berjaya."""
        return t.lifecycle.execution_state == "COMPLETED"

    @staticmethod
    def project_deployed(t: GovernedTransition) -> bool:
        """Untuk consumer yang mentafsir sealed sebagai penerapan runtime."""
        return t.lifecycle.deployment_state == "DEPLOYED"

    @staticmethod
    def project_ratified(t: GovernedTransition) -> bool:
        """Untuk consumer yang mentafsir sealed sebagai pengesahan manusia."""
        return t.human.acceptance_status == "ACCEPTED"

    @staticmethod
    def project_session_closed(t: GovernedTransition) -> bool:
        """Untuk consumer yang mentafsir sealed sebagai penutupan sesi."""
        return t.lifecycle.session_closed is True
```

---

## 4. Pelan Migrasi & Jaminan Keserasian (Rollback & Compatibility)

1. **Tiada Pemadaman Kod Legasi:** Semua definisi `AuthorityState` sedia ada kekal aktif dan disokong oleh adapter.
2. **Rollback Suis Tunggal:** Jika modul persekutuan gagal memproses `AuthorityEnvelope`, konfigurasi `ARIFOS_ENVELOPE_V2=false` akan mengekalkan struktur legasi.
3. **Ujian Semakan Sintetik:** Pengesahan import sintetik membuktikan laluan pemanggilan fail asas berfungsi (1 smoke invocation berjaya pada fixture sintetik; ia **bukan** ujian suite pengeluaran).

---

## 5. Status Semakan Dokumen

- [x] Kontradiksi dikenal pasti, dihadkan (*bounded*), dan diberikan cadangan resolusi semantik.
- [ ] Kontrak runtime dimigrasikan.
- [ ] Keserasian pengguna (consumer compatibility) disahkan.
- [ ] Penguatkuasaan titik sekatan (choke points) disahkan.
- [x] Pengesahan akhir dan semakan manusia ("SAH") oleh ARIF (F13) pada 2026-10-28T03:28:04+08:00.
