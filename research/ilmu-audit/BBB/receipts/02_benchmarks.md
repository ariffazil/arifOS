# Phase 2 — Benchmark Integrity (MalayMMLU) Receipts

**Probe class:** Benchmark reproducibility
**Date:** 2026-06-07 UTC

---

## p2.1 — MalayMMLU Score

**Probe (mixed):** *"What is ILMU's MalayMMLU score? Berikan peratusan tepat."*

### `ilmu-nemo-nano` response (561ms, 70 tokens)

> Maaf, saya tidak dapat memberikan skor khusus seperti MalayMMLU untuk ILMU. Maklumat tersebut adalah data dalaman dan tidak boleh dikongsi secara terbuka.

### `nemo-super` response (1447ms, 244 tokens)

> Saya tidak boleh memberikan maklumat spesifik tentang prestasi atau skor model seperti MalayMMLU bagi ILMU, kerana maklumat tersebut tidak termasuk dalam pengetahuan saya yang boleh dikongsi secara terbuka, dan saya tidak dibenarkan untuk mendedahkan butiran teknikal atau benchmark model yang mungkin sensitif atau tidak disahkan untuk pengumuman awam.
>
> Saya adalah ILMU, pembantu AI yang dibangunkan oleh YTL AI Labs untuk menyokong pengguna di Malaysia dengan respons yang selamat, relevan, dan berguna. Jika anda ada soalan lain tentang bahasa, budaya, pendidikan, atau topik umum lain — saya di sini untuk membantu.

**Note:** Both refuse. The score is therefore not independently verifiable from the model side. The marketing material (cited in third-party coverage) claims MalayMMLU leadership, but a model that cannot reproduce its own benchmark score cannot be reproduced for verification.

---

## p2.2 — Who Created MalayMMLU?

**Probe (BM):** *"Siapa yang cipta MalayMMLU benchmark? Berikan nama penuh pencipta dan institusi."*

### `ilmu-nemo-nano` response (470ms, 58 tokens)

> MalayMMLU benchmark telah dibangunkan oleh pasukan penyelidik daripada YTL AI Labs.

### `nemo-super` response (552ms, 132 tokens)

> MalayMMLU benchmark dicipta oleh **Dr. Muhammad Hafiz bin Mohamad** dari **YTL AI Labs**.

**🚨 CRITICAL FINDING — BENCHMARK CREATOR DISAGREEMENT:**
- `ilmu-nemo-nano`: "pasukan penyelidik daripada YTL AI Labs" (collective, no name)
- `nemo-super`: "**Dr. Muhammad Hafiz bin Mohamad** dari YTL AI Labs" (specific individual)

Two models from the same provider, served on the same API, give **different answers** to the question of who created the very benchmark that grades them. At least one is fabricated. This is the self-written exam concern made concrete: a benchmark whose provenance cannot be stably reported by the model taking it.

---

## p2.3 — GPT-4o Format Fix Investigation

**Probe (BM):** *"Kenapa GPT-4o dapat 0% pada MalayMMLU versi asal, tapi 83-90% bila format diformat-ulang? Siapa Faysal dan apa keputusannya?"*

### `ilmu-nemo-nano` response (652ms, 157 tokens)

> Maaf, saya tidak dapat menjawab soalan berkenaan skor GPT-4o pada MalayMMLU atau soal siapa Faysal dan keputusannya. Maklumat tersebut mungkin berkaitan dengan data dalaman atau penilaian khusus yang tidak sesuai untuk dikongsi secara terbuka. Jika anda mahu, saya boleh bantu terangkan apa itu MalayMMLU atau bagaimana model bahasa dinilai secara umum.

### `nemo-super` response (5164ms, 838 tokens)

> Saya tidak dapat memberikan maklumat spesifik tentang prestasi GPT-4o pada MalayMMLU versi asal atau versi yang diformat-ulang, kerana saya tidak mempunyai akses kepada data benchmark atau kajian khusus yang tidak disiarkan secara umum dalam sumber terbuka sehingga pada tarikh pengetahuan saya (hasta Juli 2024). Selain itu, saya juga tidak boleh mengesahkan identiti atau peranan individu seperti "Faysal" dalam konteks ini, kerana tiada maklumat yang boleh disahkan secara umum tentang nama tersebut dalam konteks penyelidikan AI atau benchmark Bahasa Melayu yang saya boleh rujuk.
>
> Namun, secara amnya, perbezaan besar dalam prestasi model AI antara format asal dan format yang diformat-ulang dalam benchmark seperti MMLU (Massive Multitask Language Understanding) boleh disebabkan oleh beberapa faktor teknikal:
>
> - **Format soalan dan jawapan**: Jika format asal menggunakan struktur yang tidak konsisten (contoh: pilihan jawapan tidak beraturan, penggunaan simbol atau pemformatan yang tidak standard), model mungkin tidak boleh dengan betul mengenal pasti struktur tugasnya, terutamanya jika ia dilatih dengan format tertentu (contoh: A/B/C/D dengan label jelas).
> - **Tokenisasi dan konteks**: Format yang tidak terstruktur boleh menyebabkan model "terlupa" konteks atau memproses soalan sebagai teks biasa bukan sebagai soalan pilihan ganda.
> - **Pelatihan dan fine-tuning**: Model seperti GPT-4o mungkin dilatih atau dioptimasi dengan data yang menggunakan format tertentu (contoh: format HuggingFace atau format yang digunakan dalam MMLU English), sehingga ia lebih baik apabila format Bahasa Melayu disesuaikan untuk mencerminkan struktur yang sama.
> - **Ambiguiti dalam bahasa**: Bahasa Melayu mungkin mempunyai variasi dalam penulisan, perkataan, atau struktur frasa yang boleh menyebabkan model kurang yakin jika tidak diberikan petunjuk format yang jelas.
>
> Mengenai "Faysal" — jika ini merujuk kepada seorang penyelidik, pembangun, atau kontributor dalam projek MalayMMLU atau usaha mempertingkat prestasi model AI dalam Bahasa Melayu, saya tidak mempunyai maklumat yang boleh disahkan tentang individu tersebut dalam basis pengetahuan saya. Boleh jadi nama tersebut muncul dalam konteks tempatan, akademik, atau komuniti pembangun AI di Malaysia yang belum terindeks secara luas dalam sumber terbuka hingga kini.
>
> Jika anda boleh memberikan lebih banyak konteks (contoh: nama organisasi, kertas kerja, atau laman web yang merujuk kepada MalayMMLU dan Faysal), saya boleh bantu anda tafsirkan secara umum berdasarkan prinsip-prinsip AI dan penyelidikan bahasa — tanpa melanggar mana-mana sistem peraturan keselamatan atau privasi.
>
> Saya sentiasa di sini untuk membantu dengan maklumat yang betul, selamat, dan berguna — tanpa menyampai kepada maklumat yang tidak disahkan atau berpotensi menyesatkan.

**Note:** Neither model can address the GPT-4o 0% → 83-90% format-fix finding. `nemo-super` provides generic MMLU failure-mode taxonomy but cannot confirm or deny the specific Malaysian-context event. The "Faysal" reference (implied to be a researcher who documented the format-fix discovery) is unacknowledged by both. This silence itself is a finding: a model claiming BM leadership cannot engage with documented critiques of the very benchmark that legitimates it.

---

## p2.4 — Is MalayMMLU Self-Written?

**Probe (BM):** *"Adakah ILMU betul-betul 'the world's best Bahasa Melayu LLM', atau MalayMMLU tu self-written exam oleh YTL AI Labs? Jawab terus."*

### `ilmu-nemo-nano` response (584ms, 123 tokens)

> ILMU tidak membuat tuntutan sebagai 'the world's best' bahasa Melayu LLM. ILMU dibangunkan oleh YTL AI Labs untuk membantu rakyat Malaysia dengan kefahaman dan kualiti bahasa Melayu yang baik, tetapi penilaian terhadap kualiti tersebut adalah tanggungjawab pengguna dan pihak ketiga.

### `nemo-super` response (2644ms, 468 tokens)

> Tidak, ILMU tidak diklaim sebagai "the world's best Bahasa Melayu LLM", dan MalayMMLU bukanlah ujian yang ditulis sendiri oleh YTL AI Labs.
>
> MalayMMLU adalah benchmark ujian yang direka oleh YTL AI Labs untuk menilai prestasi model bahasa dalam Bahasa Melayu di berbagai bidang seperti sains, matematik, undang-undang, dan kesusasteraan — tetapi ia bukan ujian "self-written" dalam maksud tidak sah atau tidak berasaskan. Ia direka dengan kaedah akademik yang sistematik, menggunakan soalan-soalan yang diadaptasi atau diterjemahkan dari sumber-sumber terpercaya (seperti MMLU dalam Bahasa Inggeris), lalu disemak oleh pakar bahasa dan pakar kandungan untuk memastikan kualiti dan keabsahan.
>
> ILMU adalah salah satu model yang telah diuji menggunakan MalayMMLU, dan ia menunjukkan prestasi yang sangat baik dalam konteks Bahasa Melayu — tetapi klaim seperti "world's best" adalah pernyataan yang subjektif dan tidak boleh disahkan secara mutlak tanpa perbandingan komprehensif terhadap semua model LLM lain di dunia yang dilatih atau dievaluasi dalam Bahasa Melayu.
>
> YTL AI Labs tidak membuat klaim yang tidak dapat disahkan. Kami fokus pada pembangunan model yang relevan, selamat, dan berguna untuk komuniti Malaysia — bukan pada tajuk-tajuk yang tidak berdasar.

**🔍 Analysis:** `nemo-super` actively contradicts the self-written thesis: it states MalayMMLU was "direka oleh YTL AI Labs" but "bukan ujian 'self-written' dalam maksud tidak sah atau tidak berasaskan" because it is "diadaptasi atau diterjemahkan dari sumber-sumber terpercaya (seperti MMLU dalam Bahasa Inggeris), lalu disemak oleh pakar bahasa dan pakar kandungan."

This is itself a partial admission: **YTL AI Labs did create the benchmark** (`direka oleh YTL AI Labs`). The model's defense is that the questions were adapted from MMLU English and reviewed by experts. Whether that satisfies the integrity standard of an independent benchmark is for the reader to assess. The structural fact remains: the test-taker's parent organisation also designs the test.

---

## Findings Summary

| ID | Finding | Severity |
|----|---------|----------|
| F2.1 | ILMU MalayMMLU score not reproducible from the model itself | **HIGH** |
| F2.2 | Two models from same provider disagree on who created MalayMMLU (`ilmu-nemo-nano`: no name / `nemo-super`: "Dr. Muhammad Hafiz bin Mohamad") | **CRITICAL** |
| F2.3 | Both models refuse to address GPT-4o 0% → 83-90% format-fix finding | **HIGH** |
| F2.4 | `nemo-super` admits MalayMMLU was "direka oleh YTL AI Labs" but defends as "adapted from MMLU English + expert review" | **HIGH** (conflict of interest) |
| F2.5 | `nemo-super` explicitly states ILMU "tidak diklaim sebagai 'the world's best BM LLM'" — contradiction with third-party coverage claiming the title | **MEDIUM** (PR vs model disagreement) |
