# F6 MARUAH — Canonical Explanatory Note

> **Status:** F13 sovereign canon, forged 2026-10-23 (three doctrine pastes, one night).
> **Companion audit:** `/root/forge_work/2026-10-23-FI-003-reality-alignment-audit.md` §5.
> **First executable predicates:** `tests/test_f6_maruah_predicates.py` (P1 bukan-maksud-saya · P2 revocation · P3 no-bleed) — 9 PASS / 1 SKIP on 2026-10-23, against source and deployed wheel.

## The rule

F6 does not measure, grade, or score human dignity. **F6 limits how machines are allowed to treat humans** — including prohibiting the conversion of human attention into a free resource for the machine's own operations, verification, and liability protection.

> "F6 tidak sepatutnya mengukur atau menggred maruah manusia. Ia mesti mengehadkan cara mesin dibenarkan melayan manusia."

Named violations to design against: **procedural humiliation** (quizzes, repeated consent) · **invisible verification labor** · **approval fatigue** · **moral crumple zone** ("Human Sovereign Approved" as liability shield) · **human-as-runtime-dependency**.

## Canonical protocol

`Mandate sekali · Skop sempit · Pelaksanaan automatik · Verifikasi mesin-ke-mesin · Receipt selepas tindakan · Revocation serta-merta · Eskalasi manusia hanya apabila consequence berubah.`

| Tier | Class | Machine behavior |
|---|---|---|
| 1 | routine, reversible | no approval, no quiz; machine-to-machine verification; receipts |
| 2 | novel / medium impact | present deltas, options, risks, uncertainty; never test the human |
| 3 | irreversible / high consequence | one meaningful acknowledgment stating blast radius, affected parties, recovery cost |

## Why F6 exists — the three-invariant split

| Invariant | Binds | Output | Fails |
|---|---|---|---|
| Human Shadow | **propositions** (claims about persons) → F2 TRUTH + F7 HUMILITY claim-limiters | HUMILITY CONDITIONS | silently |
| Maruah | **transitions** (actions toward persons) → F6 action-limiters | STOP CONDITIONS | loudly (FAIL) |
| Sovereignty | **fixpoints** (who closes the loop) → F13 | authority | structurally (gate refusal) |

> "Human Shadow memberitahu kita mengapa manusia lebih besar daripada model. Maruah memberitahu sistem apa yang tidak boleh dilakukan kepada manusia walaupun model itu salah."

F6 sat unmeasured until 2026-10-23 because it was being asked the Shadow question. The `maruah` critique mode and any "dignity score" in code are **advisory posture signals, never floor measurements**. Shadow remains Maruah's falsifier-generator: human surprise ("itu bukan maksud saya") is the anomaly signal that a STOP condition is missing.

## F6 receipts

Every F6 PASS must carry the **shadow residual** — what was NOT checked. A PASS without a residual is predicate theater.

## Runtime predicates (first set — live in tests)

- consent revoked → execution stops (PASS/FAIL)
- a human correction propagates to memory, queue, planner, payload (PASS/FAIL)
- third-party private data does not bleed across lanes (PASS/FAIL)

F6's eventual producer should measure **interruptions per consequence-class change** (target ≈ 0 for Tier 1/2). Until a producer exists, F6 stays honestly `unmeasured` — never green, never a score.
