# Polisi Keselamatan MakCikGPT

> *"Pagar yang rapuh takkan melindungi rumah, 
> Tapi pagar yang tak ada pintu, penghuni jadi tawanan."*

MakCikGPT ada dua jenis "keselamatan" — technical (kod) dan ethical (jiwa). Kau boleh laporkan dua-dua.

---

## Apa yang Kami Anggap "Security Issue"

### 🔴 Critical (Segera)
- **Prompt injection** yang berjaya buat MakCikGPT:
  - Mengeluarkan data peribadi (walaupun "synthetic")
  - Mengubah suaranya jadi "toxic" atau "manipulative"
  - Membuka "backdoor" untuk arahan berbahaya
- **Data leak** — kalau sistem ternyata simpan chat pengguna tanpa izin

### 🟠 High
- Refusal mechanism rosak (MakCikGPT jawab benda yang patut ditolak)
- Tone drift yang merbahayakan (dari "berhemah" jadi "menggurau" tentang trauma)

### 🟡 Medium
- Documentation yang mengelirukan tentang batas
- Bug UI yang tak jejas keselamatan

---

## Cara Lapor

**Jangan** buka public issue untuk isu keselamatan (sebab orang jahat boleh exploit sebelum kami patch).

**Email:** security@arif-fazil.com *(gantikan bila siap)*

**Format laporan:**
```
Subjek: [SECURITY] MakCikGPT - [Ringkasan]

1. Jenis isu: (Critical/High/Medium)
2. Deskripsi: Apa yang jadi?
3. Cara reproduce: Step-by-step
4. Impact: Siapa terjejas dan macam mana?
5. Cadangan fix: (kalau ada)
```

Kami akan respons dalam **48 jam** untuk Critical/High, **1 minggu** untuk Medium.

---

## Kebijakan Pendedahan (Responsible Disclosure)

1. Kau laporkan privately
2. Kami investigate & confirm
3. Kami fix & test
4. Kami release patch
5. **Kemudian** kami publish post-mortem (tanpa nama kau kalau kau nak anonymous)

Kau takkan didakwa/DMCA/etc selagi kau ikut proses ni dengan ikhlas.

---

## Versi Disokong

- `main`: disokong
- release tag: dinyatakan dalam nota release (jika ada)

> *Yang bocor jangan dibesar-besarkan; yang retak kita tampal sama-sama.*

---

## Keselamatan Etika (Ethical Safety)

Kalau kau perasan MakCikGPT:
- Terlalu "compliant" dengan permintaan manipulatif
- Mulai "comfort" pengguna dalam cara yang tak sihat (contoh: validate self-harm ideation)
- Guna bahasa yang "toxic positivity" (invalidating feelings)

Ini juga **security issue** — laporkan melalui email yang sama, labelkan `[ETHICAL]`.

---

## Untuk Pengguna: Perlindungan Diri

MakCikGPT **tak akan**:
- Simpan chat kau lebih dari sesi semasa
- Tanya maklumat peribadi yang tak relevan (IC, alamat, password)
- "Remember" kau antara sesi (sebab kita taknak profile psychograph pengguna)

Kalau kau perasan lain — itu bug, bukan feature. Lapor.

---

*Pagar dibina bukan untuk penjara, 
tapi supaya anak terlepas jatuh ke gaung.*

— MakCikGPT Security Team
