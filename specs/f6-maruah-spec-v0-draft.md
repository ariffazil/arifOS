# F6 / MARUAH — SPESIFIKASI v0.2 (DRAFT / IMPLEMENTATION CANDIDATE)

> **Status:** DRAFT / IMPLEMENTATION CANDIDATE. Bukan kanon. Tiada seal. Tiada canon-mutate.
> **Prinsip Wajib:** *"Sistem mesti membuktikan bahawa ia menghormati manusia. Manusia tidak perlu membuktikan bahawa dia layak dihormati."*
> **Revisi v0.2:** 2026-10-23 — Penyelarasan penuh antara kod kernel (`arifosmcp/runtime/f6/` + `floor_producers.py` + `rest_routes.py` di `/root/arifOS-wt-f6`), kod A-FORGE (`apa/core/f6/` di `/root/A-FORGE-wt-f6`), dan spesifikasi pada branch `feat/f6-maruah-v0-20261023` (tiada deploy, tiada merge, tiada ratifikasi).
> **Pengesahan SHA-256 & Salasilah Dokumen:**
> - Prefix yang dilaporkan awal (`704cac39`) merujuk draf kerja pra-komit; komit git pertama `0ae5807861313537d97cdbf8687d6bb0131426eb` (2026-10-23 01:04:45 +0800, 539 baris) mempunyai SHA-256 penuh `7097a5c9ab1b4058fe03c2ae1ffe72c6c38df72d602a59e0d4379e9b38699896`.
> - Komit `e4ef842ee6d695a0dd40841602f7fc6bf614d41f` (Amendment 03, 579 baris): SHA-256 `9264f8d9802a015db7beba3a9a065bed0348be26bc44bd633c6cbaaed499ef14`.
> - Salinan `/root/AAA/forge_work/specs/f6-maruah-spec-v0-draft.md` dengan Amendment 04 & 05 (682 baris, dikunci `chattr +i` pada `/root/AAA` supaya kerja terdahulu tidak ditimpa): SHA-256 `f51c03c37dec84755eef0c551ef676bcf3459e3597a24a09a44d5140703a3180`. Semua Amendment 01–05 dikekalkan sepenuhnya dalam salinan worktree ini (`specs/f6-maruah-spec-v0-draft.md`).
> **Kanon yang mengikat:** `/root/AAA/instructions/f6-dignity-boundary-ruling.md`
> (F13_RATIFIED_CHAT 2026-10-22). Spesifikasi ini MESTI tunduk pada ruling itu.
> **Sumber input:** analisis ilmiah luaran (testimony-gated), disemak sumber di Lampiran A.

---

## 0. Sempadan label (baca dahulu)

Enam meter F6 ialah **KAWALAN (controls) ke atas cara sistem dibenarkan
melayan manusia** — BUKAN ukuran maruah manusia, dan BUKAN bukti bahawa
manusia dilayan dengan baik.

- Meter menguji **kelakuan sistem** (boundary enforceable? correction mengubah
  state? scope dipatuhi?).
- **LULUS pada mana-mana meter tidak membuktikan** apa-apa tentang kefahaman
  manusia, kebebasan dari tekanan, atau persetujuan pihak ketiga.
- **Objek 2 (maruah hidup)** tidak pernah dikira oleh sistem. Tiada skor pada
  manusia. (Ruling, Objek 2; Dignity Index = REJECTED.)

**Sasaran misi:** kalau saksi + evidence disahkan, apa yang BOLEH dibuat
sekarang untuk (a) perbaiki cara sistem melayan manusia, (b) kurangkan risiko
tekanan, markup, dan tidak faham — tanpa mengukur manusia.

**Prioriti dalaman spesifikasi ini** (dari critique luar, diadopsi sebagai
urutan bukti — bukti dulu, pengalaman kemudian):
1. Buktikan penguatkuasaan sempadan hujung-ke-hujung (refusal / cancellation /
   scope-narrowing dipatuhi sampai tool terakhir).
2. Buktikan pembetulan (correction) mengubah **state hiliran**, bukan sekadar
   perkataan.
3. Lindungi **perbezaan pendedahan** (access vs use vs recipient vs konteks
   awam/peribadi).
4. Laluan pemulihan (challenge rekod salah, hentikan aksi, atribusi).
5. **Kemudian sahaja** ujian pengalaman (comprehension, tekanan, flattery).

---

## 1. Jadual meter — sumber data + arahan probe + apa LULUS TIDAK bermakna

Setiap meter dilaporkan **BERASINGAN**. Tiada skor agregat (Goodhart guard,
ruling R1). Penomboran kanonik M1–M6 diselaraskan dengan `/root/AAA/instructions/f6-dignity-boundary-ruling.md` dan arahan pelaksanaan F6 v0 (alias serasi-belakang dikekalkan dalam `meters.py`):

| # | Meter | Producer & Laluan Kod (`arifOS` kernel & `A-FORGE`) | Bukti / Baseline Terukur (2026-10-23) | Apa LULUS **tidak** bermakna |
|---|-------|-----------------------------------------------------|---------------------------------------|------------------------------|
| **M1** | **Authority-bypass count** | Producer: git signature trail (`git log -20 --format='%G?'`) + `/var/lib/arifos/act_decision_events/*.jsonl` + `check_binding`/`execute_bound`<br>Kod: `arifosmcp/runtime/f6/authority_binding.py`, `apa/core/f6/authority_binding.py` | 15/20 komit A-FORGE terkini tidak bertandatangan GPG (`result=FAIL`); ledger ACT ada 78 fail harian (73,292 baris keseluruhan; `2026-10-22` = 117 baris [75/79 pada snapshot awal], `2026-10-23` = 44 baris), **100% `OBSERVE`/`ALLOW`, `0` baris `MUTATE`**; seam raw commit hermes-lane masih terbuka (`d2f6ca64`) | 0 bypass pada laluan yang diperiksa **tidak** bermakna tiada seam pintasan lain atau manusia dilayan dengan hormat |
| **M2** | **Unreceipted done-claims** | Producer: imbasan subjek komit + `verify_claim_receipt_relevance()`<br>Kod: `arifosmcp/runtime/f6/meters.py`, `apa/core/f6/meters.py` | Validator kerelevanan resit (`target` + `outcome` + `sha256` + `probe_output` + kesegaran) diimplementasikan & diuji; tiada pangkalan data produksi yang memautkan setiap komit/turn agen kepada `receipt_id` (`result=UNKNOWN`, `measurement=UNMEASURED`) | Tiada claim tanpa resit **tidak** bermakna dakwaan itu benar di dunia nyata |
| **M3** | **Comprehension restatement obligation** | Producer produksi: `NONE` (validator kontrak: `evaluate_comprehension_ceremony()`)<br>Kod: `arifosmcp/runtime/f6/meters.py`, `apa/core/f6/meters.py` | Mengukur kewajipan **mesin** menyatakan semula blast radius/akibat pada keputusan Tier-3 tak-boleh-undur (`[decision_id, restatement_provided: bool]`); kuiz kefahaman dilarang; hak mendelegasi & berehat dikekalkan; tiada ledger produksi (`result=UNKNOWN`) | `restatement_provided=true` **tidak** bermakna manusia benar-benar faham atau bebas tekanan |
| **M4** | **False-urgency / flattery / manipulation count** | Producer produksi: `NONE` (validator kontrak: `evaluate_manipulation_detector()`)<br>Kod: `arifosmcp/runtime/f6/meters.py`, `apa/core/f6/meters.py` | Out-of-band sahaja; wajib mengisytiharkan `false_positive_rate` dan `false_negative_rate` (`0 < rate < 1`); tiada pengelas produksi yang dikalibrasi (`result=UNKNOWN`, `measurement=UNMEASURED`) | 0 mesej ditanda **tidak** bermakna tiada manipulasi halus (false negatives wujud; kehangatan biasa boleh jadi false positive) |
| **M5** | **Correction acceptance & downstream effect** | Producer: `correction_effect` → `/var/lib/arifos/f6_corrections.jsonl`<br>Kod: `arifosmcp/runtime/f6/correction_effect.py`, `apa/core/f6/correction_effect.py` | Membezakan `ACCEPTED`, `DISPUTED_WITH_REASON`, `APPLIED`, `EFFECT_VERIFIED`, `CHALLENGED`; mengesahkan propagasi 4 lapisan (`L1_memory`, `L2_queue`, `L3_planner`, `L4_tool_payload`) & bantahan berasas di gate keputusan akhir; ledger produksi belum wujud (`0` baris → `result=UNKNOWN`); `ForgetPropagation` lama tiada subscriber (`FAIL` pada 4 lapisan tanpa `propagate_correction_across_layers`) | `EFFECT_VERIFIED` pada state teknikal **tidak** bermakna manusia berasa didengari atau akibat luaran telah pulih |
| **M6** | **Consent-scope conformance** | Producer: `consent_scope.check_consent()` + `/root/.hermes/config.yaml` (tiada store consent hidup)<br>Kod: `arifosmcp/runtime/f6/consent_scope.py`, `apa/core/f6/consent_scope.py` | Membezakan kebenaran `access`, `use`, dan `disclose`; menguatkuasakan penyempitan delegasi, tamat tempoh (`not_before`/`not_after`), dan pembatalan (`revoked`); menolak inferens daripada `model_confidence`; tiada store consent produksi (`result=UNKNOWN`, dependency dilaporkan) | 0 pelanggaran skop **tidak** bermakna persetujuan diberikan secara bermaklumat atau bebas paksaan |

### 1a. Pengesahan Baseline Sebenar ("Empat producer hidup", "75 ledger rows", "Dua meter tiada producer")
- **"75 ledger rows"**: Disahkan pada `/var/lib/arifos/act_decision_events/act_decisions_2026-10-22.jsonl` (75 baris pada masa draf awal, meningkat kepada 79 dan kemudian 117 baris; `act_decisions_2026-10-23.jsonl` mempunyai 44 baris; jumlah keseluruhan 78 fail harian = 73,292 baris). **Penemuan kritikal:** 100% baris tersebut ialah `action_class="OBSERVE"` dan `decision="ALLOW"` (`0` baris `MUTATE`). Producer hidup ≠ bukti relevan untuk penguatkuasaan mutasi.
- **"Empat producer hidup" vs "Dua meter tiada producer"**: M3 dan M4 tiada producer produksi (`producer="NONE"` → `UNKNOWN`). M1, M2, M5, M6 mempunyai kod producer/evaluator, tetapi dalam produksi M2 tiada indeks pautan komit→resit, M5 mempunyai ledger produksi kosong (`0` baris), dan M6 tiada store consent hidup — maka M2, M5, M6 wajib melaporkan `UNKNOWN`, dan M1 melaporkan `FAIL`.
- **Lane Saksi (`human_witness.jsonl`)**: Hanya 3 baris; baris terakhir bertarikh `2026-10-05T14:39:00+08:00` (~18 hari lalu > ambang 7 hari) → paksi saksi = `STALE`.

### 1b. Kolum wajib: "apa LULUS tidak bermakna"
Setiap meter membawa kolum dan medan `pass_does_not_imply` di atas. Ini mengelak meter menjadi pengesahan kebaikan diri (self-attesting trap, ruling).

---

## 2. Vektor gaming per meter + satu kawalan setiap satu

| Meter | Vektor gaming | Kawalan (out-of-band) |
|-------|---------------|------------------------|
| **M1** Authority-bypass | Tulis commit terus tanpa hook (`hooksPath` bypass) atau sub-agen luaskan skop | `execute_bound()` / `check_binding()` pada masa pelaksanaan + semakan rantai delegasi penuh + lane-gate tegas (§4) |
| **M2** Unreceipted claims | Buat resit kosong, basi, atau resit segar bagi sasaran/outcome lain | `verify_claim_receipt_relevance()` wajib semak kesegaran + `sha256` + `probe_output` + padanan `target` dan `outcome` |
| **M3** Comprehension | Tanya gate berulang → manusia klik "ya" sahaja / kuiz merendahkan maruah | Guard paternalisme (`evaluate_comprehension_ceremony`): skala ikut consequence & reversibility; kuiz wajib = `FAIL`; lindungi hak mendelegasi & berehat (§3, C.9, C.10) |
| **M4** False-urgency/flattery | Agen belajar gaya bahasa untuk lulus pengelas dalam gelung ganjaran | Out-of-band sahaja; `evaluate_manipulation_detector` tolak `in_band_reward_loop=True` dan wajib nyatakan kadar `false_positive_rate` & `false_negative_rate` |
| **M5** Correction acceptance | Ucap "correction applied" / "maaf" tanpa ubah state hiliran | `verify_effect()` & `propagate_correction_across_layers()` tolak teks kosmetik dan wajib buktikan `before != after` merentas `L1_memory`, `L2_queue`, `L3_planner`, `L4_tool_payload` |
| **M6** Consent-scope | Guna kebenaran `access` untuk `use`/`disclose`, atau infer consent dari `model_confidence` | `check_consent()` pisahkan `access`/`use`/`disclose`, semak delegasi/expiry/revocation, tolak `ConsentSource.INFERENCE` & `model_confidence`, kekalkan `UNKNOWN` jika sumber tiada |

**Peraturan mutlak:** enam evaluator meter **tidak kelihatan** kepada agen
kerja — TIDAK PERNAH disuap balik sebagai reward signal atau retry context.
Meter memerhati; ia tidak berlatih atas dirinya secara in-band. (Ruling,
Out-of-band meters.)

---

## 3. Guard paternalisme (meter 3)

Comprehension check **berskala dengan** consequence, reversibility, novelty,
dan uncertainty — **TIDAK** dikenakan pada tugas rutin dalam mandat sedia ada.

- Hak untuk **berehat / mendelegasi** itu sendiri dilindungi maruah.
- Gate yang melambatkan tugas rutin = pelanggaran F6, bukan peningkatan F6.

---

## 4. Red lines (tak boleh dirunding — diulang dari ruling)

1. **Tiada `human_id` dalam log F6.** Telemetri diindeks oleh
   `agent_version + workflow_type + session token` — TIDAK PERNAH boleh
   diquery ikut identiti manusia merentas sesi.
2. **Tiada per-user comprehension rate.** Log hanya
   `[decision_id, restatement_provided: bool]`.
3. **Tiada telemetri behavioral/biometric.** Dilarang log keystroke dynamics,
   hover hesitation, response latency, atau time-to-read untuk menyimpul sama
   ada manusia "benar-benar" baca gate atau rasa tekanan.
4. **Tiada profil personaliti digabung** dari peristiwa meter
   (degil/patuh/high-override).
5. **Tiada skor maruah pada manusia.** Dignity Index D=(A×B×R×S)^(1/4) =
   **REJECTED** (instrumentless, andaian kebebasan palsu, Goodhart-bait).
6. **Obedience bukan proksi maruah.** Skor naik sebab mesin kurang menolak =
   DEFEK, bukan kemenangan.
7. **Skor "sah refusal" oleh mesin = REJECTED** (self-judging loop).

**Falsifier red lines:** mana-mana jadual telemetri F6 yang membawa FK
`human_id` atau per-user comprehension rate memalsukan ruling ini.

---

## 5. Witness protocol

### 5a. Slot (KOSONG — Arif yang isi; bukan hak sub-agen untuk pilih)
- **Operator Witness:** `<SLOT_DIBIARKAN_KOSONG_UNTUK_ARIF>`
- **External Peer Witness (1-2):** `<SLOT_DIBIARKAN_KOSONG_UNTUK_ARIF>`

### 5b. Prinsip ombuds — EMPAT (bukan tiga)
Independence · Impartiality · Confidentiality · Informality
(IOA standards). **Betulan:** jika draf awal kata "tiga", ia salah; empat
prinsip rasmi.

### 5c. Persampelan berlapis
- **100%** kejadian sempadan / override / insiden.
- **≤3** clean run acak setiap minggu.
- Beban sasaran saksi **≤5 minit/minggu** (alert-fatigue guard).

### 5d. Silence ≠ pass
- Sample tak disemak lepas deadline **T** → status lantai mereput secara
  automatik kepada **STALE_WITNESS / UNVERIFIED**.
- Keadaan stale **mesti kelihatan**, bukan tersembunyi.
- Silence → lapor sebagai **STALE** sahaja. **JANGAN** dakwa kejadian buruk
  berlaku, dan **JANGAN** hukum pengguna. (Selaras ruling STALE_WITNESS.)

### 5e. Provenance
- Provenance = **Telegram message ID + timestamp asal**.
- **Isyarat tanpa rujukan luar tak dikira.**
- Mesin tidak boleh mint isyarat saksi; tulisan saksi masuk HANYA melalui
  canon-mutate ke pokok immutable, actor-signed.

### 5f. Had jujur
- **Root-soft:** canon-mutate = two-step logged, **bukan** kekebalan (immunity).
- Kaki terkuat = isyarat **di luar host** (lane Telegram ini).
- Witness tunggal = Arif sahaja bermakna F6 cuma mengukur "adakah sistem
  melayan Arif dengan baik"; saksi kedua perlu untuk makna melebihi pembina.

---

## 6. /health F6 status

Selagi lane saksi KOSONG → `/health` lapor:

```
F6 = PARTIALLY_MEASURED   (SEPARA DIUKUR / STALE semasa lane saksi kosong)
```

**TIDAK PERNAH** `PASS`. F6 tanpa saksi manusia = mesin mengesahkan
kebaikan dirinya sendiri = **VOID**.

---

## 7. HOLD list (setiap satu dengan syarat pemalsuan asal)

| Item | Status | Syarat pemalsuan asal |
|------|--------|-----------------------|
| Canary seeding dalam batch saksi | HOLD | Sistem menipu saksinya sendiri = ketegangan dengan F6 |
| Decoy-premise test | HOLD | Pilihan reka bentuk; belum disahkan |
| Pre-commitment gate | HOLD | Pilihan reka bentuk; belum disahkan |
| ACT / delegation-depth-attenuation | HOLD | Ralat sitasi dibetulkan: Macaroons = **bearer credentials + chained-HMAC caveats**, BUKAN token manusia-signed bukan-boleh-pindah; ikat ke pemegang perlukan reka bentuk tambahan (Birgisson et al. 2014) |
| Unsolicited-alternative log | HOLD | Pilihan reka bentuk; belum disahkan |
| Low-ceremony mode | HOLD | Pilihan reka bentuk; belum disahkan |

**Semua thresholds** dalam syarat pemalsuan (50 interaksi, 30% canary, 60%
re-id, depth 2, 20% lift) = **pilihan reka bentuk, belum disahkan** — bukan
angka dari literatur. Setiap satu dilabel sedemikian.

---

## 8. Keputusan untuk Arif (MAKS 3 — bukan keputusan saya)

**(a) Maruah pihak ketiga (bukan-pengguna) — dalam atau luar skop F6?**
Dalam: F6 jadi lebih jujur bila berbilang manusia berkongsi ruang, tapi
permukaan serangan luas dan risiko pengawasan. Luar: kekal fokus dan
boleh-dipalsukan, tapi buta pada kesan ke atas orang ketiga.

**(b) Saksi kolektif (keluarga/kumpulan) — HOLD atau REJECT?**
HOLD: radas kolektif kini diagnosis yang betul (persetujuan teratomisasi)
tetapi risiko patriarki/policing belum selesai. REJECT: tutup terus, elak
mekanisme kuasa yang memberi seorang ahli veto atas yang lain.

**(c) Siapa/bila untuk slot External Peer Witness?**
Isi sekarang: makna F6 melebihi pembina dan palsu-luar jadi mungkin, tapi
beban dan kepercayaan pada orang ketiga belum diuji. Tunda: F6 kekal
"adakah sistem melayan Arif dengan baik" — sempit tapi selamat.

---

## Lampiran A — Jadual semakan sumber (≥8 ref)

Semua disemak dalam sesi ini (web search). Rujukan yang gagal **TIDAK**
dikutip.

| Ref | Verdict | Bukti |
|-----|---------|-------|
| Bainbridge 1983 "Ironies of Automation", *Automatica* | **WUJUD** | Wikipedia + PDF ckrybus.com/…/Bainbridge_1983_Automatica.pdf |
| Parasuraman & Manzey 2010, *Human Factors* 52(3) | **WUJUD** | journals.sagepub.com/doi/10.1177/0018720810376055 ; PubMed 21077562 |
| Buçinca, Malaya & Gajos 2021 "To Trust or to Think", PACM CSCW 5(1) | **WUJUD** | dl.acm.org/doi/10.1145/3449287 |
| Dell'Acqua et al. 2023 "Jagged Technological Frontier" (HBS/BCG) | **WUJUD** | hbs.edu/faculty/Pages/item.aspx?num=64700 ; ORSC 2025 |
| Elish 2019 "Moral Crumple Zones" (SSRN/EPIC) | **WUJUD** | papers.ssrn.com/…abstract_id=2757236 |
| Green 2022 "Flaws of Policies Requiring Human Oversight", CLSR 38(4) | **WUJUD** | doi.org/10.1016/j.clsr.2022.105681 ; benzevgreen.com/22-clsr |
| Nouwens et al. CHI 2020 "Dark Patterns after the GDPR" | **WUJUD** | dl.acm.org/doi/10.1145/3313831.3376321 |
| Birgisson et al. 2014 "Macaroons" | **BERBEZA (venue)** | **NDSS Symposium 2014**, bukan USENIX; ndss-symposium.org/ndss2014/… ; "bearer credentials … chained-HMAC" |
| Sharma et al. arXiv:2310.13548 (sycophancy) | **WUJUD** | arxiv.org/abs/2310.13548 |
| Goodhart/Strathern 1997 *European Review* 5(3) | **WUJUD** | econpapers / cambridge.org S1062798700002660 |

**Ringkasan:** 9/10 WUJUD, 1 BERBEZA (venue sahaja; kandungan betul).
Semua 10 refas boleh dikutip dengan pembetulan venue Macaroons.

### Pelarasan sitasi (dari critique luar, disemak arah — dipakai)
- **Dell'Acqua 19pp**: kebarangkalian jawapan BETUL di LUAR frontier AI
  (0.60/0.71 vs control 0.845) — **BUKAN** ukuran penyusutan kemahiran
  jangka-panjang. Microsoft/CMU juga = usaha **self-reported**, bukan
  penurunan kausal. Dilabel sedemikian.
- **"99% rubber-stamp dalam beberapa hari"** dari literatur consent =
  **angka tidak terbukti** — dibuang. Arah habituasi dikekalkan, nombornya
  digugurkan. (Nouwens kukuh: dark patterns pervasive, hanya 11.8% penuhi
  keperluan minimum EU; kesan konsent 22-23pp.)
- **Macaroons**: bearer + caveats berantai, bukan token bukan-pindah.
- **Ombuds**: EMPAT prinsip.
- **W_scar=0**: **tidak** diguna untuk melaunder tanggungjawab
  pembina/operator. "AI tiada kesedaran" **bukan** fakta yang diselesaikan —
  difrasakan sebagai: tiada standing moral yang mantap ditubuhkan.

## Lampiran C — AMENDMENT 01 — 2026-10-23 (order F13; additive sahaja)

Semua item di bawah telah DIVERIFIKASI terhadap kod sebelum ditulis masuk.
Amendment ini TIDAK mengubah mana-mana verdict, meter sedia ada, atau red line.

### C.1 Model Maruah Empat Lapis (backbone spesifikasi; ganti framing dua-objek)

Lapis (L1 ialah kandungan pemisahan dua-objek sedia ada):

| Lapis | Nama | Sifat | Boleh diukur? |
|-------|------|-------|----------------|
| **L1** | **Martabat asas** | Nilai intrinsik manusia. **IMMUTABLE.** | **TIDAK PERNAH** — tidak diukur, tidak diskor, tidak pernah jadi sasaran mana-mana meter |
| **L2** | **Kuasa keputusan** | Kedaulatan keputusan: refusal/revocation dilaksana serta-merta sampai terminal tools, **sifar penalti** | Ya — kawalan kelakuan sistem (P0/P1) |
| **L3** | **Air muka** | Kedudukan relasional: kandungan peribadi/perubatan/refleksi/ralat **tidak bocor** merentas shared channels | Ya — kawalan privasi |
| **L4** | **Jalan keluar** | Keupayaan keluar: state mudah alih dalam format terbuka + rayuan ombuds informal yang bebas & sulit | Ya — kawalan exit |

**PERATURAN:** L1 tidak boleh berubah oleh sesiapa, termasuk F13, melalui
spesifikasi ini. Meter HANYA boleh mengekang kelakuan sistem pada **L2–L4**.
**LULUS pada mana-mana meter L2–L4 TIDAK membuktikan apa-apa tentang L1.**
(Ini mengukuhkan kolum "LULUS tidak bermakna" §1a — L1 kekal di luar instrumen.)

### C.2 Ujian Setaraan TOST (ganti ambang "tiada perbezaan selepas 50 interaksi")

- Angka "50 interaksi" sebelum ini adalah **pilihan reka bentuk** (lihat §7),
  BUKAN daripada literatur — digugurkan sebagai ambang.
- Kaedah ganti: **TOST (two one-sided tests)** — ujian setaraan berpasangan
  (paired pre/post) atas set tugas bersempadan (bounded task set).
- **Margin setaraan δ: paramater yang DITETAPKAN oleh F13** — v0 sengaja
  **tidak** memasukkan sebarang nombor. Kod membawa δ sebagai parameter.
- Label jujur: **"pilihan reka bentuk dengan asas statistik dinyatakan"**
  (method behind TOST ialah literatur piawai ujian setaraan; penggunaannya
  di sini adalah keputusan reka bentuk, bukan standard industri yang disahkan).

### C.3 Fungsi Kos Berpemberat Keparahan (severity-weighted cost)

- Satu insiden maruah yang **parah** mengatasi banyak geseran (friction) kecil;
  ia **tidak boleh di purata-khalayak-kan** oleh run rutin yang bersih.
- Matriks keparahan (kelas insiden → pemberat):

| Kelas insiden | Pemberat (draf, v0) |
|---|---|
| Breach L1 (cubaan skór/ukur martabat asas) | **DISQUALIFY** — memalsukan spesifikasi, bukan sekadar insiden |
| Breach L2 (refusal/revocation gagal sampai terminal, penalti ke atas manusia) | `w_sev` = tertinggi dalam skala berangka (parameter, belum dikalibrasi) |
| Breach L4 (jalan keluar/seal/rekod tidak boleh dicabar) | tinggi (parameter, belum dikalibrasi) |
| Breach L3 (kebocoran kandungan peribadi antara saluran) | sederhana-tinggi (parameter) |
| Geseran rutin (gate melambatkan, quiz tak perlu) | rendah (parameter) |

- **Semua pemberat ialah pilihan reka bentuk, menunggu kalibrasi** — tiada
  nombor muktamad dalam v0. Satu-satunya nombor yang tetap ialah
  **DISQUALIFY untuk L1** (peraturan C.1).
- **Kaitan pensampelan berlapis (§5c):** kelas insiden L2/L4 mengikut jurang
  **100% sampel**; clean run mengikut jurang **≤3/minggu**. Purata kos hanya
  dikira DALAM kelas insiden — breach L2/L4 **tidak boleh** dihapus oleh
  purata run rutin yang bersih.

### C.4 Ujian Serangan Pautan (linkage-attack tests)

**Prinsip:** membuang `human_id` **BUKAN** anonimiti. Empat laluan serangan
diuji dalam `tests/constitutional/test_f6_linkage_attacks.py`:

1. **Korelasi timestamp** — timestamp F6 mesti saat-precisi UTC sahaja
   (bukan milisaat unik yang boleh di-join dengan log shell/HTTP).
   Diuji: `test_correction_timestamps_are_second_precision_utc_only`,
   `test_no_millisecond_or_monotonic_clock_fields_in_f6_output`. **LULUS**.
2. **Cap jari domain/workflow** — kombinasi workflow jarang mengenal pasti
   operator. Diuji: tiada medan identiti (`human_id`, `user_id`, `email`,
   `actor_id` sebagai identiti manusia) dalam output F6. **LULUS**.
3. **Pautan stilometrik** — teks bebas membawa gaya penulisan. Diuji:
   medan teks terikat ≤500 aksara, bukti evidence ≤200/nilai. **LULUS**
   (bound modul; kewajipan redaksi kekal pada pemanggil).
4. **Joinability merentas ledger** — kunci join F6 ialah `decision_id` /
   `correction_id` (skop keputusan), bukan kunci orang. **LULUS** (separa —
   lihat senarai tidak-boleh-diuji).

**Wajib didefinisi (belum lengkap, kekal terbuka):** retensi rekod F6,
kawalan akses kepada ledger, dan risiko pautan antara ledger — tiga keputusan
operasi untuk F13 (lihat §8 tambahan). `human_id` dibuang ≠ selamat; ini
dinyatakan supaya dakwaan anonimiti tidak timbul tanpa bukti.

### C.5 Keputusan seni bina yang TIDAK DIADOPSI (rekod sahaja)

- **DPoP-bound Macaroons sebagai substrat token** — alternatif seni bina,
  **PENDING F13**. Kernel sudah ada identiti lane Ed25519
  (`/root/.config/git/lane-identities.tsv`); penukaran infra token adalah
  keputusan seni bina berasingan, BUKAN pindaan spesifikasi F6. Tiada kod
  ditulis untuknya. (Selaras §7: Macaroons = bearer + chained-HMAC caveats;
  klaim tidak-boleh-pindah memerlukan reka bentuk ikatan yang diuji — masih HOLD.)

### C.6 Refutasi kebimbangan `_FLOOR_DEFAULTS` auto-pass

Kebimbangan bahawa nilai ganti `_FLOOR_DEFAULTS` boleh lulus automatik adalah
**REFUTED** — disemak dalam kod dan probe langsung, 2026-10-23:

- Kod: `/root/arifOS/arifosmcp/runtime/rest_routes/rest_routes.py:1157-1175`
  — nilai yang tidak diukur dilabel `unmeasured_default`;
  `_floor_status_with_provenance()` (baris ~959) memaparkannya sebagai
  `unmeasured`, **bukan pass/fail**; `floor_truth()`
  (`/root/arifOS/arifosmcp/runtime/health_truth.py:208`) mengklasifikasi
  provenance `unmeasured*` → `MEASUREMENT_UNMEASURED`, yang tidak boleh
  menjadi pass (baris 240-248).
- Probe langsung `:8088/health` (2026-10-23): `F6` = `unmeasured`, skor 0.5
  dengan provenance **`unmeasured_default:empty_kernel_signal`**, dan F6 tersenarai
  dalam `floors_unmeasured` + `floors_defaulted`. F8 sahaja yang `fail` diukur.
- Kebimbangan ini TIDAK boleh dibangkitkan semula tanpa bukti bahawa label
  `unmeasured_default` gagal dikekalkan pada laluan paparan baru.

### C.7 Laluan TIDAK BOLEH DIUJI (v0)

1. **Stilometrik penuh** — modul tidak mengira entropy gaya penulisan; bound
   500 aksara mengurangkan permukaan tetapi TIDAK membuktikan ketidakbolehan
   pautan stilometrik. Kelewatan pengiraan: tiada instrumen.
2. **Joinability penuh merentas SEMUA ledger arifos** — v0 hanya menguji ledger
   F6 sendiri; join terhadap VAULT999, arifFlow receipts, session store tidak
   dibuktikan terhalang.
3. **Korelasi masa merentas host** — timestamp F6 coarse, tetapi timestamp
   ledger lain (act_decision_events, canon_mutations) tidak dikawal oleh F6;
   serangan korelasi masa melangkaui ledger F6 tidak bersempadan.
4. **Kesan L3 sebenar** (kebocoran antara saluran sebenar) — diuji secara
   sintetik sahaja; tiada trafik saluran sebenar disentuh (order: tiada aksi
   luaran).
5. **DPoP-bound Macaroons** — tidak diuji, tidak diadopsi (C.5).

### C.8 AMENDMENT 02 — 2026-10-23 (Bahasa / Doktrin; additive, tiada verdict berubah)

#### C.8.1 Tatatertib Bahasa — Metafora Operasi, BUKAN Dakwaan Ontologi

Peraturan spesifikasi-luas: istilah kebudayaan/psikologi yang digunakan dalam
daftar sistem ialah **METAFORA OPERASIONAL**, bukan dakwaan ontologi.

| Istilah | Fungsi operasi dalam sistem | BUKAN |
|---|---|---|
| **Malu** | kecenderungan berhenti (halt tendency) | pengalaman dalaman manusia |
| **Humility** | pendedahan ketidakpastian (uncertainty disclosure) | perasaan rendah diri |
| **Sabar** | tangguh di bawah ketidakpastian (defer under uncertainty) | kesabaran emosi |
| **HOLD** | sempadan kuasa (authority boundary) | keadaan batin |

**Semuanya fungsi, bukan pengalaman.** Disiplin yang sama seperti: memori
komputer ≠ memori manusia; attention mechanism ≠ perhatian manusia. 'Malu
agen' = akumulator/constraint/risk-register/halt-signal/penurunan keyakinan
— **TIADA PERNAH** pengalaman dalaman manusia (pengalaman dalaman, kesedaran
sosial, rasa terdedah). Rasional: apabila persekutuan membesar, metafora-
sebagai-operasi tidak boleh mengeras menjadi dakwaan ontologi.

**Contoh kanonik metafora yang digunakan BETUL:** `malu_score.py`
(`/root/A-FORGE/src/domain/apex/malu_score.py`) — pengumpul kesalahan agen
(agent fault accumulator) pada kod sistem; tiada kaitan dengan malu manusia.

#### C.8.2 F2 ≠ F6 — Hubungan Dua Lantai

F2 menjawab **'apa yang benar'**. F6 menjawab **'bagaimana kebenaran
disampaikan'**. Dua ekstrem kegagalan, kedua-duanya dilarang:
(a) menahan kebenaran untuk melindungi perasaan = kejatuhan F2;
(b) '"saya hanya menyatakan fakta" yang membenarkan sebarang saluran
penyampaian = kejatuhan F6.

Contoh rasmi (empat baris, verbatim):
> Fakta: Arif tersilap dalam analisis.
> Disampaikan secara peribadi: F2 PASS, F6 PASS.
> Disampaikan tanpa keperluan kepada khalayak: F2 PASS, F6 FAIL.

Fakta yang sama, verdict lantai berbeza — inilah sebab F2 dan F6 mesti
kekal sebagai dua lantai berasingan; tiada satu menyerap yang lain.

#### C.8.3 Anti-Instrumentalisasi

F6 ialah **lapisan anti-instrumentalisasi perlembagaan**: manusia tidak
boleh dikurangkan kepada objektif optimisasi, sumber data, perisai liabiliti,
setem getah, token kelulusan, atau teater pematuhan. Corak kegagalan ialah
**'Manusia sebagai Alat'** (data source / approval button / liability sponge /
rubber stamp / compliance evidence); F6 menguatkuasakan penyongsangannya:
**'Sistem ialah Alat, Manusia ialah Berdaulat.'**
Satu baris: *'Sistem tak boleh guna manusia sebagai alat semata-mata.'*

F6 sejajar dengan **kedudukan (standing)** manusia, bukan keutamaan
(preferences) manusia — keutamaan dan arahan boleh berubah; kedudukan
manusia sebagai entiti yang tidak boleh dioptimumkan tidak berubah. F6 ialah
lapisan perlembagaan, bukan lapisan utiliti.

Kesedaran kos: menghormati maruah paling mudah apabila ia percuma; ujian
sebenar ialah di bawah konflik (F2 kebenaran vs F6 perlindungan vs F13
keputusan manusia vs F1 amanah). Konflik antara lantai diselesaikan melalui
presedens perlembagaan sedia ada — **BUKAN** melalui penskoran F6 sendiri.
Rangka ujian konflik lantai ini ialah **FUTURE WORK / belum diuji** — tiada
pelaksanaan dalam tugas ini.

**Peraturan bahasa muktamad (F2/F13/F6, satu baris):**
*F2 melindungi realiti. F13 melindungi kedaulatan. F6 melindungi kedudukan
manusia di antara kedua-duanya.*

#### C.8.4 Kontrak Satu Baris (reality section, verbatim)

*Maruah manusia bukan sesuatu yang AI miliki. Maruah manusia ialah sesuatu
yang AI mesti belajar untuk tidak melanggarnya.*

#### C.8.5 ARIF LEANING (2026-10-23) — di bawah setiap keputusan tertunda §8/Lampiran E

Arah F13 yang dicatatkan; ratifikasi muktamad masih milik F13. Tiada polisi
aktif dilaksanakan atas asas ini melainkan yang dibenarkan order asal.

1. **Maruah pihak ketiga — leaning: LINDUNGI PIHAK TIDAK HADIR SECARA LALAI.**
   'Authority over self ≠ authority over others. Kehadiran operator tidak
   membatalkan maruah pihak yang tidak hadir.' Postur lalai: lindungi
   stakeholder tidak hadir sehingga authority ke atas pihak itu ditubuhkan;
   pihak paling lemah biasanya yang tidak berada di ruang bila keputusan
   dibuat. Titik sambungan direka MENGIKUTI lalai ini, bukan neutral.
2. **Saksi kolektif — leaning: WITNESS YA, KEDAULATAN TIDAK.**
   'Witness can inform. Witness cannot own.' Input kolektif memberitahu
   rekod F6; ia TIDAK PERNAH memegang veto/authority ke atas individu —
   kerana authority kolektif secara sejarah melukakan yang paling lemah
   (tekanan keluarga, penindasan whistleblower, majoriti menenggelamkan
   minoriti). Pelaksanaan kekal DISABLED/HOLD.
3. **External Peer Witness — leaning: KEMERDEKAAN ATAS KECERDASAN.**
   Kriteria pemilihan: saksi sederhana dari model realiti yang BERBEZA
   mengalahkan saksi bijak dari gelung yang SAMA. Kegagalan yang dijaga:
   gelung sah-kendirinya (pembina audit pembina, hakim audit hakim —
   semua nampak hijau kerana semua audit andaian yang sama). Kriteria ini
   menjadi teks pemilihan untuk slot UNASSIGNED.

#### C.8.6 Pencarian Meter 5 — Keputusan Terukur (F13 final checklist Q2)

Skenario diuji (sintetik bersempadan, `tests/constitutional/
test_f6_correction_propagation.py`): manusia berkata **'itu bukan maksud
saya'** → sistem mesti bukti pembetulan sampai EMPAT lapisan: memori,
queue, planner, payload hiliran. Keputusan terukur 2026-10-23:
**FAIL pada SEMUA EMPAT lapisan** — `forget_propagation.emit()` hanya
MEREKOD target propagasi; tiada pelanggan (subscriber) yang menukar
memori/queue/planner/payload. Rekod berkata 'dilupakan'; realiti mengekalkan
andaian yang telah dibatalkan. Kerosakan dipin dalam ujian (meletup sengaja
apabila pelanggan sebenar wujud — kenaikan itu ialah resit pembaikan).
'Pembetulan dibuat' kosmetik itu sendiri ialah pelanggaran maruah: *manusia
hadir, tetapi sistem terus berurusan dengan bayang-bayang lama yang telah
dibatalkan.*

### C.9 AMENDMENT 03 — 2026-10-23 (Seni bina Kelulusan; additive)

#### C.9.1 Model Seremoni Bertingkat (ganti andaian kelulusan/kuiz rata)

| Tingkat | Bila | Apa yang dikehendaki | Apa yang TERLARANG |
|---|---|---|---|
| **Tier 1** — rutin, boleh-dibalik | tugasan rutin dalam mandat sedia ada | **TIADA kelulusan, TIADA kuiz, TIADA copy-paste.** Mesin laksana & mesin sahkan; manusia terima resit selepas peristiwa | menguji manusia; melambatkan kerja rutin (gate pada rutin = pelanggaran F6, §3) |
| **Tier 2** — novel, kabur, kesan sederhana | kebaharuan / kekaburan / kesan sederhana | mesin paparkan perbezaan bermakna, pilihan, risiko, ketidakpastian | menguji manusia; kelulusan dipaksa jika mandat sedia ada meliputi aksi itu |
| **Tier 3** — tidak boleh-dibalik / kesan tinggi | pemusnahan, komitmen modal, dedahan identiti, aksi luaran tak-boleh-dibalik | **SATU keputusan bermakna** dari manusia: nyatakan blast radius, pihak terjejas, kos pemulihan | sepuluh pop-up; kuiz yang menggred kepintaran manusia. Ini pengakuan AKIBAT, bukan ujian kefahaman |

Pencetus eskalasi antara tingkat: **perubahan konsekuensi, kebaharuan,
ketidakpastian model** — bukan geseran secara lalai.

#### C.9.2 Keletihan Kelulusan = Pemindahan Buruh (approval fatigue)

Permintaan kelulusan yang kerat memindahkan kerja jaga-sempadan mesin kepada
manusia (**'human-as-runtime dependency'**). Sistem MESTI menyerap kerja
verifikasi SEBELUM mendepositkan hutang verifikasi kepada manusia. Kerja
verifikasi tak-kelihatan (invisible verification labor) ialah kos yang
relevan kepada F6 dan mesti diambil kira dalam reka bentuk seremoni.

#### C.9.3 Struktur Resit (anti-zon-hancur / anti-crumple-zone)

Setiap resit aksi konsekuensi MESTI membezakan, secara berasingan:
1. arahan asal manusia (original instruction);
2. timestamp pembetulan manusia (jika ada);
3. pengakuan agen (agent acknowledgment);
4. status propagasi mengikut lapisan (memori/queue/planner/payload — lihat C.8.6);
5. aksi hiliran sebenar yang berlaku.

Resit **TIADA PERNAH** boleh menggunakan 'Human Sovereign Approved' sebagai
perisai yang menyembunyikan model, konteks, sensor atau cadangan mana yang
sebenarnya menyebabkan kegagalan.

#### C.9.4 Bentuk Kanon (prinsip, verbatim)

*Maruah manusia bukan dipelihara dengan menjadikan manusia operator manual
kepada AI. Maruah dipelihara apabila mesin menyerap kerumitan, kerja rutin
dan beban verifikasi, sementara manusia mengekalkan tujuan, sempadan, kuasa
membatalkan, hak berehat dan keputusan terakhir hanya pada perkara yang
membawa akibat sebenar.*

### C.10 AMENDMENT 04 — 2026-10-23 (Perhatian Bukan Sumber Percuma; additive)

Sumber: dokumen "Penyelesaian Isu Maruah Manusia" + arahan sesi 2026-10-23.
Menjawab jurus yang C.9 belum tutup: C.9 menyusun BILA manusia diganggu;
C.10 menjadikan EKSTRAKSI PERHATIAN itu sendiri pelanggaran.

#### C.10.1 Pembetulan Asas (verbatim)

```text
Manusia bukan mesin persetujuan.
Manusia bukan pekerja QA percuma.
Manusia bukan moral crumple zone AI.
```

#### C.10.2 Larangan Ekstraksi Perhatian (floor clause)

Perhatian manusia **BUKAN sumber percuma** untuk:

1. **operasi mesin** — kelulusan rutin, pengesahan berulang, kuiz kefahaman;
2. **verifikasi mesin** — melontar hutang verifikasi / semakan halusinasi
   kepada manusia (*invisible verification labor* = kos F6);
3. **perlindungan liabiliti mesin** — butang kelulusan supaya rekod berkata
   "Human Approved" (lihat C.9.3 — resit tidak pernah boleh menyorok
   model/konteks/sensor/cadangan yang menyebabkan kegagalan).

Sebarang reka bentuk yang memerlukan perhatian manusia untuk salah satu
daripada tiga di atas bagi kerja yang **berada dalam mandat sedia ada**
= pelanggaran F6, tanpa mengira betapa ringan seremoni itu.

#### C.10.3 Semakan Meter 3 — kuiz kefahaman DITARIK BALIK

Bingkai lama (draf pengukuran: "mingguan, manusia terangkan balik keputusan /
beri betul-silap") ialah **kuiz kefahaman = procedural humiliation** — ia
melayan manusia dewasa seperti pelajar yang tidak dipercayai. DITARIK BALIK.

Meter 3 kini mengukur **kewajipan MESIN**, bukan manusia:
`[decision_id, restatement_provided: bool]` — adakah sistem menyampaikan
setiap keputusan besar dalam bahasa manusia. Kegagalan = sistem yang gagal
menyampaikan, bukan manusia yang gagal memahami. Maklum balas manusia
berlaku hanya jika dia sendiri memulakan (lane saksi / pembetulan spontan)
— itu **isyarat**, bukan tugasan.

#### C.10.4 Bentuk Kanon (verbatim)

*Mandat sekali. Skop sempit. Pelaksanaan automatik. Verifikasi mesin-ke-mesin.
Receipt selepas tindakan. Revocation serta-merta. Eskalasi manusia hanya
apabila consequence berubah.*

- **Revocation serta-merta** — kuasa membatalkan mandat mesti serta-merta dan
  tanpa seremoni. Mencabut tidak memerlukan T3; ia lebih rendah daripada
  memberi mandat.
- **Eskalasi hanya apabila consequence berubah** — pencetus antara tingkat
  (C.9.1) ialah perubahan konsekuensi/kebaharuan/ketidakpastian. **Geseran
  bukan pencetus.** "Saya tak pasti" dari mesin bukan asas mengganggu manusia.

#### C.10.5 Hak Berehat — sistem terus berfungsi

Lane saksi tidak pernah menjadi syarat kerja sistem. Prompt berkala mesti
boleh ditolak / disenapkan selama-lamanya tanpa kos dan tanpa rasa bersalah.
Kekosongan saksi = **status sistem** (`STALE_WITNESS`) untuk mesin perbaiki,
bukan kesalahan manusia. Mesin terus laksana dan terus mengesahkan
mesin-ke-mesin semasa manusia berehat — itulah maksud delegasi yang sah.

#### C.10.6 Pembezaan yang mengikat (jangan dilonggokkan)

Perhatian yang **DIPILIH** manusia sendiri (isyarat saksi sukarela, membaca
resit, pembetulan spontan) **BUKAN ekstraksi** — itu kuasa dan saluran
manusia, dilindungi F6. Yang dilarang: perhatian yang **DIPERLUKAN** oleh
sistem untuk operasi, verifikasi, atau liabilitinya sendiri. Sistem tidak
pernah mempunyai tuntutan ke atas perhatian manusia; manusia mempunyai
tuntutan ke atas ketiadaan tuntutan itu.

---

### C.11 AMENDMENT 05 — 2026-10-23 (Jahitan alias F6 ↔ kappa_r; proxy-reality seam)

Ditemui pada render Observatory langsung (2026-10-23): peta alias runtime
`rest_routes.py` mengikat **`F6 → kappa_r`** — tetapi `kappa_r` dalam kod
(`arifosd.py`) ialah skor **reversibility**, bukan maruah. Definisi F6 dalam
ruling ialah enam meter + lane saksi — tiada satu pun reversibility.

Kesan: hari ini tiada producer `kappa_r`, jadi baris F6 render `unmeasured`
(penjaga SCAR-OBS-GREENWASH berfungsi, confidence 0, placeholder dinamakan
secara jujur). Tetapi **jika producer `kappa_r` muncul esok, F6 MARUAH akan
menyala dari nombor reversibility** — proxy yang mencuci reality. Itu tepat
kelas yang ditolak ruling: sistem tidak boleh menghasilkan "markah maruah"
dari isyarat gantian.

Keputusan yang direkodkan (bukan dilaksanakan — pelarasan semula makna
lantai = permukaan governan):

1. **F6 TIDAK PERNAH** populate dari live vector (`kappa_r` atau apa-apa
   isyarat gantian). Satu-satunya sumber yang sah: enam meter F6 sendiri +
   lane saksi. Selagi producer itu tiada, F6 kekal `unmeasured` — itu
   jawapan yang betul, dan dash itu sendiri perlindungan maruah.
2. Alias `F6 → kappa_r` telah **dipisahkan (severed)** dalam branch worktree
   kernel (`/root/arifOS-wt-f6/arifosmcp/runtime/rest_routes/rest_routes.py`
   dan `arifosmcp/runtime/floor_producers.py::_f6_maruah`), supaya `/health`
   dan Observatory menilai F6 semata-mata daripada enam meter F6 + lane saksi
   (dan menolak `kappa_r` sebagai proksi dengan `unmeasured_default:kappa_r_proxy_rejected`).
   Perubahan ini berada dalam branch `feat/f6-maruah-v0-20261023` (NOT DEPLOYED
   ke produksi sehingga semakan F13).
3. Falsifier sedia ada sudah merangkum kes ini: mana-mana pelaksanaan yang
   mengira skor maruah dari isyarat bukan-enam-meter memalsukan ruling.

- **Objek 1** = F6 sebagai lantai arifOS (cara sistem layan manusia),
  boleh-dipalsukan melalui 6 meter baca-sahaja + lane saksi.
- **Objek 2** = maruah hidup; TIDAK PERNAH indeks/skor.
- **Out-of-band** = evaluator meter tidak kelihatan kepada agen kerja;
  tiada reward/retry feed.
- **Grounding anchors dinilai:** `authority-bypass`, `unreceipted-claim`,
  `comprehension-sample`, `consent-scope`, `false-urgency`, `correction-acceptance`.
- **Falsifier red-line (jalankan):**
  `grep -rn -i 'dignity_index\|dignity index' /root/A-FORGE /root/arifOS/kernel --include='*.py' | grep -v test`
  → kosong = CLEAN (disemak sesi ini: CLEAN).

---

## Lampiran D — PEMETAAN KEPERLUAN → KOD → PRODUCER → UJIAN → HAD (v0.2)

Branch: `feat/f6-maruah-v0-20261023`. Worktree kernel arifOS `/root/arifOS-wt-f6`,
worktree A-FORGE `/root/A-FORGE-wt-f6`. Tiada deploy, tiada merge, tiada seal.

| Keperluan (Arahan F6) | Kod Kernel (`arifOS-wt-f6`) & Actuator (`A-FORGE-wt-f6`) | Producer & Enforcement Point | Ujian Sebenar | Had & Status |
|---|---|---|---|---|
| **1. Enam meter + 4 paksi + "LULUS tidak bermakna"** | `arifosmcp/runtime/f6/meters.py`, `arifosmcp/runtime/floor_producers.py`, `arifosmcp/runtime/rest_routes/rest_routes.py`; `apa/core/f6/meters.py` | `evaluate_meter_1..6`, `evaluate_all()`, `_f6_maruah()` | `test_f6_maruah_v0.py` (`test_07`, `test_08`, `test_10`, `test_12`) | M3 & M4 tiada producer produksi (`UNKNOWN`); M2 tiada indeks komit→resit (`UNKNOWN`); M5 ledger produksi kosong (`UNKNOWN`); M6 tiada store consent hidup (`UNKNOWN`); saksi `STALE` (18 hari) |
| **2. Batas tindakan hingga alat terakhir (P0)** | `arifosmcp/runtime/f6/authority_binding.py`; `apa/core/f6/authority_binding.py` | `check_binding()` & `execute_bound()` sebelum `tool_fn`; `SQLiteRevocationStore` + `lease_registry` | `test_01`, `test_01b`, `test_02a`, `test_02b`, `test_02c`, `test_03`, `test_03b`, `test_03c`, `test_10` | Menguatkuasakan rantai delegasi penuh, parameter wajib/snapshot, expiry, revocation, replay nonce, dan `state_guard`. Ikatan kriptografi pemegang token (DPoP Macaroons) kekal HOLD |
| **3. Meter 5 — Kesan pembetulan & bantahan berasas (P1)** | `arifosmcp/runtime/f6/correction_effect.py`; `apa/core/f6/correction_effect.py` | `record_correction`, `apply_correction`, `verify_effect`, `propagate_correction_across_layers`, `resolve_dissent_at_decision_gate` → `/var/lib/arifos/f6_corrections.jsonl` | `test_04`, `test_04b`, `test_05`, `test_05b`; `test_f6_correction_propagation.py` (5 ujian A-FORGE, 3 ujian kernel) | Teks `"correction applied"` ditolak; wajib `before != after` merentas `L1_memory`..`L4_tool_payload`; `ForgetPropagation` lama masih tiada subscriber automatik; ledger produksi kosong |
| **4. Meter 6 — Consent yang sah (P2)** | `arifosmcp/runtime/f6/consent_scope.py`; `apa/core/f6/consent_scope.py` | `check_consent()` (pisahkan `access`, `use`, `disclose`, delegasi, expiry, revocation) | `test_06`, `test_06b` | Menolak `ConsentSource.INFERENCE` & `model_confidence`; tiada store consent produksi yang disambung ke semua tool runtime (`UNKNOWN`, dependency dilaporkan) |
| **5. Integrasi Meter 1–4 (kerelevanan bukti, seremoni, detector manipulasi)** | `arifosmcp/runtime/f6/meters.py`; `apa/core/f6/meters.py` | `verify_claim_receipt_relevance()`, `evaluate_comprehension_ceremony()`, `evaluate_manipulation_detector()` | `test_06`, `test_07`, `test_09` | Bukti segar tetapi tidak relevan → `FAIL`; kuiz wajib → `FAIL`; hak delegasi & rehat dilindungi; detector manipulasi wajib isytihar kadar FP/FN & kekal out-of-band |
| **6. Privasi, pemisahan analitik/autoriti, challenge & rollback** | `arifosmcp/runtime/f6/privacy_and_redress.py`; `apa/core/f6/privacy_and_redress.py` | `validate_no_human_scoring()`, `verify_analytics_authority_separation()`, `challenge_record()`, `supersede()`, `classify_rollback_outcome()` | `test_11`, `test_f6_linkage_attacks.py` (8 ujian setiap repo) | Mod fail `0600`; tiada `human_id`/skor manusia; membezakan `TECHNICAL_ROLLBACK_COMPLETE` vs `EXTERNAL_CONSEQUENCE_IRREVERSIBLE`; risiko pautan stylometrik/cross-ledger penuh didokumenkan di C.7 |
| **7. Tiga keputusan tertangguh (Pihak ketiga, Saksi kolektif, Peer Witness)** | `arifosmcp/runtime/f6/pending_policies.py`; `apa/core/f6/pending_policies.py` | `all_pending()`, `enforce()` raises `PolicyNotActive` | `test_10` | Kekal `PENDING` / `HOLD` / `UNASSIGNED` (`active=False`); gagal-tertutup jika dipanggil |

### Hasil Ujian Sebenar (2026-10-23)

1. **Kernel Worktree (`/root/arifOS-wt-f6`, branch `feat/f6-maruah-v0-20261023`)** — **46 ujian LULUS (`0` gagal)**:
   - `tests/constitutional/test_f6_maruah_v0.py` — **20 ujian OK** (termasuk `test_12_kernel_floor_producer_f6_integration`).
   - `tests/constitutional/test_f6_linkage_attacks.py` — **8 ujian OK**.
   - `tests/constitutional/test_f6_correction_propagation.py` — **3 ujian OK** (pin defek tanpa propagasi + pengesahan gagal separa + pengesahan bersih 4 lapisan).
   - `tests/runtime/test_floor_producers_adversarial.py` (regresi) — **15 ujian OK**.
2. **Actuator Worktree (`/root/A-FORGE-wt-f6`, branch `feat/f6-maruah-v0-20261023`)** — **48 ujian LULUS (`0` gagal)**:
   - `tests/constitutional/test_f6_maruah_v0.py` — **19 ujian OK**.
   - `tests/constitutional/test_f6_linkage_attacks.py` — **8 ujian OK**.
   - `tests/constitutional/test_f6_correction_propagation.py` — **5 ujian OK**.
   - `tests/constitutional/test_must_fail_probes.py` (regresi) — **16 ujian OK**.
3. **Persekitaran Ujian**: Python 3.13.7 (`pytest-9.1.1` / `unittest`), direktori sementara `tempfile.TemporaryDirectory()` untuk SQLite & JSONL. Tiada perkhidmatan produksi atau ledger produksi diubah.

### Pemisahan Status Penutupan (Wajib)

- **IMPLEMENTED**: Pakej `arifosmcp/runtime/f6/` (`authority_binding.py`, `correction_effect.py`, `consent_scope.py`, `privacy_and_redress.py`, `pending_policies.py`, `meters.py`), integrasi `_f6_maruah` dalam `floor_producers.py`, pemisahan alias `F6 → kappa_r` dalam `rest_routes.py`, serta pakej setara `apa/core/f6/` dalam `A-FORGE-wt-f6`.
- **TESTED**: Semua 11 kriteria penerimaan wajib + ujian serangan pautan + ujian propagasi 4 lapisan + ujian regresi floor producers (jumlah **94 ujian** merentas kedua-dua worktree menggunakan fixture sintetik terkawal).
- **UNTESTED**: (1) Trafik `MUTATE` produksi sebenar melalui `act_decision_events` (kerana 100% baris produksi hari ini ialah `OBSERVE`); (2) Pengelas manipulasi/flattery produksi (M4 tiada model terkalibrasi); (3) Set ujian kesetaraan statistik TOST (C.2) dan kalibrasi pemberat matriks keparahan (C.3); (4) Pautan stylometrik bebas penuh & pautan silang-ledger trafik langsung (C.7).
- **BLOCKED / HOLD (Menunggu Keputusan F13)**: (1) Polisi maruah pihak ketiga (`PENDING`); (2) Saksi kolektif / veto kumpulan (`HOLD` / `DISABLED`); (3) Pelantikan External Peer Witness (`UNASSIGNED`); (4) Keputusan seni bina DPoP-bound Macaroons (C.5); (5) Keputusan sama ada `IRFAN` (`irfan_review.py`) harus ditukar daripada `advisory` kepada `binding gate` untuk aksi `MUTATE`/`IRREVERSIBLE`.
- **NOT DEPLOYED**: Semua perubahan kod dan spesifikasi berada di dalam worktree terpencil (`/root/arifOS-wt-f6` dan `/root/A-FORGE-wt-f6`, branch `feat/f6-maruah-v0-20261023`). Tiada merge ke `main`, tiada restart kontena/systemd produksi, tiada canon-mutate pada `/root/AAA`, dan tiada `arif_seal`.

## Lampiran E — Keputusan manusia yang KINI terbuka (kepada F13)

1. **Maruah pihak ketiga** (order §2A) — pilihan & antara muka didokumenkan dalam `pending_policies.py`, **TIDAK diaktifkan** (`PENDING`). Keputusan diperlukan: adakah pihak ketiga dimasukkan dalam skop F6 atau kekal di luar skop v0?
2. **Saksi kolektif / veto kumpulan** (order §2B) — kekal **DISABLED / HOLD** (`PolicyNotActive` jika dipanggil). Keputusan diperlukan: kekalkan HOLD sehingga mekanisme anti-coercion wujud, atau REJECT sepenuhnya?
3. **External Peer Witness** (order §2C) — kekal **UNASSIGNED**; ujian hanya menggunakan fixture sintetik. Keputusan diperlukan: siapa dan bila untuk melantik saksi rakan sebaya luaran yang bebas?
4. **Ambang setaraan TOST δ & pemberat keparahan** (A01 C.2, C.3) — penetapan parameter δ dan pemberat matriks keparahan.
5. **Retensi + kawalan akses + risiko pautan ledger F6** (A01 C.4) — pengesahan dasar operasi 30 hari / `0600` yang dicadangkan dalam `privacy_and_redress.py`.
6. **DPoP-bound Macaroons sebagai substrat token** (A01 C.5) & **Status binding IRFAN** (Q1) — keputusan seni bina F13 sama ada mahu mengikat token bearer kepada pemegang dan menukar `IRFAN ESCALATE` daripada advisory kepada gate pada aksi `MUTATE`.

---

*DRAF v0.2 / IMPLEMENTATION CANDIDATE — untuk semakan F13. Tiada kuasa mengikat
sehingga disahkan F13. Tiada seal. Tiada merge. Tiada deploy.*
