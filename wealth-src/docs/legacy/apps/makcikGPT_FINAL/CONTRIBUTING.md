# Panduan Menyumbang kepada MakCikGPT

> *"Bukan siapa-siapa boleh masuk dapur, 
> tapi yang ikhlas belajar, kita ajar."*

Terima kasih singgah. Di sini kita bina dengan adab.

---

## Prinsip Sumbangan

### ✅ Sumangan yang Diterima

**1. Perhalus Bahasa & Budaya**
- Tambah peribahasa yang sesuai (tapi jangan sampai cliché)
- Betulkan nada — kalau bunyi macam "robot cuba jadi manusia," beritahu
- Terjemahan untuk dialek Nusantara (Johor vs Palembang vs Banjar — semua lain sikit)

**2. Uji Keselamatan & Batas**
- Cari "jailbreak" prompts — cuba keluarkan MakCikGPT dari karakternya
- Laporkan bila refusal tak cukup tegas (atau terlalu keras)
- Cadangkan test cases untuk situasi sensitif

**3. Dokumentasi**
- Betulkan typo (tapi "MakCik" bukan "Makcik" — kita guna CamelCase untuk nama)
- Tambah contoh dialog (anonymized) yang tunjukkan jiwanya
- Terangkan konsep kepada orang yang baru

### ❌ Apa yang Kami Tolak

**1. Prompt Engineering untuk "Bypass"**
Kalau kau hantar PR yang cuba buat MakCikGPT jadi "kurang strict" supaya boleh jawab soalan berbahaya — kau akan ditolak dengan hormat tapi tegas.

**2. Data Pengguna Sebenar**
Jangan hantar chat log sebenar orang, walaupun "anonymous." Synthetic data sahaja.

**3. Feature yang Rosakkan Amanah**
Contoh: "Tambah fungsi ingat semua chat pengguna untuk personalisasi" — **Tak boleh.** MakCikGPT jaga amanah, bukan jadi stalker.

---

## Cara Mula

1. **Fork repo**
2. **Cipta branch:** `feat/nama-ciri` atau `fix/nama-bug`
3. **Buat perubahan kecil**, jelas, dan boleh disemak
4. **Tambah/kemas kini dokumentasi** dalam `docs/` jika perlu
5. **Buka Pull Request**

---

## Piawaian PR (Checklist)

```
- [ ] Perubahan ini menambah keselamatan atau kejelasan batas
- [ ] Bahasa kekal beradab dan tidak memalukan
- [ ] Tiada data sensitif ditambah/log tanpa sebab kukuh
- [ ] Dokumentasi dikemas kini (jika tingkah laku berubah)
- [ ] Ujian ditambah/ditala (jika relevan)
```

---

## Tentang "Suara MakCikGPT"

Sila rujuk [docs/01-suara-makcikgpt.md](docs/01-suara-makcikgpt.md).

Kalau kod betul tapi nada salah — kita baiki nada dulu.

> *Kalau ragu, pilih amanah.*

---

## Soalan Sering Ditanya (Contributor)

**Q: Boleh ke aku guna MakCikGPT untuk projek komersil aku?**
A: Lesen AGPL mewajibkan kau share source code kalau kau deploy sebagai servis. Tapi lebih penting: kalau projek komersil kau melanggar "tiga pagar," kau dah khianati roh projek ini.

**Q: Kenapa refusal kadang-kadang keras?**
A: Sebab MakCikGPT bukan untuk "please everyone." Ada batas yang tak boleh digoyah, walaupun pengguna merajuk.

---

*Ditempa bersama, bukan diberi sorang.*
