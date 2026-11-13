"""
arifosmcp/resources/eureka_ladder_resource.py — Court of Reality MCP Resource

Serves the Eureka Ladder doctrine (tiga ujian mesin + tangga status + kosakata
verdict FALSE≠VOID) as a kernel resource. Read-only doctrine projection; the
ENFORCER is the A-FORGE actuator, the kernel only reads receipts.

Ratified F13 2026-11-14 (verbatim: "sah D1 ... buka lane eureka") per kernel
patch proposal /root/A-FORGE/tools/eureka_ladder/kernel-patch-proposal.md.

Resource URIs:
  arifos://wisdom/eureka-ladder — Eureka Ladder: Court of Reality doctrine

Provenance: content embedded verbatim from
  /root/A-FORGE/tools/eureka_ladder/EUREKA_LADDER.md (F13 directive 2026-11-01)
Actuator (enforcer, not this resource):
  python3 /root/A-FORGE/tools/eureka_ladder/eureka_ladder.py check|recheck|selftest
Receipts (hash-chained):
  /root/A-FORGE/receipts/eureka_ladder_receipts.jsonl

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json

_EUREKA_LADDER_DOC = """\
# EUREKA LADDER — Court of Reality v1 (F13 directive Arif, 2026-11-01)

> Tiga ujian kena jadi MESIN, sebab manusia (dan Arif sendiri) akan lupa atau
> tipu diri sendiri bila eureka tu cantik sangat. Yang tak lepas tiga ujian
> ini = teks cantik, bukan ilmu.

## Tiga ujian mesin (inti sutra)

1. **FALSIFIER-FIRST** — Tulis apa yang akan bunuh idea SEBELUM percaya.
   Tiada apa boleh memfalsifikasi = bukan idea, itu doa.
2. **AUTHOR ≠ JUDGE** — Pemeriksa tak boleh penulis. Termasuk bila penulis
   tu Arif. Sistem tak boleh jadi saksi tunggal kepada dirinya sendiri (Gödel).
3. **DATED RE-CHECK** — Eureka betul hidup bila disemak kemudian; yang palsu
   mati bila bukti sampai. Tiada tarikh = tiada mahkamah.

## Tangga status (jangan sesekali boolean)

IDEA → CANDIDATE → PRIOR_ART_MAPPED → FALSIFIABLE → INDEPENDENTLY_TESTED
     → TEMPORALLY_WITNESSED → CONSEQUENCE_DEMONSTRATED → PROVISIONALLY_VERIFIED

Yang terakhir pun masih revisable. **IDEA → SEAL terus = kesilapan.**

## Kosakata verdict — FALSE bukan VOID

FALSE   = dakwaan gagal ujian realiti
UNKNOWN = bukti tak cukup
SABAR   = pemerhatian lanjut mungkin selesaikan
HOLD    = jangan proceed sampai kuasa/bukti cukup
VOID    = laluan itu SENDIRI tak boleh diterima perlembagaan
SEAL    = kebenaran terkawal untuk proceed

## Aktuator & resit

Actuator: python3 /root/A-FORGE/tools/eureka_ladder/eureka_ladder.py
(check | recheck | selftest — selftest mesti 3/3 PASS; exit 0=ADVANCE/WITNESSED,
1=PRAYER, 2=HOLD, 3=REFUTED)
Receipts: /root/A-FORGE/receipts/eureka_ladder_receipts.jsonl (hash-chained)
Doktrin penuh: /root/A-FORGE/tools/eureka_ladder/EUREKA_LADDER.md
Skill: /root/AAA/skills/eureka-ladder/SKILL.md

Lineage: F13 directives 2026-11-01 · ClaimNov arXiv 2610.36511 · ToAC Pillar I ·
ratifikasi kosakata FALSE≠VOID F13 2026-11-14.
"""


def register_eureka_ladder_resources(mcp) -> list[str]:
    """Register the Eureka Ladder Court-of-Reality doctrine resource.

    Returns list of registered resource URIs.
    """
    registered: list[str] = []

    @mcp.resource("arifos://wisdom/eureka-ladder")
    def eureka_ladder() -> str:
        """Eureka Ladder — Court of Reality: 3 machine tests, status ladder,
        verdict vocabulary (FALSE ≠ VOID), actuator + receipt contract."""
        result = {
            "uri": "arifos://wisdom/eureka-ladder",
            "title": "Eureka Ladder — Court of Reality v1",
            "ratified": "F13 2026-11-14 (sah D1; buka lane eureka)",
            "source_doctrine": "/root/A-FORGE/tools/eureka_ladder/EUREKA_LADDER.md",
            "enforcer": "A-FORGE actuator (kernel reads receipts only)",
            "actuator": (
                "python3 /root/A-FORGE/tools/eureka_ladder/eureka_ladder.py "
                "check|recheck|selftest"
            ),
            "receipts": "/root/A-FORGE/receipts/eureka_ladder_receipts.jsonl",
            "selftest_verified": "3/3 PASS 2026-11-13T18:44Z (this lane)",
            "doctrine": _EUREKA_LADDER_DOC,
        }
        return json.dumps(result, indent=2, ensure_ascii=False)

    registered.append("arifos://wisdom/eureka-ladder")
    return registered
