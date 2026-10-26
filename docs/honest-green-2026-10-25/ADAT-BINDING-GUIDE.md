# IKAT ADAT — Panduan Baca arifOS (selepas deploy 26 Okt 2026)

> Untuk manusia. Bukan untuk mesin. Kalau kau baca ni dalam 2 minit dan faham,
> ia lulus ujian. Kalau tidak, salah aku, bukan kau.

---

## 1. Apa yang berubah (3 ayat)

Dulu, satu diagnosis *liputan* (bahagian mana belum berwayar) dipakai untuk memutuskan sama ada F1 (amanah) lulus. Jadi F1 boleh **gagal walaupun aliran sebenar sihat** — dan ia berbuat begitu dua minit sekali.

Sekarang F1 dinilai oleh alat yang memang ratified untuknya: nisbah verify/execute (FQ) lawan lantai 0.5. Liputan tetap ditunjuk, tetapi sebagai **nota**, bukan lantai.

Dulu juga ada nombor palsu: F8 dipamer "lulus 0.80" sedangkan bacaan sebenar **dilangkau**. Sekarang ia kata **"belum diukur"**. Hijau berkurang. Itu betul.

---

## 2. Tiga medan sahaja yang perlu kau tengok

```
curl -s 'localhost:8088/health?nocache=1' | jq '{
  floor_passed, execution_readiness,
  unmeasured: .layer_health.constitutional.floors_unmeasured,
  aggregate: .layer_health.constitutional.floors_aggregate }'
```

| Medan | Maksudnya | Hari ini |
|---|---|---|
| `floor_passed` | `true` = semua lantai diukur dan lulus · `null` = ada yang belum diukur · `false` = ada yang **gagal** | `null` — jujur, bukan gagal |
| `execution_readiness` | `held` = sistem **enggan** meluluskan tindakan secara automatik | `held` — ini **reka bentuk**, bukan kerosakan |
| `floors_unmeasured` | lantai yang **tiada alat** | `F4 F6 F7 F8 F9 F10` |

**Peraturan membaca:** kalau `floor_passed` = `null`, jangan tafsir sebagai "sistem sihat" **atau** "sistem rosak". Ia bermaksud: *sebahagian tak diukur*. Tanya soalan kedua: lantai mana, dan alatnya ada ke belum.

---

## 3. Adat yang mengikat (siapa boleh buat apa)

| Siapa | Boleh | Tidak boleh |
|---|---|---|
| **Arif (F13)** | putus, vet, ubah perlembagaan | — (tetapi setiap tindakan tetap direkod) |
| **arifOS** | nilai, hukum, tulis ledger | jalankan kod, ubah fail |
| **A-FORGE** | laksana perubahan, selepas ada verdict | halalkan dirinya sendiri |
| **Agent (333/555/888)** | cadang, sahkan, hakim (888) | luluskan kerja sendiri |

Satu ayat: **keupayaan bukan kuasa.** Agent yang boleh buat sesuatu bukan bermakna ia dibenarkan buat.

---

## 4. Apa yang mesin ini **tidak akan** dakwa

1. Ia tidak akan kata "lulus" untuk lantai yang tiada alat. Kalau tiada bukti, ia kata **belum diukur**.
2. Ia tidak akan tukar nombor supaya papan nampak hijau. Kalau bacaan teruk, ia tunjuk teruk.
3. Ia tidak akan anggap "tiada data" sebagai "sifar". Kosong ≠ sifar.
4. Ia tidak akan tutup lantai perlembagaan atas dasar keyakinan model. Keyakinan bukan kuasa.

---

## 5. Status jujur hari ini (26 Okt 2026, 11:4x MYT)

| Perkara | Status | Bukti |
|---|---|---|
| F1 dinilai oleh FQ, bukan liputan | **SIAP** | `arifflow_probe:quotient=1.0032;constellation=PARTIAL_WIRING` → lulus |
| Nombor palsu F8 dibuang | **SIAP** | `status unmeasured, measured false` |
| Bendera palsu `UNKNOWN_VERDICT_TOKEN` dibuang | **SIAP** | panggilan judge: bendera tiada lagi |
| `execution_readiness` masih `held` | **BELUM** | perlu alat F6 + F10, bukan pelonggaran |
| `actor_id` boleh ditukar dalam sesi sah | **BELUM** | keputusan F13: `actor_id` mengikat atau tidak? |
| Prod = main + 1 hotfix | **BELUM** | merge ke main adalah tindakan berasingan |

---

## 6. Kalau ia rosak, balik dalam 2 minit

```bash
rsync -a --delete /opt/arifos/backups/pre-deploy-20261026T112735/arifosmcp-sitepkgs/ \
  /opt/arifos/current/venv/lib/python3.13/site-packages/arifosmcp/
rsync -a --delete /opt/arifos/backups/pre-deploy-20261026T112735/app/ /opt/arifos/app/
systemctl restart arifos.service
```

Resit penuh: `DEPLOY-RECEIPT-2026-10-26.md` dalam folder yang sama.

---

*DITEMPA BUKAN DIBERI. Angka yang menipu lebih berbahaya daripada angka yang tiada.*
