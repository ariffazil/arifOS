# arifOS v1.0.0-SEALED — Kernel Freeze Protocol

> **Status:** PROPOSAL (F13 fire-word: `freeze`) · **Branch:** `freeze/v1.0.0-SEALED`
> **Doctrine:** Kernel (Penyengat) beku & auditable · Garden (Taman) continuous dev di atasnya.
> **Ratified by repetition:** directive delivered 3× by F13 SOVEREIGN, 2026-08-30/31.

## 1. Apa yang beku (The Boundary Cut)

| Dimensi | Kernel (beku) | Garden (hidup) |
|---|---|---|
| Repo path | `/root/arifOS` floors + judge + seal runtime | A-FORGE tools, AAA skills, organ apps, integrations |
| Sifat | Deterministik, auditable, version-locked | Fleksibel, generatif, iteratif |
| Perubahan | HANYA via ritual v1.x (tag→build→attest→seal) | Commit bebas, ΔS≥0 |
| Produk | arifOS v1.0.0-SEALED (IP/SaaS, audit-ready) | Market-facing capabilities |

**Frozen surface (kontrak):** 8 MCP tools exposed, federation schema 2.0.0,
F1–F13 definitions, constitution hash `arifos-constitution-v2026.05.05-SSCT`,
VAULT999 append format.

## 2. Enam keperluan seal (with live status)

| # | Keperluan | Status (2026-08-31) | Bukti |
|---|---|---|---|
| 1 | Tag produk `v1.0.0-SEALED`, clean build, wheel pin | ❌ belum — tags wujud tapi date-rolling (`v2026.08.25`…) | `git tag` |
| 2 | 16 critical module hashes: attestation → **boot-enforced** | ⚠️ hash wujud (`critical_module_hash_count:16`), belum gate | arif_init attestation |
| 3 | **Auditor Export Tool** — Merkle proof generator dari VAULT999 | ❌ belum — chain sihat (2,953 records, 0 broken) tapi tiada verifier pihak ketiga | VAULT999 probe |
| 4 | EU AI Act floor→article mapping (compliance dossier) | ❌ belum ditulis | — |
| 5 | sct-renew liveness | 🟡 transient timeout 04:53 MYT; manual trigger RENEWED 05:07 MYT | journalctl |
| 6 | Kontrak beku documented (surface + schema + floors immutable) | ⚠️ de facto, tidak diikat | health probe |

## 3. Ritual freeze (execution order)

1. **Green the punch list** — selesai #2 (boot gate), #3 (auditor tool), #4 (dossier), final liveness check #5.
2. **Code freeze** — last commit ke kernel pada branch ini; CHANGELOG-1.0.md ditulis.
3. **Tag & build** — `git tag v1.0.0-SEALED` → wheel build → sha256 pin ke dalam release attestation.
4. **Boot verify** — service restart DENGAN hash gate aktif; mismatch hash = kernel refuse boot (hard stop deterministic).
5. **Kernel seal** — `arif_seal` VAULT999: freeze record + tag + wheel hash + surface hash + module hash manifest. **888 trigger — irreversible.**
6. **Garden unpinned** — post-seal, organ repos bebas bergerak; kernel changes hanya via `v1.1.0-SEALED` ritual berulang.

## 4. EU AI Act mapping (dossier skeleton)

| Floor | Artikel | Klaim pematuhan |
|---|---|---|
| F1 AMANAH (reversibility) | Art. 15 (robustness) | Hard-stop pada reversibility failure |
| VAULT999 audit chain | Art. 12 (record-keeping) | Append-only hash chain, 2,953 rekod |
| F13 SOVEREIGN (human oversight) | Art. 14 | 888_HOLD pada semua irreversible |
| ACT/SCT authorization | Art. 9 (risk management) | Scoped capability tokens, TTL, kid |
| F2 TRUTH (epistemic labels) | Art. 13 (transparency) | OBS/DER/INT/SPEC pada semua klaim |

## 5. Post-freeze evolution law

- Kernel repo: **no garden commits**. Perubahan floor = deprecation-registry entry + v1.x ritual.
- Compatibility breaks = major version + federasi migration notice.
- "Never finished" berpindah ke Garden — tempatnya yang sah.

---
*DITEMPA, BUKAN DIBERI. Protocol ini menunggu fire-word `freeze` dari F13.*
