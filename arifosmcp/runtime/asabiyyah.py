"""asabiyyah — federation cycle instrument.

Distilled from Ibn Khaldun's *asabiyyah* (al-Muqaddimah, 1377) and the four-stage
cycle (Foundation -> Comfort -> Luxury -> Decline), cross-checked against
Usman Awang's *Melayu* (1992) and Turchin's secular cycles (2009).

The doctrine says: no nation is chosen, no race is exempt, and the mechanism is
the same everywhere. So the mechanism has to be *measurable*, or it is just
another story about identity.

Three computable signals, one classifier:

  CER  ceremony/exercise ratio   -> Luxury signature: production of doctrine
                                    outruns exercise of capability.
  ASD  asabiyyah depth           -> Kafes signature: doctrine is inherited,
                                    but nobody left has *executed* the work.
  ENC  enforcement coverage      -> Kerkoporta signature: a mutation path exists
                                    that does not pass the gate.

Plus two derived readings:

  PATH_OUT   which lever is cheapest to move (the Meiji clause: asabiyyah can be
             rebuilt, so the instrument must always emit a way back)
  GADAI      sovereignty risk: are we celebrating while the village is pawned?

Design law (arifFlow F3 / arifOS F2): this module OBSERVES. It never judges.
Every reading carries `source` + `observed_at`. A reading with no source is a
STORY, not a MIRROR. `NOT_APPLICABLE` is a legal value and is preferred over an
invented number.

Contract: /root/AAA/schemas/asabiyyah-reading.schema.json
No third-party dependencies. Standard library only.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Literal, Sequence

__all__ = [
    "State",
    "Metric",
    "SubstrateReading",
    "CycleVerdict",
    "band_cer",
    "band_asd",
    "band_enc",
    "ceremony_exercise_ratio",
    "asabiyyah_depth",
    "enforcement_coverage",
    "classify_stage",
    "path_out",
    "mirror_check",
    "kampung_gadai_risk",
    "aggregate",
    "DEFAULT_DROP_DIR",
]

State = Literal["MEASURED", "NOT_APPLICABLE", "UNKNOWN"]

DEFAULT_DROP_DIR = Path("/var/lib/arifos/asabiyyah")

# --------------------------------------------------------------------------
# bands — thresholds are declared, not tuned. They encode the doctrine's
# qualitative stages; changing them changes what stage the federation reports,
# so they live in one place with names.
# --------------------------------------------------------------------------

CER_FOUNDATION = 1.5   # doctrine production <= 1.5x exercised capability
CER_COMFORT = 3.0
CER_LUXURY = 6.0       # beyond this the artifact pile is the product
ASD_GENERATIVE = 0.50  # at least half of doctrine-holders also execute
ASD_THIN = 0.40
ASD_KAFES = 0.15       # doctrine is inherited; execution is extinct
ENC_COMPLETE = 1.00    # every protected mutation path passes the gate
ENC_KERKOPORTA = 0.80  # an open postern is an open postern


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


@dataclass
class Metric:
    """One measured value with its provenance. No source => STORY."""

    name: str
    value: float | None
    state: State
    source: str
    observed_at: str
    band: str = ""
    notes: str = ""

    @classmethod
    def na(cls, name: str, reason: str) -> "Metric":
        return cls(
            name=name,
            value=None,
            state="NOT_APPLICABLE",
            source=reason,
            observed_at=_now(),
            band="NOT_APPLICABLE",
        )


@dataclass
class SubstrateReading:
    """One organ's self-measurement. The organ owns its own substrate truth."""

    organ: str
    host: str
    observed_at: str
    metrics: dict[str, Metric] = field(default_factory=dict)
    evidence: dict[str, Any] = field(default_factory=dict)
    reading_version: int = 1

    def to_json(self) -> str:
        return json.dumps(
            {
                "reading_version": self.reading_version,
                "organ": self.organ,
                "host": self.host,
                "observed_at": self.observed_at,
                "metrics": {k: asdict(v) for k, v in self.metrics.items()},
                "evidence": self.evidence,
            },
            indent=2,
            sort_keys=True,
        )


@dataclass
class CycleVerdict:
    """Federation-level observation. NOT a verdict on anyone. F3 observe-only."""

    stage: str
    confidence: float
    reasons: list[str]
    metrics: dict[str, float | None]
    path_out: dict[str, str]
    organs_read: list[str]
    organs_silent: list[str]
    ungated: list[str] = field(default_factory=list)
    observed_at: str = field(default_factory=_now)


# --------------------------------------------------------------------------
# the three signals
# --------------------------------------------------------------------------


def band_cer(x: float | None) -> str:
    if x is None:
        return "NOT_APPLICABLE"
    if x < CER_FOUNDATION:
        return "FOUNDATION"
    if x < CER_COMFORT:
        return "COMFORT"
    if x < CER_LUXURY:
        return "LUXURY"
    return "DECLINE"


def band_asd(x: float | None) -> str:
    if x is None:
        return "NOT_APPLICABLE"
    if x >= ASD_GENERATIVE:
        return "GENERATIVE"
    if x >= ASD_THIN:
        return "THIN"
    if x >= ASD_KAFES:
        return "KAFES_WATCH"
    return "KAFES"


def band_enc(x: float | None) -> str:
    if x is None:
        return "NOT_APPLICABLE"
    if x >= ENC_COMPLETE:
        return "COMPLETE"
    if x >= ENC_KERKOPORTA:
        return "PARTIAL"
    return "KERKOPORTA"


def ceremony_exercise_ratio(
    ceremony_artifacts: int,
    exercised_capabilities: int,
    *,
    source: str,
    observed_at: str | None = None,
) -> Metric:
    """CER = doctrine produced / capability exercised.

    `ceremony_artifacts`: doctrine/policy/ritual artifacts still live (not
    archive, not vendored). `exercised_capabilities`: capabilities with a real
    invocation receipt inside the observation window.

    Zero exercised capabilities with non-zero ceremony is DECLINE by definition
    -- the ratio is undefined, not zero, and undefined-here means nothing is
    being used.
    """
    ts = observed_at or _now()
    if exercised_capabilities <= 0:
        if ceremony_artifacts <= 0:
            return Metric.na("cer", "empty substrate: no ceremony, no exercise")
        # Doctrine is being produced while the capability is never exercised.
        # The ratio is UNDEFINED, not zero -- and undefined-here is the worst
        # reading, not the safest. Value is null (never a non-finite float:
        # json.dumps would emit `Infinity`, which is not valid RFC 8259 and
        # strict parsers reject), while state stays MEASURED because the two
        # counts behind it were both genuinely measured.
        return Metric(
            name="cer",
            value=None,
            state="MEASURED",
            source=source,
            observed_at=ts,
            band="DECLINE",
            notes=(
                f"{ceremony_artifacts} ceremony artifacts, 0 exercised capabilities "
                "-- ratio undefined (doctrine produced, capability never exercised)"
            ),
        )
    value = ceremony_artifacts / exercised_capabilities
    return Metric(
        name="cer",
        value=round(value, 4),
        state="MEASURED",
        source=source,
        observed_at=ts,
        band=band_cer(value),
    )


def asabiyyah_depth(
    applicants: int,
    exercisers: int,
    *,
    source: str,
    observed_at: str | None = None,
) -> Metric:
    """ASD = distinct actors who have EXECUTED / distinct actors who HOLD doctrine.

    Khaldun's engine, operationalised. The Kafes failure is not corruption --
    it is a governing layer raised on outputs it never produced. ASD = 1 means
    exactly one actor still executes; everyone else inherited the summary.
    """
    ts = observed_at or _now()
    if applicants <= 0:
        return Metric.na("asd", "no doctrine holders on record")
    ratio = min(1.0, exercisers / applicants)
    return Metric(
        name="asd",
        value=round(ratio, 4),
        state="MEASURED",
        source=source,
        observed_at=ts,
        band=band_asd(ratio),
        notes=f"{exercisers} executors / {applicants} doctrine holders",
    )


def enforcement_coverage(
    gated_paths: int,
    total_paths: int,
    *,
    source: str,
    observed_at: str | None = None,
    ungated: Sequence[str] = (),
) -> Metric:
    """ENC = protected mutation paths that pass a gate / all mutation paths.

    99% coverage is not "almost complete" -- it is one open postern, and the
    empire falls through the postern. Total paths = 0 is NOT_APPLICABLE, never
    1.0: no paths enumerated is not the same as no paths unprotected.
    """
    ts = observed_at or _now()
    if total_paths <= 0:
        return Metric.na("enc", "no mutation paths enumerated")
    value = min(1.0, gated_paths / total_paths)
    notes = ""
    if ungated:
        notes = "ungated: " + ", ".join(sorted(ungated)[:8])
    return Metric(
        name="enc",
        value=round(value, 4),
        state="MEASURED",
        source=source,
        observed_at=ts,
        band=band_enc(value),
        notes=notes,
    )


# --------------------------------------------------------------------------
# classifier + way back
# --------------------------------------------------------------------------


def _band_of(m: Metric | None, band_fn) -> str | None:
    """Band for one metric, or None if it was not measured.

    Classification reads BANDS, never raw values. The band functions are the
    single source of the thresholds, and this also means a metric whose value
    is legitimately undefined (the zero-division CER case: doctrine produced,
    capability never exercised) still carries its stage meaning -- instead of
    silently reading as "not measured" and flattering the verdict.
    """
    if m is None or m.state != "MEASURED":
        return None
    if m.value is None:
        return m.band or None
    return band_fn(m.value)


def classify_stage(metrics: dict[str, Metric]) -> tuple[str, float, list[str]]:
    """Banded stage from the three signals. Precedence is declared, not tuned."""
    cb = _band_of(metrics.get("cer"), band_cer)
    ab = _band_of(metrics.get("asd"), band_asd)
    eb = _band_of(metrics.get("enc"), band_enc)

    reasons: list[str] = []
    stage = "FOUNDATION"

    kerkoporta = eb == "KERKOPORTA"
    ceremony_overwhelm = cb == "DECLINE"
    kafes = ab == "KAFES"

    if kerkoporta:
        reasons.append("enc band KERKOPORTA: ungated mutation path (Kerkoporta)")
    if ceremony_overwhelm:
        reasons.append("cer band DECLINE: artifact pile is the product")
    if kafes:
        reasons.append("asd band KAFES: doctrine inherited, execution extinct (Kafes)")

    if kerkoporta or ceremony_overwhelm or kafes:
        stage = "DECLINE"
    elif cb == "LUXURY" or ab in ("THIN", "KAFES_WATCH"):
        stage = "LUXURY"
        if cb == "LUXURY":
            reasons.append("cer band LUXURY")
        if ab in ("THIN", "KAFES_WATCH"):
            reasons.append(f"asd band {ab}")
    elif cb == "COMFORT":
        stage = "COMFORT"
        reasons.append("cer band COMFORT")
    else:
        reasons.append("all signals inside Foundation bands")

    measured = sum(1 for m in metrics.values() if m is not None and m.state == "MEASURED")
    confidence = round(min(1.0, measured / 3.0), 2)
    if measured == 0:
        stage = "UNKNOWN"
        reasons = ["no signal measured on any organ"]

    return stage, confidence, reasons


def path_out(metrics: dict[str, Metric]) -> dict[str, str]:
    """The cheapest lever back. Khaldun's cycle is not a death sentence --
    Meiji (1868) and Korea (1953) both rebuilt asabiyyah inside one generation.
    An instrument that only reports decline is a story, not a mirror.
    """
    out: dict[str, str] = {}
    eb = _band_of(metrics.get("enc"), band_enc)
    ab = _band_of(metrics.get("asd"), band_asd)
    cb = _band_of(metrics.get("cer"), band_cer)

    if eb is not None and eb != "COMPLETE":
        out["enc"] = (
            "Close the postern first: enumerate the ungated mutation paths and route "
            "them through the existing gate. Cheapest of the three -- no new capability."
        )
    if ab is not None and ab != "GENERATIVE":
        out["asd"] = (
            "Put a second executor on the primitive: whoever holds the doctrine must "
            "run the work once, receipted. Depth without exercise is Kafes."
        )
    if cb is not None and cb in ("COMFORT", "LUXURY", "DECLINE"):
        out["cer"] = (
            "Stop producing doctrine. Every new artifact must cite the exercised "
            "capability it came from and name the capability it changes."
        )
    if not out:
        out["hold"] = "All three signals inside Foundation bands. Hold; do not add ceremony."
    return out


# --------------------------------------------------------------------------
# the two derived readings
# --------------------------------------------------------------------------


def mirror_check(claim: str, evidence_refs: Iterable[str]) -> dict[str, str]:
    """Cermin bukan cerita. A claim with provenance is a MIRROR; a claim without
    is a STORY that happens to be true sometimes. Usman Awang did not praise the
    Malays -- he showed them a mirror, and a mirror needs no adjectives.
    """
    refs = [r for r in evidence_refs if r and r.strip()]
    if refs:
        return {
            "class": "MIRROR",
            "reason": f"{len(refs)} evidence reference(s) attached",
            "claim": claim,
        }
    return {
        "class": "STORY",
        "reason": "no evidence reference: cannot be checked, therefore cannot be trusted",
        "claim": claim,
    }


def kampung_gadai_risk(
    relinquished_value: float,
    total_value: float,
    *,
    source: str = "sovereign asset ledger",
    observed_at: str | None = None,
) -> Metric:
    """'Sedangkan kampung telah tergadai / Sawah sejalur tinggal sejengkal /
    Tanah sebidang mudah terjual.'

    The stanza Arif's poem ends on is not about poverty. It is about holding the
    rope while someone else draws the bucket -- positional exclusion, not
    incapacity. Measured as the share of sovereign capacity already signed away.
    """
    ts = observed_at or _now()
    if total_value <= 0:
        return Metric.na("gadai", "no asset base on record")
    share = max(0.0, min(1.0, relinquished_value / total_value))
    if share == 0:
        band = "none"
    elif share < 0.15:
        band = "watch"
    elif share < 0.40:
        band = "alert"
    else:
        band = "critical"
    return Metric(
        name="gadai",
        value=round(share, 4),
        state="MEASURED",
        source=source,
        observed_at=ts,
        band=band,
        notes=f"{share:.1%} of asset base relinquished",
    )


# --------------------------------------------------------------------------
# aggregator — the kernel's read of the whole federation
# --------------------------------------------------------------------------


def _read_drop_file(path: Path) -> SubstrateReading | None:
    try:
        raw = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError):
        return None
    metrics = {}
    for name, m in (raw.get("metrics") or {}).items():
        if not isinstance(m, dict):
            continue
        metrics[name] = Metric(
            name=m.get("name", name),
            value=m.get("value"),
            state=m.get("state", "UNKNOWN"),
            source=m.get("source", ""),
            observed_at=m.get("observed_at", ""),
            band=m.get("band", ""),
            notes=m.get("notes", ""),
        )
    return SubstrateReading(
        organ=raw.get("organ", path.stem),
        host=raw.get("host", "unknown"),
        observed_at=raw.get("observed_at", ""),
        metrics=metrics,
        evidence=raw.get("evidence") or {},
        reading_version=int(raw.get("reading_version", 1)),
    )


def _federation_metrics(
    readings: Sequence[SubstrateReading],
) -> tuple[dict[str, Metric], list[str]]:
    """Federate organ readings. Sum the counts, re-derive the ratios -- do NOT
    average the ratios. Averaging ratios lets a quiet organ dilute a loud one;
    the federation's ceremony pile is the sum of its organs' piles.
    """
    ceremony = 0
    exercised = 0
    applicants = 0
    exercisers = 0
    gated = 0
    total_paths = 0
    ungated: list[str] = []
    have: set[str] = set()

    for r in readings:
        ev = r.evidence or {}
        if any(k in ev for k in ("ceremony_artifacts", "exercised_capabilities")):
            ceremony += int(ev.get("ceremony_artifacts", 0) or 0)
            exercised += int(ev.get("exercised_capabilities", 0) or 0)
            have.add("cer")
        if any(k in ev for k in ("doctrine_holders", "executors")):
            applicants += int(ev.get("doctrine_holders", 0) or 0)
            exercisers += int(ev.get("executors", 0) or 0)
            have.add("asd")
        if any(k in ev for k in ("gated_paths", "total_paths")):
            gated += int(ev.get("gated_paths", 0) or 0)
            total_paths += int(ev.get("total_paths", 0) or 0)
            ungated.extend(ev.get("ungated") or [])
            have.add("enc")

    ts = _now()
    src = f"federated from {len(readings)} organ reading(s)"
    metrics: dict[str, Metric] = {}
    if "cer" in have:
        metrics["cer"] = ceremony_exercise_ratio(ceremony, exercised, source=src, observed_at=ts)
        metrics["cer"].notes = f"{ceremony} ceremony artifacts / {exercised} exercised capabilities"
    if "asd" in have:
        metrics["asd"] = asabiyyah_depth(applicants, exercisers, source=src, observed_at=ts)
    if "enc" in have:
        metrics["enc"] = enforcement_coverage(
            gated, total_paths, source=src, observed_at=ts, ungated=ungated
        )
    return metrics, ungated


def aggregate(drop_dir: Path | str | None = None) -> CycleVerdict:
    """Read every organ's SubstrateReading and emit the federation stage."""
    d = Path(drop_dir) if drop_dir else DEFAULT_DROP_DIR
    readings: list[SubstrateReading] = []
    if d.is_dir():
        for f in sorted(d.glob("*.json")):
            r = _read_drop_file(f)
            if r:
                readings.append(r)

    metrics, ungated = _federation_metrics(readings)
    stage, confidence, reasons = classify_stage(metrics)
    return CycleVerdict(
        stage=stage,
        confidence=confidence,
        reasons=reasons,
        metrics={k: m.value for k, m in metrics.items()},
        path_out=path_out(metrics),
        organs_read=[r.organ for r in readings],
        organs_silent=[] if readings else ["ALL - no organ reading found in " + str(d)],
        ungated=sorted(set(ungated)),
    )


def _main(argv: Sequence[str] | None = None) -> int:
    import argparse

    p = argparse.ArgumentParser(prog="asabiyyah", description="federation cycle instrument")
    p.add_argument("--drop-dir", default=str(DEFAULT_DROP_DIR))
    args = p.parse_args(argv)
    v = aggregate(args.drop_dir)
    print(json.dumps(asdict(v), indent=2))
    return 0 if v.stage != "UNKNOWN" else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
