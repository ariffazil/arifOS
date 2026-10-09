# VAULT999-SIG — Dossier Juruaudit (Audit-Grade Integrity Trail)

> **Fasa 1 Kernel Immutable Floor · G1 · 2026-08-30 · FI-008 (Kimi Code)**
> **Skop:** rantaian meterai kanonik `seal_chain.jsonl` (F-004, epoch `F004-CANONICAL-2026-07-17`)
> **Status kod:** termasuk dalam cawangan `freeze/v1.0.0-SEALED` (arifOS), ujian `arifosmcp/tests/test_kernel_hardening_phase1.py` — 17/17 lulus

---

## 1. Jurang asal (resit forensik)

Sebelum Fasa 1, rantaian meterai **terhubung-hash tetapi TIDAK diautentikasi**:

- `append_receipt(signature="")` — tandatangan pilihan, default kosong.
- Entri hidup terakhir disahkan semasa siasatan: `sequence=28`, `signature=''`, `sig_key_id` tiada — `/root/.local/share/arifos/vault999/seal_chain.jsonl`.
- `GapClass.SIGNATURE_FAIL` / `WRONG_KEY` ditakrifkan dalam `canonical_vault_chain.py` tetapi **tidak pernah dibangkitkan** oleh sebarang laluan kod.
- Implikasi: sesiapa yang mempunyai akses tulis ke fail rantaian boleh menulis semula sejarah secara konsisten (kira semula semua hash) tanpa dapat dikesan oleh pengesah dalam sistem.

## 2. Reka bentuk VAULT999-SIG

| Lapisan | Mekanisme |
|---|---|
| Penandatanganan | Setiap resit kanonik ditandatangani **HMAC-SHA256 penuh (256-bit)** ke atas `receipt_hash` semasa `append_receipt`, bila kunci dikonfigurasi. Medan `sig_key_id="vault-hmac-1"` menandakan kunci. Nilai `signature` daripada pemanggil (termasuk placeholder legasi `"verified"`) **di-override** — sifar ubahan pemanggil. |
| Kunci | `ARIFOS_VAULT_HMAC_KEY` (env) atau `ARIFOS_VAULT_HMAC_KEY_FILE` (fail). Kunci bebas daripada `ARIFOS_SESSION_SECRET` (pemisahan tugas kunci). |
| Cutover | Titik potong `VAULT-SIG-1` = jujukan sign pertama dalam rantaian. Entri kanonik **selepas** cutover wajib bertandatangan. Sejarah pra-cutover **tidak ditulis semula** (doktrin: "gaps are classified, never rewritten"). |
| Mod amaran (lalai) | Entri sign disahkan; unsigned-selepas-cutover dikira dalam `unsigned_after_cutover` (boleh dilihat juruaudit, rantaian kekal hijau). |
| Mod kuatkuasa (`ARIFOS_VAULT_SIG_ENFORCE=1`) | (a) append tanpa kunci → gagal-fail-closed `SIG_ENFORCE_NO_KEY`; (b) unsigned selepas cutover → jurang `SIGNATURE_FAIL`, rantaian MERAH. **Aktivasi mod ini = tindakan 888_HOLD** (lihat §5). |
| Pengesahan | `verify_chain` mengesahkan semula: link `prev_hash`, recompute `receipt_hash` (15 medan kanonik, JSON tersusun), HMAC setiap entri bertanda, duplikasi id/jujukan. Output baharu: `signed_entries`, `signed_unverifiable`, `unsigned_after_cutover`, `cutover_seq`, `sig_enforce`. |

## 3. Laluan audit bebas (untuk prospek / juruaudit EU AI Act)

Alat: **`tools/audit_verify.py`** — stdlib-sahaja, **sifar import arifosmcp**. Juruaudit:

```bash
# 1. Salin rantaian keluar dari sistem (juruaudit pegang salinan sendiri)
scp vps:/root/.local/share/arifos/vault999/seal_chain.jsonl ./chain-copy/

# 2. Kunci dihantar out-of-band (JANGAN melalui sistem yang diaudit)
#    (fail kunci 0600, diserah secara selamat)
python3 audit_verify.py --chain chain-copy/seal_chain.jsonl --key-file vault.key

# 3. (Pilihan) Semak head against anchor yang direkodkan luar:
python3 audit_verify.py --chain chain-copy/seal_chain.jsonl --key-file vault.key \
    --expect-head sha256:<head-yang-direkod>
```

Exit `0` = VERIFIED (link + hash + signature semua hijau); exit `1` = jurang/tandatangan gagal (laporan penuh `--json`).
Alat sepupu: `tools/vault999_auditor_export.py` (manifest eksport + anchoring artefak).

**Pemetaan EU AI Act (ringkas, untuk bual prospek):** Art. 12 (penyimpanan rekod/log — rantaian append-only + resit bertandatangan), Art. 15 (ketepatan & ketahanan — pengesahan bebas offline, fail-closed), Art. 17 (tadbir urus risiko — tangga warn/enforce + 888_HOLD pada kuatkuasa).

## 4. Jurang berpasir (grandfathered) — diklasifikasi, tidak ditulis semula

| ID | Lokasi | Sifat | Attestasi |
|---|---|---|---|
| V999-GR-001 | indeks kanonik 7 (baris 201) | `prev_hash` ialah pengenal pra-migrasi, bukan hash terkira | V999-BRIDGE-SEAL-001 |
| V999-GR-002 | seq=16, `rcpt-86483e9e4a4b4b14` | `prev_hash` tidak bersambung selepas entri hingar WM-HARD-ENFORCE | diklasifikasi 2026-07-30 |
| V999-GR-003 | seq=28, `rcpt-6f9000b09b2e4e77` | `prev_hash` hex-16-char dipetik daripada entri bukan-kanonik ( pepijat `append_receipt` lama) | diklasifikasi 2026-08-11 |

Jurang ini dikecualikan dalam `verify_chain` runtime pada indeks tertentu sahaja. **Alat `audit_verify.py` juruaudit TIDAK mewarisi pengecualian ini** (postur ketat) — jurang di atas akan muncul sebagai `CHAIN_BREAK` dalam laporan juruaudit dan diterangkan oleh dossier ini. Rantaian sign VAULT-SIG-1 bermula selepasnya.

## 5. Prosedur aktivasi kuatkuasa (888_HOLD — F1: rekod kedaulatan kanonik)

1. (Selesai) Kod + ujian dalam repo; mod amaran aktif selepas deploy pertama.
2. Jana kunci vault (`openssl rand -hex 32` → fail 0600 di `/root/.secrets/`, env dalam `arifos.service`).
3. `chown arifos:arifos` fail rantaian + alokator (lihat §6) — pastikan append servis berjaya.
4. Biar mod amaran berjalan sehingga ≥1 seal baharu sign (cutover terbentuk) dan `/999/verify` hijau.
5. **888 approve** → set `ARIFOS_VAULT_SIG_ENFORCE=1` → restart → sahkan rantaian hijau + `sig_enforce=true`.
6. Rekod head hash cutover dalam VAULT999 (seal berkaitan) sebagai anchor luar.

## 6. Jumpaan ops semasa pelaksanaan (perlu tindakan deploy)

1. **Fail rantaian `root`-owned, servis jalankan sebagai `arifos`** — `/root/.local/share/arifos/vault999/seal_chain.jsonl` ialah `-rw-r--r-- root root`. Append oleh servis (`User=arifos`) akan `EACCES`. Digabung dengan item 2, ini senyap.
2. **Persist rantaian non-fatal** — `tools.py` laluan arif_seal mempunyai `except Exception → logger.warning` di sekeliling append rantaian: meterai boleh pulang OK tanpa resit masuk rantaian. *Cadangan Fasa 2+: dalam mod kuatkuasa, kegagalan persist mesti membatalkan status seal.* Hari ini: dipantau melalui `/999/verify` `unsigned_after_cutover` + log `seal chain persist non-fatal`.
3. Rantaian senyap sejak 2026-08-11 (tulis terakhir) — konsisten dengan #1 untuk mana-mana seal cubaan oleh servis selepas itu; head cache dikemas kini oleh laluan baca.

## 7. Ujian regression

`python3 -m pytest arifosmcp/tests/test_kernel_hardening_phase1.py -v` — 17 ujian:
- G4: fail-close ASI (MUTATE/IRREVERSIBLE HOLD, OBSERVE lalui, ASI_TIER HOLD, laluan tersedia tidak berubah)
- G1: sign+verify, tamper-badan-dengan-rehash → SIGNATURE_FAIL, tamper-malas → HASH_MISMATCH, kunci-salah, tiada-kunci (unverifiable dihitung), enforce tolak append unsigned, enforce bendera unsigned-selepas-cutover, alat juruaudit hijau/merah/tanpa-kunci (subprocess)

*DITEMPA BUKAN DIBERI.*
