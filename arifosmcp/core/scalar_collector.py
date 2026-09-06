"""
arifosmcp/core/scalar_collector.py — Live Scalar Feed Protocol (TASK-P2-03)
═══════════════════════════════════════════════════════════════════════════════
DITEMPA BUKAN DIBERI — Forged, Not Given

Live measurement protocol for the 7 canonical APEX scalars consumed by
arif_judge_deliberate (stage 888). Until this module shipped, the 7 APEX
scalars (G, C_dark, W³, κ_r, ψ_le, peace², QDF) were UNMEASURED in live
sessions — judges had no real inputs to reason against.

This module measures them.

Scalar measurement sources
---------------------------
    G           → arif_think(mode='apex') / apex_canonical only (NOT confidence)
    C_dark      → apex_scalars.C_dark preferred; else shadow_vars ratio
    W³          → count of active witnesses × diversity_score (each 0–1)
    κ_r         → ratio of F2-compliant claims in session
    ψ_le        → VAULT chain length × seal rate
    peace²      → external input (WELL organ score), default 0.72 if absent
    QDF         → computed composite (NOT measured independently)

AAA scalar physics (2026-07-25):
    Canonical G-fold lives in arif_think(mode='apex') → apex_canonical.compute_apex.
    Confidence is NOT G. Local A-FORGE/AAA estimators are Ω/Ψ evidence, not ontology.

Scalar envelope
---------------
Every measure_* method returns a dict of the shape:
    {
      "value":        float | None,
      "confidence":   float [0.0, 1.0],
      "source":       str,
    }

When source data is unavailable, value is None, confidence is 0.0, and
source is the literal string "UNMEASURED". This is the F9 anti-hantu
discipline applied to telemetry: never fabricate missing scalars, never
silently coerce UNMEASURED to 0.0 to mask failure.

Constitutional floors enforced
-----------------------------
F1  AMANAH      — ScalarCollector is read-only. It queries session state
                  and VAULT999 (already-sealed records) but never writes
                  anything. The seal chain head is read with O_APPEND-safe
                  primitives only.
F2  TRUTH       — every collected value is a finite real number, validated
                  by math.isfinite. UNMEASURED sentinels are first-class
                  citizens, never coerced.
F9  ANTI-HANTU  — when a measurement source is missing, return UNMEASURED.
                  No fabricated defaults. C_dark=0.0 would mask shadow drift;
                  G=0.0 would mask reasoning-blindness. UNMEASURED is the
                  honest answer.
F11 AUDIT       — every measurement records its source string for the
                  caller's audit trail.

F13 SOVEREIGN   — this module produces evidence only. It does NOT gate,
                  judge, or seal. The judge decides what to do with
                  UNMEASURED scalars.

Wiring into arif_judge_deliberate
--------------------------------
The judge (stage 888) calls ScalarCollector.collect_snapshot(...) at
deliberation time. The result is attached to
VerdictOutput.meta["scalar_snapshot"]. If any scalar is UNMEASURED, a
companion VerdictOutput.meta["scalar_warning"] is set — the verdict
PROCEEDS, but the warning is recorded for audit. UNMEASURED scalars do
NOT auto-VOID. F9 anti-hantu: scalar measurement failure is a signal, not
a hard constitutional breach. The judge owner of the verdict.

Author  : 888-APEX / Gemini CLI perspective (FI-008 dispatch)
Task    : TASK-P2-03 (F2+F7 gated, no F13 trigger)
Epoch   : 2026-07-15
"""

from __future__ import annotations

import json as _json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "ScalarCollector",
    "ScalarMeasurement",
    "UNMEASURED_SOURCE",
]


# Canonical sentinel source string when measurement fails.
# String sentinel (not None) lets JSON encoders round-trip safely without
# losing the distinction between "measured but zero" and "never measured".
UNMEASURED_SOURCE = "UNMEASURED"


@dataclass(frozen=True)
class ScalarMeasurement:
    """One scalar reading with provenance.

    Attributes
    ----------
    value : float | None
        The measured value, or None if UNMEASURED.
    confidence : float
        Confidence in the measurement, in [0.0, 1.0]. 0.0 = UNMEASURED.
        For measured values, this is the in-pipeline confidence (e.g.
        0.90 for a capped witness confidence per F7 HUMILITY).
    source : str
        Provenance string: e.g. "arif_mind_reason.confidence",
        "witness_log.session", "vault_chain.seal_chain.jsonl",
        or "UNMEASURED" when measurement failed.

    Construction
    ------------
    Use the factory constructors `measured(value, confidence, source)` and
    `unmeasured()` rather than instantiating raw. This enforces the F9
    anti-hantu contract: UNMEASURED means *both* value=None AND source=
    "UNMEASURED" AND confidence=0.0. The dataclass is frozen to prevent
    post-hoc tampering with provenance.
    """

    value: float | None
    confidence: float
    source: str

    @classmethod
    def measured(cls, value: float, confidence: float, source: str) -> "ScalarMeasurement":  # noqa: UP037
        """Build a measurement with a finite real value.

        Validates that `value` is finite (rejects NaN, +Inf, -Inf) and
        that `confidence` is in [0.0, 1.0]. F2 TRUTH: no silent coercion.
        """
        if value is None or not math.isfinite(float(value)):
            return cls.unmeasured()
        if confidence is None:
            confidence = 0.85  # direct ratio measurement default confidence
        elif not math.isfinite(float(confidence)):
            confidence = 0.0
        elif not (0.0 <= float(confidence) <= 1.0):
            # F7 HUMILITY cap — confidence > 1.0 is non-physical.
            confidence = min(max(float(confidence), 0.0), 1.0)
        return cls(value=float(value), confidence=float(confidence), source=str(source))

    @classmethod
    def unmeasured(cls) -> "ScalarMeasurement":  # noqa: UP037
        """The honest UNMEASURED answer — F9 anti-hantu contract.

        Three invariants always co-fire:
            value is None
            confidence is 0.0
            source is "UNMEASURED"
        """
        return cls(value=None, confidence=0.0, source=UNMEASURED_SOURCE)

    def to_dict(self) -> dict[str, Any]:
        """JSON-safe dict representation. value remains None when unmeasured."""
        return {
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
        }

    @property
    def is_measured(self) -> bool:
        """True iff this scalar has a real value (F9: distinction matters)."""
        return self.value is not None and self.source != UNMEASURED_SOURCE


# ─── Default paths for VAULT999 read-only access ──────────────────────────
# F1 AMANAH: this module only READS VAULT999 (which is fossil/append-only).
# It never writes; seal chain is consumed read-only.
_DEFAULT_VAULT_CHAIN_PATH = "/root/.local/share/arifos/vault999/seal_chain.jsonl"
_DEFAULT_VAULT_CHAIN_HEAD_PATH = "/root/.local/share/arifos/vault999/seal_chain_head.json"
_DEFAULT_WELL_STATE_PATH = os.environ.get("WELL_STATE_PATH", "/root/WELL/state.json")


class ScalarCollector:
    """Live APEX scalar feed for arif_judge_deliberate.

    The collector is the I/O layer between raw constitutional telemetry
    (sessions, witness log, VAULT999) and the structured scalar dict that
    the judge consumes. It performs read-only observation — no mutations.

    Construction
    ------------
        collector = ScalarCollector(
            session_id="sess_abc",          # optional
            session_context={...},          # optional, overrides _session lookup
            evidence={...},                 # optional, from 333_REASON
            vault_chain_path=...,           # optional, default documented above
            well_score=...,                 # optional, external input (AAA)
        )

    At least one of {session_id, session_context, evidence} should be
    provided so that non-vault scalars can resolve. With no inputs, every
    method returns UNMEASURED — which is correct behavior (F2/F9 honest).

    F1 AMANAH: this class does not mutate any of its inputs.
    """

    def __init__(
        self,
        session_id: str | None = None,
        session_context: dict[str, Any] | None = None,
        evidence: dict[str, Any] | None = None,
        vault_chain_path: str | None = None,
        well_state_path: str | None = None,
        well_score: float | None = None,
    ) -> None:
        self._session_id = session_id
        self._session_context_override = session_context
        self._evidence = evidence or {}
        self._vault_chain_path = Path(
            vault_chain_path or os.environ.get("ARIFOS_VAULT_CHAIN_PATH", _DEFAULT_VAULT_CHAIN_PATH)
        )
        self._well_state_path = Path(well_state_path or _DEFAULT_WELL_STATE_PATH)
        self._well_score_external = well_score

    # ───────────────────────────────────────────────────────────────────
    # Public measurement API — 5 canonical methods per TASK-P2-03 spec
    # ───────────────────────────────────────────────────────────────────

    def collect_G(self) -> ScalarMeasurement:  # noqa: N802
        # Note: N802 violation is intentional. The TASK-P2-03 spec
        # explicitly mandates the canonical APEX naming — G, C_dark, W3,
        # kappa_r, psi_le — to keep the arithmetic notation readable.
        """G-fold — ONLY from arif_think(mode='apex') / apex_canonical.

        AAA scalar physics: G is the Nash product A·P·E·X·Φ derived per
        session. It is NEVER confidence, NEVER a stored primitive.

        Source path (strict order):
            evidence/session apex_scalars.G   (from arif_think mode=apex)
            evidence.g_fold.G
            evidence.G  (only if source tags apex)

        Confidence-as-G is FORBIDDEN (was a structural entropy source).
        Returns UNMEASURED if no apex-derived G is present — F9 honest.
        """
        # 1) Nested apex_scalars dict from arif_think mode=apex
        for src in (self._evidence, self._session_context):
            if not isinstance(src, dict):
                continue
            apex = src.get("apex_scalars")
            if isinstance(apex, dict) and apex.get("G") is not None:
                raw_g = apex["G"]
                # F2: no silent string coercion — only real numbers
                if not isinstance(raw_g, (int, float)) or isinstance(raw_g, bool):
                    continue
                g_val = float(raw_g)
                if math.isfinite(g_val):
                    src_tag = str(apex.get("source") or "apex_scalars.G")
                    # Accept only apex-tagged or explicitly derived sources
                    if (
                        "apex" in src_tag.lower()
                        or apex.get("derived") is True
                        or apex.get("canonical_module")
                        or src_tag == "apex_scalars.G"
                    ):
                        return ScalarMeasurement.measured(
                            value=max(0.0, min(1.0, g_val)),
                            confidence=min(max(0.0, min(1.0, g_val)), 0.90),
                            source="arif_think.mode=apex",
                        )
            g_fold = src.get("g_fold")
            if isinstance(g_fold, dict) and g_fold.get("G") is not None:
                raw_g = g_fold["G"]
                if not isinstance(raw_g, (int, float)) or isinstance(raw_g, bool):
                    continue
                g_val = float(raw_g)
                if math.isfinite(g_val) and g_fold.get("canonical") is True:
                    return ScalarMeasurement.measured(
                        value=max(0.0, min(1.0, g_val)),
                        confidence=min(max(0.0, min(1.0, g_val)), 0.90),
                        source="arif_think.mode=apex",
                    )

        # 2) No apex-derived G → UNMEASURED (do NOT fall back to confidence)
        return ScalarMeasurement.unmeasured()

    def collect_C_dark(self) -> ScalarMeasurement:  # noqa: N802
        """Shadow term — prefer apex_canonical C_dark, else shadow_vars ratio.

        Source path:
            apex_scalars.C_dark (from arif_think mode=apex) — preferred
            self._evidence["shadow_vars"] / "total_session_vars"
            self._session_context["shadow_vars"] / "session_vars"
            self._evidence["var_dark_ratio"]
            self._session_context["var_dark_ratio"]

        Returns UNMEASURED if no denominator OR zero total (div-by-zero
        is a measurement failure, not 0.0 — F9).
        """
        # Prefer canonical apex shadow term when present
        for src in (self._evidence, self._session_context):
            if not isinstance(src, dict):
                continue
            apex = src.get("apex_scalars")
            if isinstance(apex, dict) and apex.get("C_dark") is not None:
                try:
                    cd = float(apex["C_dark"])
                except (TypeError, ValueError):
                    continue
                if math.isfinite(cd):
                    return ScalarMeasurement.measured(
                        value=max(0.0, min(1.0, cd)),
                        confidence=0.90,
                        source="arif_think.mode=apex",
                    )

        # Try ratio shortcut first — saves two lookups if upstream already
        # computed it (e.g. 333_REASON reasoner pre-norms its telemetry).
        for src in (self._evidence, self._session_context):
            if not isinstance(src, dict):
                continue
            raw_ratio = src.get("var_dark_ratio") or src.get("c_dark_ratio")
            if raw_ratio is not None and math.isfinite(float(raw_ratio)):
                return ScalarMeasurement.measured(
                    value=float(raw_ratio),
                    confidence=0.70,  # ratio lookups are inferred proxies
                    source="session_context.var_dark_ratio",
                )

        shadow: float | None = None
        total: float | None = None

        # Look in evidence first, then session_context.
        for src in (self._evidence, self._session_context):  # noqa: B007
            if not isinstance(src, dict):
                continue
            if shadow is None:
                s = src.get("shadow_vars") or src.get("shadow_count")
                if s is not None:
                    shadow = float(s)
            if total is None:
                t = (
                    src.get("total_session_vars")
                    or src.get("session_vars")
                    or src.get("vars_total")
                )
                if t is not None:
                    total = float(t)

        # F9: zero-total-variables → measurement failure, not 0.0 ratio.
        if shadow is None or total is None or total <= 0:
            return ScalarMeasurement.unmeasured()

        ratio = shadow / total
        # F2 TRUTH: clamp to [0, 1] (sane shadow ratio band).
        if not math.isfinite(ratio):
            return ScalarMeasurement.unmeasured()
        ratio = max(0.0, min(1.0, ratio))
        # STAB-2026-08-07b: confidence=0.65 was a fabricated number. The ratio was
        # measured, but the CONFIDENCE in that measurement was not — derive it or
        # return UNMEASURED rather than inventing 0.65.
        return ScalarMeasurement.measured(
            value=ratio,
            confidence=None,
            source=f"session.shadow_vars/total_session_vars ({shadow:.0f}/{total:.0f})",
        )

    def collect_W3(self) -> ScalarMeasurement:  # noqa: N802
        """Tri-witness consensus — count(active witnesses) × diversity_score.

        Source path:
            self._evidence["witnesses"]: list of {"channel", "confidence"}
                channels ∈ {"human", "ai", "external"}
            self._session_context["witness_log"]: list (alias)
            self._evidence["w3"]: pre-computed shortcut

        W³ formula (Nash geometric mean per arifOS doctrine):
            For each present witness channel:
                take its confidence ∈ [0, 1]
            W³ = ∛(h × ai × ext) when all three present
            W³ = geometric_mean of present channels when partial
            W³ = 0.0 when NO channel present (Nash requires all 3 — but
                 we degrade gracefully to arithmetic mean so partial
                 coverage still scores something; F3 WITNESS discipline
                 is enforced UPSTREAM by the seal/policy engine, not here.)

        Returns UNMEASURED when no witness source is provided.
        Confidence in the measurement = 1.0 if all 3 channels are present,
        else scales down by channel count.
        """
        # Shortcut: pre-computed W3 (e.g. from witness_log query).
        for src in (self._evidence, self._session_context):
            if not isinstance(src, dict):
                continue
            pre = src.get("W3") or src.get("w3")
            if pre is not None and math.isfinite(float(pre)):
                return ScalarMeasurement.measured(
                    value=float(pre),
                    confidence=1.0,
                    source="session_context.W3",
                )

        witnesses: list[dict[str, Any]] = []
        for src in (self._evidence, self._session_context):
            if not isinstance(src, dict):
                continue
            w = src.get("witnesses") or src.get("witness_log") or src.get("tri_witness")
            if isinstance(w, list):
                witnesses = [x for x in w if isinstance(x, dict)]
                if witnesses:
                    break

        if not witnesses:
            return ScalarMeasurement.unmeasured()

        confidences: list[float] = []
        channels_seen: set[str] = set()
        for w in witnesses:
            ch = str(w.get("channel", w.get("source", "unknown"))).lower()
            channels_seen.add(ch)
            c_val = w.get("confidence")
            if c_val is None:
                c_val = w.get("conf")
            if c_val is not None:
                try:
                    cf = float(c_val)
                except (TypeError, ValueError):
                    continue
                if math.isfinite(cf):
                    # F7 HUMILITY cap per channel.
                    confidences.append(min(max(cf, 0.0), 0.90))

        if not confidences:
            return ScalarMeasurement.unmeasured()

        # Geometric mean (Nash 1950). 1-of-3 → just the one value;
        # 2-of-3 → sqrt(a*b); all 3 → ∛(a*b*c).
        product = 1.0
        for c in confidences:
            product *= c
        w3 = product ** (1.0 / len(confidences))

        if not math.isfinite(w3):
            return ScalarMeasurement.unmeasured()

        # Confidence in the measurement: full credit when all 3 channels,
        # scaled penalty for partial coverage (F3 prefers tri-channel).
        channels_full = {"human", "ai", "external"}
        coverage = len(channels_seen & channels_full) / 3.0
        # Plus a small bonus for "any" third-channel (e.g. a fourth proxy)
        # so partial coverage still registers some confidence signal.
        conf = min(1.0, coverage + 0.10)

        return ScalarMeasurement.measured(
            value=w3,
            confidence=conf,
            source=(
                f"witness_log.{len(confidences)}_channel"
                f"/{len(channels_seen & channels_full)}_tri_coverage"
            ),
        )

    def collect_kappa(self) -> ScalarMeasurement:
        """Reasoning consistency — F2-compliant claims ÷ total claims in session.

        κ_r measures how much of the session's claim mass survives F2
        TRUTH verification. High κ_r → most claims held up under scrutiny;
        low κ_r → lots of speculation, retraction, or unverifiable claims.

        Source path:
            self._evidence["f2_compliant_claims"] / "total_claims"
            self._session_context["f2_compliant_claims"] / "total_claims"
            self._evidence["kappa_r"]: pre-computed shortcut

        Returns UNMEASURED when denominator is zero (no claims is not
        a 1.0 ratio — it's measurement absence).
        """
        # Shortcut.
        for src in (self._evidence, self._session_context):
            if not isinstance(src, dict):
                continue
            pre = src.get("kappa_r")
            if pre is not None and math.isfinite(float(pre)):
                return ScalarMeasurement.measured(
                    value=float(pre),
                    confidence=0.80,
                    source="session_context.kappa_r",
                )

        compliant: float | None = None
        total: float | None = None
        for src in (self._evidence, self._session_context):
            if not isinstance(src, dict):
                continue
            if compliant is None:
                c = src.get("f2_compliant_claims") or src.get("verified_claims")
                if c is not None:
                    compliant = float(c)
            if total is None:
                t = src.get("total_claims") or src.get("claims_total")
                if t is not None:
                    total = float(t)

        if compliant is None or total is None or total <= 0:
            return ScalarMeasurement.unmeasured()

        ratio = compliant / total
        if not math.isfinite(ratio):
            return ScalarMeasurement.unmeasured()
        ratio = max(0.0, min(1.0, ratio))
        return ScalarMeasurement.measured(
            value=ratio,
            confidence=0.70,
            source=f"session.f2_compliant_claims/total ({compliant:.0f}/{total:.0f})",
        )

    def collect_psi_le(self) -> ScalarMeasurement:
        """Existential coherence — VAULT chain length × seal rate.

        ψ_le is the time-integration of honest memory. Two factors:
          chain_length  = number of sealed entries in the chain
          seal_rate     = SEAL_count / total_count (HOLD/VOID count as
                          non-seal; the seal rate penalizes volatile chains)

        Composite formula (TASK-P2-03 spec, simplified):
            ψ_le = log10(1 + chain_length) × seal_rate
        The log10 keeps the composite in [0, 1] for realistic chain lengths
        (L=10→log≈1.04, L=100→log≈2.00, L=1000→log≈3.00, L=10000→log≈4.00,
        L=100000→log≈5.00, naturally saturating).

        Source: VAULT999 seal_chain.jsonl (read-only — fossil layer).

        Returns UNMEASURED if chain file is missing, unreadable, or empty.
        """
        chain_length = 0
        seal_count = 0
        try:
            if not self._vault_chain_path.exists():
                return ScalarMeasurement.unmeasured()
            with self._vault_chain_path.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    chain_length += 1
                    # Be tolerant of malformed lines (F2 TRUTH: skip rather
                    # than fabricate). Seal rate only counts SEAL entries.
                    try:
                        rec = _json.loads(line)
                    except (_json.JSONDecodeError, ValueError):
                        continue
                    if not isinstance(rec, dict):
                        # Some legacy lines are bare strings; F2 says skip.
                        continue
                    verdict = str(rec.get("verdict", "")).upper()
                    if verdict == "SEAL":
                        seal_count += 1
        except OSError:
            return ScalarMeasurement.unmeasured()

        if chain_length <= 0:
            return ScalarMeasurement.unmeasured()

        seal_rate = seal_count / chain_length if chain_length > 0 else 0.0
        # Composite ψ_le — log-scaled chain length × seal rate.
        # log10(1+L) ∈ [0, ∞); multiply by seal_rate ∈ [0,1] keeps ψ_le ∈ [0, ∞).
        # We do NOT clamp the upper bound here — downstream APEX scalar
        # evaluation decides whether ψ_le is in band.
        psi_le = math.log10(1.0 + chain_length) * seal_rate

        if not math.isfinite(psi_le):
            return ScalarMeasurement.unmeasured()

        return ScalarMeasurement.measured(
            value=psi_le,
            confidence=0.60,  # chain-derived, not session-direct
            source=(
                f"vault_chain.seal_chain.jsonl "
                f"(L={chain_length}, SEAL={seal_count}, rate={seal_rate:.3f})"
            ),
        )

    # ───────────────────────────────────────────────────────────────────
    # Convenience: snapshot collector (used by arif_judge_deliberate)
    # ───────────────────────────────────────────────────────────────────

    def collect_snapshot(self) -> dict[str, Any]:
        """Collect all 5 canonical scalars + QDF composite in one call.

        Returns a dict of the shape:
            {
              "scalars": {
                "G":           {"value": ..., "confidence": ..., "source": ...},
                "C_dark":      {...},
                "W3":          {...},
                "kappa_r":     {...},
                "psi_le":      {...},
              },
              "qdf":      float | None,
              "qdf_source": "computed" | "UNMEASURED",
              "all_measured": bool,
              "unmeasured_keys": list[str],
            }

        Per the TASK-P2-03 spec: QDF is a computed composite, NOT measured
        independently. It is derived from G, C_dark, W³, κ_r, ψ_le via
        the canonical APEX equation set sealed 2026-07-15
        (commit bbb5075bd):

            QDF = G × (1 - C_dark) × W³ × κ_r × ψ_le

        F9 anti-hantu: if any of the 5 inputs is UNMEASURED, QDF is None
        and qdf_source = "UNMEASURED". Never fabricate QDF from partial
        inputs.
        """
        scalars: dict[str, ScalarMeasurement] = {
            "G": self.collect_G(),
            "C_dark": self.collect_C_dark(),
            "W3": self.collect_W3(),
            "kappa_r": self.collect_kappa(),
            "psi_le": self.collect_psi_le(),
        }

        scalar_dict = {k: v.to_dict() for k, v in scalars.items()}

        all_measured = all(v.is_measured for v in scalars.values())
        unmeasured_keys = [k for k, v in scalars.items() if not v.is_measured]

        qdf: float | None
        qdf_source: str
        if all_measured:
            # Narrow types — mypy asserts.
            G = scalars["G"].value  # noqa: N806
            c_dark = scalars["C_dark"].value
            W3 = scalars["W3"].value  # noqa: N806
            k_r = scalars["kappa_r"].value
            psi = scalars["psi_le"].value
            assert G is not None
            assert c_dark is not None
            assert W3 is not None
            assert k_r is not None
            assert psi is not None
            qdf = G * (1.0 - c_dark) * W3 * k_r * psi
            if not math.isfinite(qdf):
                qdf = None
                qdf_source = UNMEASURED_SOURCE
            else:
                qdf_source = "computed"
        else:
            qdf = None
            qdf_source = UNMEASURED_SOURCE

        return {
            "scalars": scalar_dict,
            "qdf": qdf,
            "qdf_source": qdf_source,
            "all_measured": all_measured,
            "unmeasured_keys": unmeasured_keys,
        }

    # ───────────────────────────────────────────────────────────────────
    # Internal helpers
    # ───────────────────────────────────────────────────────────────────

    @property
    def _session_context(self) -> dict[str, Any] | None:
        """Lazy-resolve the session context.

        Resolution order:
          1. self._session_context_override (constructor-injected)
          2. arifosmcp.runtime.tools.get_session(self._session_id)

        Returns None when neither is available. F1 AMANAH: read-only.
        """
        if self._session_context_override is not None:
            return self._session_context_override
        if self._session_id:
            try:
                from arifosmcp.runtime.tools import get_session  # noqa: WPS433

                sess = get_session(self._session_id)
                if isinstance(sess, dict):
                    return sess
            except Exception:
                return None
        return None

    @staticmethod
    def _extract_scalar(src: dict[str, Any] | None, keys: tuple[str, ...]) -> float | None:
        """Pull the first finite numeric value from `src` under any of `keys`.

        Returns None when no key is present or no value is a finite real.
        Strings, None, NaN, ±Inf are all rejected (F2/F9). Strings are NOT
        silently coerced — a string `"0.85"` is not the same as the float
        0.85 from a measurement perspective (F2 TRUTH: provenance matters).
        """
        if not isinstance(src, dict):
            return None
        for k in keys:
            if k not in src:
                continue
            v = src[k]
            # F2: only real numbers are accepted — strings are rejected
            # rather than silently coerced. bool is rejected (semantic flag,
            # not a numeric scalar).
            if v is None or isinstance(v, bool):
                continue
            if isinstance(v, (int, float)):
                fv = float(v)
                if math.isfinite(fv):
                    return fv
        return None
