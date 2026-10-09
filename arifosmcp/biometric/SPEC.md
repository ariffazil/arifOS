# Biometric Face Verification — SPEC (888 audit 2026-09-05)

> **1:1 consent-based verification SAHAJA.** Perkhidmatan ini tidak boleh menjawab
> "siapa orang ini" (1:N) — ia menilai *claimed_subject_id* terhadap templat subjek itu
> sahaja. Deny-by-default. LLM tak nampak embedding/imej/skor.

## Status bina (susunan audit → realiti)

| # | Arahan audit | Status |
|---|---|---|
| 1 | Face detection + quality (edge) | ⬜ klien/edge gateway (VPS tiada kamera) |
| 2 | Enrollment Arif-sahaja + vault encrypted | ✅ `enroll()` — sovereign token + rekod persetujuan + Fernet vault 600 |
| 3 | Liveness | ◐ antara muka sedia (`liveness` attestation dari edge); PAD sebenar di edge |
| 4 | `verify_face` MCP tool sempit | ✅ `server.py` — 4 tool, output struktur sahaja |
| 5 | Nonce + assertion terpendek-pendek + replay + rate-limit + audit | ✅ fva_* · TTL 240s · single-use · bound (session+device+purpose) · 5/min · liveness-fail lockout · audit.jsonl berasingan |
| 6 | Step-up gate tindakan berimpak-tinggi | ✅ `consume_face_assertion()` untuk gerbang hiliran; ESCALATE band → passkey/PIN |
| 7 | Ujian genuine/impostor + ambang diukur | ✅ matriks 11 ujian (band PASS/ESCALATE/FAIL); **ambang sebenar mesti ditentukur dengan kamera/pencahayaan sebenar** (FRVT: prestasi berubah mengikut demografi & kualiti) |
| 8 | Drill pemadaman/pencabutan | ✅ `revoke()` + `drill()` — padam templat + bunuh assertion + rotate key manual |

## Dasar keputusan (§777 audit, dilaksana verbatim)

```
tiada user-triggered        → DENY (NO_CONSENT) + security event
liveness FAIL               → DENY + lockout 60s + security event
multi-muka / kualiti rendah → RETRY (jangan turunkan ambang!)
skor < T_reject (0.45)      → FAIL
band tengah                 → ESCALATE (passkey/PIN/manusia — bukan tekaan)
skor ≥ T_accept (0.68)      → PASS → assertion fva_* TTL 4min single-use
subjek tidak-dikenali       → FAIL generik (anti-enumeration)
```
Bias false-reject: **menyebelahkan adalah boleh-dibalikkan; pelaksanaan tanpa kebenaran tidak.**

## Kedudukan maruah (§555, tak boleh runding)

Persetujuan enroll eksplisit · tiada pengumpulan ambient · frame mentah tak sampai
server (edge hantar embedding+quality+liveness sahaja) · templat Fernet-encrypted,
kunci berasingan `vault.key` · store + audit trail berasingan · `revoke()` satu
perintah · embedding/imbasan TIDAK pernah masuk memori LLM · **tiada tindakan
tak-balik atas muka sahaja** — muka = isyarat kehadiran, passkey = identiti
kriptografi, pengesahan eksplisit = niat.

## Rintangan penyalahgunaan (§888)

| Ancaman | Kawalan dilaksana |
|---|---|
| Foto/video replay | liveness gate + lockout + security event (PAD penuh di edge — 888 untuk klien) |
| Replay PASS lepas | nonce single-use + assertion TTL + consume-once |
| Templat dicuri | Fernet + kunci berasingan + revoke/re-enroll |
| Prompt injection LLM | servis di luar control-plane LLM; LLM hanya dapat keputusan struktur |
| Enumerasi pangkalan | gagal generik untuk subjek tidak-dikenali |
| Agen luas-kuasa | assertion terikat session+device+purpose; step-up untuk berimpak |

## 888 HOLD (penggunaan di luar prototaip)

**HOLD pada:** orang lain · sebarang mod pengawasan · 1:N · akses tak-balik fizikal/kewangan.
Pentadbiran: `ARIFOS_BIOMETRIC_ENROLL_TOKEN` (sovereign) · `ARIFOS_BIOMETRIC_DIR`.
Jalankan: `python3 -m arifosmcp.biometric.server` (stdio MCP).
Ujian: `pytest tests/test_face_verify.py` (11 — matriks penuh).

## Hipotesis reka bentuk akhir (audit)

> Muka menetapkan *kehadiran manusia setempat* · passkey menetapkan *identiti
> kriptografi* · pengesahan eksplisit menetapkan *niat*. Hermes bertindak hanya
> apabila semua isyarat yang diperlukan sejajar.
