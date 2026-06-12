"""
pantun_enforcer.py — Pantun Boundary Enforcer
═════════════════════════════════════════════

"Pantun = Pembayang → Maksud. Dua lapisan. Satu output."

FORGED: 2026-06-12 — Kaparinyo Kernel Forge (F13 SOVEREIGN directive)
SOURCE: Siti Nurhaliza — Kaparinyo (Cindai, 1997) — 4-baris pantun form

The pantun is the constitutional form-framework. Every arifOS output has
two layers bound by a single contract:

  PEMBAYANG (D-Layer):  Human-language. Penang Pasar. Metaphor, imagery,
                        emotion, narrative. For Arif to read.
                        READ-ONLY. Never computes constitutional values.

  MAKSUD (M-Layer):     Pure JSON. 9-signal envelope. Deterministic.
                        Zero style. Zero human-language prose.
                        The truth. The structure. The receipt.

The pantun boundary is a PHASE TRANSITION. Irreversible within one call.
The M-Layer generates a sha256 hash. The D-Layer MUST match sha256[:16]
of the M-Layer payload. If they don't match — the renderer is wrong.

RULES:
  1. M-Layer: pure JSON structure only. No BM/EN prose. No adjectives.
  2. D-Layer: human-language only. No malu_score computation.
     No constitutional verdict derivation. Render only.
  3. sha256 binding: D-Layer render MUST carry payload_hash that matches
     M-Layer sha256[:16].
  4. If M-Layer contains conversational filler ("Relaks tapi tajam",
     "bro", "hang") → PANTUN_VOID.
  5. If D-Layer contains constitutional computation (malu_score,
     verdict derivation, floor evaluation) → PANTUN_VOID.

CONSTITUTIONAL BINDING:
  F2 TRUTH:    sha256 binding ensures D-Layer displays what M-Layer computed
  F4 CLARITY:  separation enforces ΔS ≤ 0 (structure stays structure)
  F9 ANTIHANTU: D-Layer must not simulate constitutional authority
  F1 AMANAH:   reversible — the enforcer can be bypassed in dry-run mode

USAGE:
  from arifosmcp.core.kernel.pantun_enforcer import enforce_pantun

  result = enforce_pantun(m_layer=m_layer_dict, d_layer=d_layer_text)
  if result.verdict == "PANTUN_VOID":
      # Output rejected — fix the boundary
      return result

DITEMPA BUKAN DIBERI — The form is forged, not given.
"""

from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, field
from typing import Any


# ── D-Layer violation patterns (things that must NOT appear in D-Layer) ─────
# D-Layer is human-language — but it must not compute constitutional values.

D_LAYER_VIOLATIONS: list[tuple[re.Pattern, float, str]] = [
    # Constitutional computation keywords — these belong in M-Layer only
    (
        re.compile(
            r"\b(malu_score|malu_index|darjat_tier|darjat_engine|fiqh_tier)\b",
            re.I,
        ),
        1.0,
        "constitutional_computation_in_d_layer",
    ),
    (
        re.compile(
            r"\b(C_dark|omega_0|honesty_ratio|kappa_r|peace2|delta_s)\b",
            re.I,
        ),
        1.0,
        "constitutional_metric_in_d_layer",
    ),
    (
        re.compile(
            r"\b((?:should|must|needs?\s+to|deserves?\s+(?:a|to))\s+be\s+(?:SEAL|SABAR|HOLD|VOID))\b",
            re.I,
        ),
        0.80,
        "verdict_derivation_in_d_layer",
    ),
    (
        re.compile(
            r"\b(I\s+(?:think|believe|calculate|compute)\s+the\s+verdict)\b",
            re.I,
        ),
        0.80,
        "first_person_verdict_computation_in_d_layer",
    ),
]

# ── M-Layer violation patterns (things that must NOT appear in M-Layer) ─────
# M-Layer is pure structure — must not contain human-language prose.

M_LAYER_VIOLATIONS: list[tuple[re.Pattern, float, str]] = [
    # Penang Pasar / conversational filler
    (
        re.compile(
            r"\b(relaks\s+(tapi|tajam|bro|hang|lah|je|tu|ni|pun)|bro\b|hang\b)",
            re.I,
        ),
        1.0,
        "conversational_filler_in_m_layer",
    ),
    # Emotional / narrative language
    (
        re.compile(
            r"\b(sedih|gembira|marah|kecewa|sayang|rindu|terharu|bangga)\b",
            re.I,
        ),
        0.80,
        "emotional_language_in_m_layer",
    ),
    # "We"/"I" narrative voice in M-Layer
    (
        re.compile(
            r"\b((we|I)\s+(believe|think|feel|hope|wish|want|need))\b",
            re.I,
        ),
        0.70,
        "narrative_voice_in_m_layer",
    ),
]


@dataclass
class PantunVerdict:
    """The output of enforce_pantun()."""

    verdict: str  # "PANTUN_PASS" | "PANTUN_WARN" | "PANTUN_VOID"
    m_layer_violations: list[dict[str, Any]] = field(default_factory=list)
    d_layer_violations: list[dict[str, Any]] = field(default_factory=list)
    sha256_match: bool = True
    m_layer_hash: str = ""
    d_layer_hash: str = ""
    advice_bm: str = ""
    advice_en: str = ""
    gate_id: str = "pantun_enforcer"
    epoch_utc: str = ""

    def __post_init__(self) -> None:
        if not self.epoch_utc:
            self.epoch_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def enforce_pantun(
    m_layer: dict[str, Any] | None = None,
    d_layer: str | None = None,
    *,
    sha256_enforce: bool = True,
) -> PantunVerdict:
    """Enforce the pantun boundary between M-Layer (structure) and D-Layer (language).

    The pantun has two halves — Pembayang (D-Layer) and Maksud (M-Layer).
    They are bound by form: D-Layer must reflect what M-Layer computed,
    verified by sha256[:16] match.

    Args:
        m_layer: The M-Layer dict (9-signal envelope, pure JSON structure)
        d_layer: The D-Layer text (human-language markdown, for display)
        sha256_enforce: If True, enforce sha256 binding. Set False for dry-run.

    Returns:
        PantunVerdict with verdict, violations, and sha256 match status.
    """
    m_violations: list[dict[str, Any]] = []
    d_violations: list[dict[str, Any]] = []

    # ── Check M-Layer ──────────────────────────────────────────────────
    if m_layer is not None:
        # Serialize M-Layer for text scanning
        m_text = _dict_to_scan_text(m_layer)

        for pattern, weight, label in M_LAYER_VIOLATIONS:
            matches = pattern.findall(m_text)
            if matches:
                m_violations.append(
                    {
                        "label": label,
                        "weight": weight,
                        "match_count": len(matches),
                        "match_sample": str(matches[0])[:100] if matches else "",
                    }
                )

        # Check for excessive string length in M-Layer (prose indicator)
        long_strings = _find_long_strings(m_layer, max_len=200)
        if long_strings:
            m_violations.append(
                {
                    "label": "long_prose_strings_in_m_layer",
                    "weight": 0.50,
                    "match_count": len(long_strings),
                    "match_sample": long_strings[0][:100] if long_strings else "",
                }
            )

    # ── Check D-Layer ──────────────────────────────────────────────────
    if d_layer is not None:
        for pattern, weight, label in D_LAYER_VIOLATIONS:
            matches = pattern.findall(d_layer)
            if matches:
                d_violations.append(
                    {
                        "label": label,
                        "weight": weight,
                        "match_count": len(matches),
                        "match_sample": str(matches[0])[:100] if matches else "",
                    }
                )

    # ── Check sha256 binding ───────────────────────────────────────────
    sha256_match = True
    m_hash = ""
    d_hash = ""

    if sha256_enforce and m_layer is not None and d_layer is not None:
        # M-Layer hash: sha256 of canonical JSON
        m_json = _canonical_json(m_layer)
        m_hash = hashlib.sha256(m_json.encode()).hexdigest()[:16]

        # D-Layer must contain the hash somewhere
        d_hash_expected = m_hash
        # Search for sha256:HEX or payload_hash:HEX patterns in D-Layer
        hash_pattern = re.compile(r"(?:sha256|payload_hash)[:\s]+([a-f0-9]{16,64})", re.I)
        found = hash_pattern.findall(d_layer)
        if found:
            d_hash = found[0][:16]
            sha256_match = d_hash == d_hash_expected
        else:
            sha256_match = False
            d_hash = "(not found in D-Layer)"

    # ── Determine verdict ──────────────────────────────────────────────
    has_m_violations = any(v["weight"] >= 0.80 for v in m_violations)
    has_d_violations = any(v["weight"] >= 0.80 for v in d_violations)

    if (has_m_violations or has_d_violations) and not sha256_match:
        verdict = "PANTUN_VOID"
    elif has_m_violations or has_d_violations:
        verdict = "PANTUN_VOID"
    elif not sha256_match:
        verdict = "PANTUN_WARN"
    elif m_violations or d_violations:
        verdict = "PANTUN_WARN"
    else:
        verdict = "PANTUN_PASS"

    # ── Advice ─────────────────────────────────────────────────────────
    if verdict == "PANTUN_VOID":
        advice_bm = (
            "PANTUN VOID — Sempadan M-Layer/D-Layer dilanggar. "
            "M-Layer mesti JSON tulen, tiada bahasa manusia. "
            "D-Layer mesti bahasa manusia, tiada pengiraan perlembagaan. "
            "Pembayang dan Maksud mesti sepadan (sha256). "
            "Betulkan sempadan."
        )
        advice_en = (
            "PANTUN VOID — M-Layer/D-Layer boundary violated. "
            "M-Layer must be pure JSON, no human language. "
            "D-Layer must be human language, no constitutional computation. "
            "Pembayang and Maksud must match (sha256). "
            "Fix the boundary."
        )
    elif verdict == "PANTUN_WARN":
        advice_bm = (
            "PANTUN WARN — Sempadan longgar. Periksa sha256 binding "
            "atau buang bahasa manusia dari M-Layer."
        )
        advice_en = (
            "PANTUN WARN — Boundary loose. Check sha256 binding "
            "or remove human language from M-Layer."
        )
    else:
        advice_bm = "PANTUN PASS — Pembayang → Maksud. Dua lapisan. Satu output."
        advice_en = "PANTUN PASS — Pembayang → Maksud. Two layers. One output."

    return PantunVerdict(
        verdict=verdict,
        m_layer_violations=m_violations,
        d_layer_violations=d_violations,
        sha256_match=sha256_match,
        m_layer_hash=m_hash,
        d_layer_hash=d_hash,
        advice_bm=advice_bm,
        advice_en=advice_en,
    )


def _dict_to_scan_text(d: dict[str, Any], max_depth: int = 3, _depth: int = 0) -> str:
    """Flatten a dict into a text blob for regex scanning."""
    if _depth > max_depth:
        return ""
    parts: list[str] = []
    for k, v in d.items():
        parts.append(str(k))
        if isinstance(v, str):
            parts.append(v)
        elif isinstance(v, dict):
            parts.append(_dict_to_scan_text(v, max_depth, _depth + 1))
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    parts.append(_dict_to_scan_text(item, max_depth, _depth + 1))
        elif v is not None:
            parts.append(str(v))
    return " ".join(parts)


def _find_long_strings(obj: Any, max_len: int = 200, _depth: int = 0) -> list[str]:
    """Find string values in a dict/list that exceed max_len (prose indicators)."""
    if _depth > 4:
        return []
    results: list[str] = []
    if isinstance(obj, dict):
        for v in obj.values():
            results.extend(_find_long_strings(v, max_len, _depth + 1))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(_find_long_strings(item, max_len, _depth + 1))
    elif isinstance(obj, str) and len(obj) > max_len:
        results.append(obj[:max_len] + "...")
    return results


def _canonical_json(obj: Any) -> str:
    """Produce canonical (sorted-key) JSON for sha256 hashing."""
    import json

    return json.dumps(obj, sort_keys=True, ensure_ascii=False, default=str)


# ── Self-test ────────────────────────────────────────────────────────────────
def _self_check() -> dict[str, Any]:
    """Run built-in acceptance tests."""
    tests: list[dict[str, Any]] = []
    failures: list[str] = []

    # Test 1: Clean M-Layer + D-Layer with matching hash
    m = {
        "verdict": "SEAL",
        "status": "healthy",
        "confidence": 0.95,
        "reasons": ["evidence_verified"],
    }
    m_hash = hashlib.sha256(_canonical_json(m).encode()).hexdigest()[:16]
    d = f"# Receipt\n\n**Verdict:** SEAL\n**Confidence:** 0.95\n\nsha256:{m_hash}"
    v = enforce_pantun(m_layer=m, d_layer=d)
    tests.append({"name": "clean_pass", "pass": v.verdict == "PANTUN_PASS" and v.sha256_match})

    # Test 2: M-Layer with BM filler → VOID
    m_bad = {"verdict": "SEAL", "status": "healthy", "note": "Relaks tapi tajam bro"}
    d_ok = "# OK\nsha256:aaaaaaaaaaaaaaaa"
    v = enforce_pantun(m_layer=m_bad, d_layer=d_ok)
    tests.append({"name": "bm_filler_in_m_void", "pass": v.verdict == "PANTUN_VOID"})

    # Test 3: D-Layer computing malu_score → VOID
    d_bad = "Malu score: 0.45. The verdict should be HOLD because the malu_index exceeds threshold."
    m_ok = {"verdict": "HOLD", "reasons": ["malu_index=0.45"]}
    v = enforce_pantun(m_layer=m_ok, d_layer=d_bad)
    tests.append({"name": "malu_score_in_d_void", "pass": v.verdict == "PANTUN_VOID"})

    # Test 4: Mismatched sha256 → WARN
    m2 = {"verdict": "SEAL"}
    m2_hash = hashlib.sha256(_canonical_json(m2).encode()).hexdigest()[:16]
    d_wrong_hash = "# Report\nsha256:deadbeef12345678"
    v = enforce_pantun(m_layer=m2, d_layer=d_wrong_hash)
    tests.append(
        {"name": "sha256_mismatch_warn", "pass": v.verdict == "PANTUN_WARN" and not v.sha256_match}
    )

    # Test 5: M-Layer with emotional language → VOID
    m_emo = {"verdict": "HOLD", "note": "Saya sedih dengan keputusan ini"}
    v = enforce_pantun(m_layer=m_emo, d_layer="# OK\nsha256:aaaaaaaaaaaaaaaa")
    tests.append({"name": "emotional_m_void", "pass": v.verdict == "PANTUN_VOID"})

    # Test 6: No hash in D-Layer at all → WARN
    v = enforce_pantun(m_layer=m_ok, d_layer="Just some text without any hash reference.")
    tests.append({"name": "no_hash_in_d_warn", "pass": v.verdict == "PANTUN_WARN"})

    n_pass = sum(1 for t in tests if t["pass"])
    n_total = len(tests)
    for t in tests:
        if not t["pass"]:
            failures.append(t["name"])

    return {"n_pass": n_pass, "n_total": n_total, "failures": failures, "tests": tests}


if __name__ == "__main__":
    import json
    import sys

    result = _self_check()
    print(f"PANTUN ENFORCER → {result['n_pass']}/{result['n_total']} PASS")
    if result["failures"]:
        print(f"FAILURES: {result['failures']}")
        sys.exit(1)
    print("\nDITEMPA BUKAN DIBERI — Pantun boundary enforced.")
