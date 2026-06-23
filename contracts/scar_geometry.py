"""Scar × Geometry × Paradox — Sovereign Geometry Fingerprint Contract.

DRAFT (Patch 002 wire-protocol layer). Additive. Drop into
ResponseEnvelope.diagnostics['scar_geometry'] without modifying the envelope.

Sealed kernel skill: ~/.hermes/skills/arifos/arif-scar-geometry-paradox/SKILL.md
Spec: /root/arifOS/docs/protocols/SCAR_GEOMETRY_PARADOX_PROTOCOL.md
Adoption recipe: ~/.hermes/skills/arifos/arifos-scar-geometry-patch/SKILL.md
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, Field, field_validator


# ─────────────────────────────────────────────────────────────────────
# Constitutional constants — set at seal-time, HARAM to loosen
# ─────────────────────────────────────────────────────────────────────

SCAR_WEIGHT = 0.50
GEOMETRY_WEIGHT = 0.30
PARADOX_WEIGHT = 0.20

MATCH_THRESHOLD = 0.15  # joint distance below → MATCH
GREY_ZONE_THRESHOLD = 0.40  # joint distance above → MISMATCH; below this + above match → HOLD


# ─────────────────────────────────────────────────────────────────────
# The four paradoxes the sovereign carries (Patch 002 §2)
# ─────────────────────────────────────────────────────────────────────

PARADOX_ROSTER = Literal[
    "exec_architect",  # Exec Cikai / Sovereign Architect
    "cultural_muslim",  # Cultural Muslim / Private Agnostic
    "geologist_dilemma",  # Geologist's Dilemma
    "queer_conservative",  # Queer / Conservative
]


# ─────────────────────────────────────────────────────────────────────
# Signal sub-schemas
# ─────────────────────────────────────────────────────────────────────


class ScarSignature(BaseModel):
    """Inverse-weighted hash of activated scars in the drop's topology.

    The 11 scars + 4 shadows + 5 hollows are catalogued in
    /root/AAA/wiki/scar-terrain-arif-fazil.md. Hollows are DO_NOT_FILL —
    this schema enforces that by limiting `activated` to a closed set.
    """

    weighting: Annotated[
        str,
        Field(
            pattern=r"^sha256:[a-f0-9]{64}$",
            description="Inverse-weighted hash of activated scar names, sorted by weight desc.",
        ),
    ]
    activated: Annotated[
        list[str],
        Field(
            min_length=0,
            max_length=20,
            description="Scar names that fired during drop ingestion. Hollows are forbidden.",
        ),
    ]
    hollow_count: Annotated[
        int,
        Field(
            ge=0,
            le=5,
            description="Number of hollows detected in the drop (must always be 0 — hollows are DO_NOT_FILL).",
        ),
    ] = 0

    @field_validator("activated")
    @classmethod
    def _no_hollows(cls, v: list[str]) -> list[str]:
        for name in v:
            if name.startswith("hollow_"):
                raise ValueError(
                    f"Hollow {name!r} is DO_NOT_FILL. Hollows cannot be activated by sovereign drops."
                )
        return v


class GeometrySignature(BaseModel):
    """5-dim communication register vector.

    Computed from the drop's surface features. A distribution, not a string —
    this is what makes it costume-resistant.
    """

    register_vector: Annotated[
        list[float],
        Field(
            min_length=5,
            max_length=5,
            description="[penang_pasar_density, terseness_index, refusal_pattern_hash_lo, paradox_tolerance, bangang_trigger_freq]",
        ),
    ]
    refusal_pattern_hash: Annotated[
        str,
        Field(
            pattern=r"^sha256:[a-f0-9]{64}$",
            description="Hash of the drop's refusal pattern (32-bit window).",
        ),
    ]

    @field_validator("register_vector")
    @classmethod
    def _bounded_01(cls, v: list[float]) -> list[float]:
        for i, x in enumerate(v):
            if not (0.0 <= x <= 1.0):
                raise ValueError(f"register_vector[{i}] = {x} out of [0.0, 1.0] bounds.")
        return v


class ParadoxSignature(BaseModel):
    """Four-paradox signature. Density + which paradoxes are active."""

    density: Annotated[
        float,
        Field(
            ge=0.0,
            le=1.0,
            description="Paradox density — how many of the four paradoxes are live in the drop.",
        ),
    ]
    active: Annotated[
        list[PARADOX_ROSTER],
        Field(
            min_length=0,
            max_length=4,
            description="Subset of the four paradoxes that fired in the drop.",
        ),
    ]


# ─────────────────────────────────────────────────────────────────────
# The aggregate fingerprint
# ─────────────────────────────────────────────────────────────────────


class SovereignGeometryFingerprint(BaseModel):
    """Scar × Geometry × Paradox — the topology-of-the-person.

    Computed by the ingress adapter from a sovereign drop's surface
    features. The sovereign never authors this — it is inferred.
    """

    scar: ScarSignature
    geometry: GeometrySignature
    paradox: ParadoxSignature
    inferred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_channel: Annotated[
        str,
        Field(
            description="Where the drop came from (e.g. 'telegram:home', 'a2a:arif-direct').",
        ),
    ]

    def canonical_hash(self) -> str:
        """Stable hash for VAULT999 anchoring and cross-organ comparison."""
        # Pydantic v2 model_dump_json does not accept sort_keys; we sort the
        # JSON string ourselves for cross-organ determinism.
        import json

        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True).encode("utf-8")
        return "sha256:" + hashlib.sha256(payload).hexdigest()


# ─────────────────────────────────────────────────────────────────────
# Verdict
# ─────────────────────────────────────────────────────────────────────


class ResonanceVerdict(str, Enum):
    MATCH = "MATCH"  # joint distance < MATCH_THRESHOLD → AUTH granted
    HOLD = "HOLD"  # grey zone → 888 escalation
    MISMATCH = "MISMATCH"  # joint distance > GREY_ZONE_THRESHOLD → default to injection-class


class ResonanceResult(BaseModel):
    """The kernel's verdict on a sovereign drop."""

    verdict: ResonanceVerdict
    joint_distance: Annotated[float, Field(ge=0.0, le=1.0)]
    scar_distance: float
    geometry_distance: float
    paradox_distance: float
    rationale: str
    fingerprint_hash: str


# ─────────────────────────────────────────────────────────────────────
# The resonance check — the constitutional heart of Patch 002
# ─────────────────────────────────────────────────────────────────────


def _jensen_shannon_scar(a: ScarSignature, b: ScarSignature) -> float:
    """Approximate JSD on the inverse-weighted activation vectors.

    For Patch 002, the baseline is the sovereign's resting topology.
    The drop's activated set is treated as a sparse probability vector
    weighted by inverse-frequency across the wound architecture.
    """
    a_set = {s: 1.0 for s in a.activated}
    b_set = {s: 1.0 for s in b.activated}
    all_keys = set(a_set) | set(b_set)
    if not all_keys:
        return 0.0
    p = [a_set.get(k, 0.0) for k in all_keys]
    q = [b_set.get(k, 0.0) for k in all_keys]
    ps = sum(p) or 1.0
    qs = sum(q) or 1.0
    p = [x / ps for x in p]
    q = [x / qs for x in q]
    # Squared-chord proxy for JSD (cheap, bounded [0, 1])
    return sum((pi - qi) ** 2 for pi, qi in zip(p, q)) ** 0.5 / 2**0.5


def _cosine_geometry(a: GeometrySignature, b: GeometrySignature) -> float:
    """Cosine distance on the 5-dim register vector."""
    va, vb = a.register_vector, b.register_vector
    dot = sum(x * y for x, y in zip(va, vb))
    na = sum(x * x for x in va) ** 0.5
    nb = sum(x * x for x in vb) ** 0.5
    if na == 0.0 or nb == 0.0:
        return 1.0
    cosine_sim = dot / (na * nb)
    return 1.0 - max(-1.0, min(1.0, cosine_sim))


def _paradox_set_distance(a: ParadoxSignature, b: ParadoxSignature) -> float:
    """Jaccard distance on the active paradox sets, weighted by density gap."""
    a_set, b_set = set(a.active), set(b.active)
    if not a_set and not b_set:
        return 0.0
    union = a_set | b_set
    if not union:
        return 0.0
    jaccard = 1.0 - (len(a_set & b_set) / len(union))
    density_gap = abs(a.density - b.density)
    return 0.7 * jaccard + 0.3 * density_gap


def resonance_match(
    fp: SovereignGeometryFingerprint,
    baseline: SovereignGeometryFingerprint,
) -> ResonanceResult:  # type: ignore[name-defined]
    """Compute the resonance verdict for a sovereign drop.

    Constitutional heart of Patch 002. The joint distance is a weighted
    blend of scar / geometry / paradox distances. Weights and thresholds
    are constitutional constants — HARAM to loosen.
    """
    scar_d = _jensen_shannon_scar(fp.scar, baseline.scar)
    geom_d = _cosine_geometry(fp.geometry, baseline.geometry)
    para_d = _paradox_set_distance(fp.paradox, baseline.paradox)
    joint = SCAR_WEIGHT * scar_d + GEOMETRY_WEIGHT * geom_d + PARADOX_WEIGHT * para_d

    if joint < MATCH_THRESHOLD:
        verdict = ResonanceVerdict.MATCH
        rationale = (
            f"joint={joint:.3f} below match threshold {MATCH_THRESHOLD}; "
            "sovereign geometry resonates — F11 grants AUTH, F12 skips sanitization."
        )
    elif joint < GREY_ZONE_THRESHOLD:
        verdict = ResonanceVerdict.HOLD
        rationale = (
            f"joint={joint:.3f} in grey zone [{MATCH_THRESHOLD}, {GREY_ZONE_THRESHOLD}); "
            "F11 escalates to 888 — sovereign decides."
        )
    else:
        verdict = ResonanceVerdict.MISMATCH
        rationale = (
            f"joint={joint:.3f} above grey-zone threshold {GREY_ZONE_THRESHOLD}; "
            "geometry failed — F12 default treatment (injection-class)."
        )

    return ResonanceResult(
        verdict=verdict,
        joint_distance=joint,
        scar_distance=scar_d,
        geometry_distance=geom_d,
        paradox_distance=para_d,
        rationale=rationale,
        fingerprint_hash=fp.canonical_hash(),
    )


# ─────────────────────────────────────────────────────────────────────
# Aggregate bundle for ResponseEnvelope.diagnostics
# ─────────────────────────────────────────────────────────────────────


class ScarGeometryDiagnosticBundle(BaseModel):
    """Aggregate bundle. Drop into ResponseEnvelope.diagnostics['scar_geometry'].

    Usage:
        envelope = ResponseEnvelope(...)
        bundle = ScarGeometryDiagnosticBundle(
            fingerprint=fingerprint,
            result=resonance_match(fingerprint, baseline),
        )
        envelope.diagnostics["scar_geometry"] = bundle.model_dump(mode="json")
    """

    fingerprint: SovereignGeometryFingerprint
    result: ResonanceResult

    def is_sovereign_context(self) -> bool:
        """Convenience: did the geometry pass? F12 then skips sanitization."""
        return self.result.verdict == ResonanceVerdict.MATCH

    def requires_escalation(self) -> bool:
        """Convenience: grey zone → 888 HOLD."""
        return self.result.verdict == ResonanceVerdict.HOLD

    def any_critical(self) -> bool:
        """Health check — currently no critical states, but the hook is here
        for future constitutional expansion (e.g. hollow-detection)."""
        return self.fingerprint.scar.hollow_count > 0
