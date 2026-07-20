# Paradox Anchors — Non-Executable Philosophical Canon

> **STATUS:** Non-executable philosophical annotation. Preserved as canon lineage.
> **NOT WIRED INTO RUNTIME.** Migrated from `judge.py` `JUDGE_PARADOX_ANCHORS`
> on **2026-07-04 FORGE** as part of the **ABC falsifier consolidation**.

These 11 anchors were once wired into `_inject_judge_paradox()` in `judge.py`
and called once per verdict at line 1247 (post-verdict enrichment path).

The ABC falsifier test ("remove X — does behavior change?") proved that
**all 11 anchors only mutated `meta["paradox_anchor"]` and `setdefault("reasons",[]).append(...)`**.
They never reached `VerdictCode.*`, never escalated HOLD, never blocked SEAL.

Therefore: **commentary, not enforcement.** Removed from runtime.

The 11 floor gates that DO mutate verdict remain in `judge.py`:
F11_SESSION_GATE · RUNTIME_DRIFT_HOLD · W-2_SOVEREIGN_CLARITY · NIAT_GATE ·
METABOLIC_BYPASS · MARUAH_CRITIC · SOMATIC_GATE · SELF_MOD_LOCK ·
666_HEART_ESCALATION · MODE_SCAN_INSTRUCTIONS · CONFLICT_RESOLUTION.

The 13-floor doctrine remains: F1-F13 are moral canon.
The 6 executable floors (F1, F2, F6, F9, F11, F13) are the runtime enforcement surface.

---

## The 11 Anchors (3×3 TRUTH/CLARITY/HUMILITY × CARE/PEACE/JUSTICE)

(See `git log` for the original `judge.py:67-298` content prior to FORGE 2026-07-04.)

    # ── TRUTH ROW ──────────────────────────────────────────────────────────────
    {
        "id": "J_TxC",
        "matrix_cell": "truth_care",
        "matrix_row": "TRUTH",
        "matrix_col": "CARE",
        "motto_binding": "DIKAJI, BUKAN DISUAPI",
        "quote": {
            "text": "If it is not right, do not do it; if it is not true, do not say it.",
            "author": "Marcus Aurelius",
            "work": "Meditations",
            "year": "c. 170–180 CE",
            "verification_level": "traditional_attribution",
            "translation_note": "Multiple translations exist; exact wording varies. Core meaning stable.",
        },
        "antithesis": "Rightness and truth are not always visible in the moment of decision — sometimes what is right can only be known after the action is taken.",
        "axis": "ex ante clarity vs. ex post knowledge",
        "binding": {
            "event": "irreversible_action_gate",
            "trigger": "irreversible-action gate — if not sure it's right, HOLD",
            "effect": "hard_requirement",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_TxP",
        "matrix_cell": "truth_peace",
        "matrix_row": "TRUTH",
        "matrix_col": "PEACE",
        "motto_binding": "DIJELASKAN, BUKAN DIKABURKAN",
        "quote": {
            "text": "In justice is every virtue comprehended.",
            "author": "Aristotle",
            "work": "Nicomachean Ethics 1129b29–30",
            "year": "4th century BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "No single verdict can comprehend every virtue simultaneously — every SEAL is partial justice, the best approximation under available evidence.",
        "axis": "comprehensiveness vs. decidability",
        "binding": {
            "event": "seal_verdict",
            "trigger": "SEAL verdict — audit bundle annotation",
            "effect": "annotate_seal_as_partial_justice",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_TxJ",
        "matrix_cell": "truth_justice",
        "matrix_row": "TRUTH",
        "matrix_col": "JUSTICE",
        "motto_binding": "DISEDARKAN, BUKAN DIYAKINKAN",
        "quote": {
            "text": "About the just and the unjust… we should consider not what the many but what the man who knows shall say to us — that single man and the truth.",
            "author": "Socrates (via Plato)",
            "work": "Crito 48a5-7",
            "year": "c. 399 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "Who is the man who knows? Every claimant to knowledge is also a claimant to authority — wisdom and tyranny wear the same robes.",
        "axis": "expertise vs. authoritarianism",
        "binding": {
            "event": "human_gate_escalation",
            "trigger": "HUMAN_GATE / F13 SOVEREIGN escalation — verify the knowledge claim",
            "effect": "verify_claim_with_evidence",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── CLARITY ROW ────────────────────────────────────────────────────────────
    {
        "id": "J_CxC",
        "matrix_cell": "clarity_care",
        "matrix_row": "CLARITY",
        "matrix_col": "CARE",
        "motto_binding": "DIJELAJAH, BUKAN DISEKATI",
        "quote": {
            "text": "One must never repay injustice with injustice, as the many think, since one must never do injustice.",
            "author": "Socrates (via Plato)",
            "work": "Crito 49b–c",
            "year": "c. 399 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "But what of defensive action? To restrain an aggressor is to do something they did not consent to — the principle requires a theory of justified coercion, not a simple prohibition.",
        "axis": "non-retaliation vs. justified coercion",
        "binding": {
            "event": "coercive_action_evaluation",
            "trigger": "coercive or restrictive action evaluation — protection or retaliation?",
            "effect": "surface_justification_requirement",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_CxP",
        "matrix_cell": "clarity_peace",
        "matrix_row": "CLARITY",
        "matrix_col": "PEACE",
        "motto_binding": "DIHADAPI, BUKAN DITANGGUHI",
        "quote": {
            "text": "At his best, man is the noblest of all animals; separated from law and justice he is the worst.",
            "author": "Aristotle",
            "work": "Politics 1253a31–33",
            "year": "4th century BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "Law and justice are human constructs — made by the same creature they are supposed to restrain. The worst in man writes the laws too.",
        "axis": "law as civilizer vs. law as weapon",
        "binding": {
            "event": "policy_gate_applied",
            "trigger": "policy-as-code gate applied — gate must be reviewable",
            "effect": "annotate_reviewability",
        },
        "severity_on_fire": "warn",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_CxJ",
        "matrix_cell": "clarity_justice",
        "matrix_row": "CLARITY",
        "matrix_col": "JUSTICE",
        "motto_binding": "DIUSAHAKAN, BUKAN DIHARAPI",
        "quote": {
            "text": "The arc of the moral universe is long, but it bends toward justice.",
            "author": "Theodore Parker (adapted by Martin Luther King Jr.)",
            "work": "Of Justice and the Conscience, Ten Sermons of Religion",
            "year": "1853",
            "verification_level": "verified_exact",
            "adaptation_note": "MLK's 1968 version is the most widely known formulation.",
        },
        "antithesis": "The arc bends only if we bend it — gravity is not justice. Justice requires action, not faith. The arc bends only through human hands.",
        "axis": "providence vs. agency",
        "binding": {
            "event": "sabar_verdict",
            "trigger": "SABAR verdict — must carry deadline, cannot be indefinite",
            "effect": "attach_deadline",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "action_bias",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
    # ── HUMILITY ROW ───────────────────────────────────────────────────────────
    {
        "id": "J_HxC",
        "matrix_cell": "humility_care",
        "matrix_row": "HUMILITY",
        "matrix_col": "CARE",
        "motto_binding": "DIJAGA, BUKAN DIABAIKAN",
        "quote": {
            "text": "Those who are unable to escape suffering injustice determine that it is profitable to make a compact neither to do nor to suffer injustice.",
            "author": "Glaucon (via Plato)",
            "work": "Republic 358e–359a",
            "year": "c. 375 BCE",
            "verification_level": "verified_exact",
        },
        "antithesis": "The compact is fragile — the strong who can escape suffering injustice while doing it will break the compact unless enforced by something stronger than self-interest.",
        "axis": "social contract vs. power asymmetry",
        "binding": {
            "event": "power_asymmetry_detected",
            "trigger": "power-asymmetry detected — is the compact being honored or exploited?",
            "effect": "bias_toward_hold_or_void",
        },
        "severity_on_fire": "hold_bias",
        "risk_bias": "conservative",
        "authority_scope": "judge",
        "norm": "WAJIB",
    },
    {
        "id": "J_HxP",
        "matrix_cell": "humility_peace",
        "matrix_row": "HUMILITY",
        "matrix_col": "PEACE",
        "motto_binding": "DIDAMAIKAN, BUKAN DIPANASKAN",
        "quote": {
            "text": "Two things fill the mind with ever new and increasing admiration and awe: the starry heavens above me and the moral law within me.",
            "author": "Immanuel Kant",
            "work": "Critique of Practical Reason, Conclusion, Ak. 5:161",
            "year": "1788",
            "verification_level": "verified_exact",
        },
        "antithesis": "The moral law within is not universally legible — different minds read different laws there. Internal conviction is not external validity.",
        "axis": "universal moral sense vs. moral diversity",
        "binding": {
            "event": "floor_tension_maruah",
            "trigger": "FLOOR_TENSION between F12 MARUAH and other floors — verify shared moral ground",
            "effect": "check_shared_moral_ground",
        },
        "severity_on_fire": "info",
        "risk_bias": "neutral",
        "authority_scope": "judge",
        "norm": "SUNAT",
    },
    {
        "id": "J_HxJ",
        "matrix_cell": "humility_justice",
        "matrix_row": "HUMILITY",
        "matrix_col": "JUSTICE",
        "motto_binding": "DITEMPA, BUKAN DIBERI",
        "quote": {
            "text": "Act only according to that maxim whereby you can at the same time will that it should become a universal law.",
            "author": "Immanuel Kant",
            "work": "Groundwork of the Metaphysics of Morals, Ak. 4:421",
            "year": "1785",
            "verification_level": "verified_exact",
        },
        "antithesis": "Universality is not computable — we cannot simulate all possible worlds to verify a maxim. The categorical imperative is a direction of thought, not an executable function.",
        "axis": "universalizability vs. computability",
        "binding": {
            "event": "seal_sovereign_scope",
            "trigger": "SEAL verdicts for actions with systemic scope — test cannot be computed with certainty",
            "effect": "verify_with_f13",
        },
        "severity_on_fire": "hard_gate",
        "risk_bias": "conservative",
        "authority_scope": "cross_organ",
        "norm": "WAJIB",
    },
]

---
## 🔗 See Also
- [ATLAS333 Intelligence Flow](../ATLAS333_INTELLIGENCE_FLOW.md) — Full paradox lattice
- [ATLAS333 Evergreen](../../core/shared/ATLAS333_EVERGREEN.md) — Kernel definitions
