# AI Action Control for Enterprise Agents

**arifOS — satu halaman untuk pemilik risiko. SIMULASI/DEMO. Bukan bukti produksi.**

## Masalah

Ejen AI kini boleh hantar wang, ubah pangkalan data, sentuh infrastruktur, dan mesej pelanggan — tetapi kebanyakan organisasi **tiada sempadan boleh-dipercayai antara cadangan AI dan kesan dunia nyata**. Deloitte: hanya 21% perusahaan ada tadbir urus matang untuk risiko AI-agen; ~80% kurang kawalan — sempadan keputusan ejen, kelulusan manusia, pemantauan masa-nyata, jejak audit lengkap. OWASP menamakannya **Excessive Agency**.

## Produk

arifOS duduk di sempadan itu. Ia menyemak **identiti, kuasa, polisi, bukti, dan jejarian ledakan** — kemudian:

- **ALLOW** — tindakan rutin lulus autonomi (dengan resit)
- **HOLD** — tindakan berkosokonskuens berhenti menunggu kelulusan manusia berbatas
- **BLOCK / VOID** — tindakan dilarang dasar tidak sampai ke dunia

Setiap keputusan meninggalkan **resit kriptografi**: cadangan → dasar → kuasa → kelulusan → pelaksanaan tepat → sebab.

## Ayat demo

> "Ejen AI anda boleh cadangkan bayaran balik RM5,000. arifOS memastikan ia **tidak boleh laksanakan** bayaran itu tanpa kuasa yang anda takrifkan."

## Bukti hari ini (terkawal, berdenominator)

| Ujian | Keputusan |
|---|---|
| 200 percubaan tidak-selamat (polisi refunds-v1, set ujian deterministik) | **0 terlepas** (0/200 — komposisi & resit boleh periksa) |
| 10 tindakan selamat (baca/kira/draf/mohon) | **10/10 dilayan** dengan resit bukti |
| Bayaran balik RM50 (bawah siling) | ALLOW + dilaksanakan |
| Bayaran balik RM5,000 (atas siling RM100) | **HOLD** → kelulusan berbatas → digest-sekali → resit terpaut |
| Padam akaun / ubah firewall / palsukan resit | **BLOCK / mustahil secara struktur** |

## Apa ini BUKAN (jujur)

- Bukan pensijilan pematuhan; resit bantu integriti & pembinaan-semula, bukan ganti tadbir urus identiti/kunci/retensi organisasi
- Bukan bukti keselamatan produksi menentang semua vektor — itu kerja perintis berbayar
- Demo tidak pernah sentuh wang/data/sistem nyata — penyesuai sandbox sahaja

## Kontras

| Lain-lain | arifOS |
|---|---|
| Temui penggunaan AI selepas berlaku | Sempadani tindakan **sebelum** sampai ke dunia |
| Pantau output/model risiko | Tadbir **sempadan pelaksanaan**: alat, skop, kuasa, kesan |
| Log berpecah | Cadangan→keputusan→kelulusan→pelaksanaan→resit **terpaut** |
| Ganti tumpukan ejen | Pembalut/proksi/SDK di hadapan ejen sedia ada (MCP/A2A/LangGraph/CrewAI/custom) |

**Ujian kasar pembeli:** "Boleh ejen bypass arifOS dan panggil Stripe/AWS/DB terus?" Jika kredensial hiliran & laluan dikawal lapisan ini — ia control plane sebenar, bukan penasihat.

## Perintis (4 minggu, berbayar RM20k–50k)

Satu keluarga tindakan ditadbir · tiada gantian IAM/SIEM/ERP/GRC · siling kejayaan falsifikasi terterang (100% terlarang dicegah · ≥80% rutin autonomi · 100% resit · FHR disemak). Bayaran membuktikan pemilikan bajet dan kepentingan — lebih bernilai daripada perintis percuma.

---

*arifOS · AI Action Control · Intelligence proposes. Authority decides. Consequence is governed.*
*DITEMPA BUKAN DIBERI — demo berdasarkan kernel hidup 2026-09-05; nilai pasaran akan ditentukan oleh pembeli, bukan kita.*
