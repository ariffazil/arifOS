"""tests/test_kx010_closed_set_gaps.py — KX-010 closed-set EXTENSION (honest RED baseline).

Sits BESIDE the sealed suite tests/test_kx010_measurement_contract.py
(VD-888-KX010-APEX-MEASUREMENT-CONTRACT-2026-10-27, SEAL_WITH_SCOPE — do not
edit that file; its verdict enumerates authorized builder sites). This file
extends the census to wire surfaces the sealed closed set does not scan, per
the 888-APEX judgment on PROPOSAL-measurement-contract v1.1 (Condition B:
census frozen per-wire-surface):

  GAP-1  /health `fq` block — INSIDE the registered KX-010 scope ("FQ
         published while server itself says scale uncalibrated") but outside
         the sealed scan (thermodynamic/governance/apex_scalars/
         eureka_margin/measurement_basis). fq.value and decomposition.raw are
         physics-labelled scalars with NO kx010.v1 contract.
  GAP-2  A2A membrane :3001 `apex_scalars_local.*` — locally computed scalars
         (e.g. C_dark status=ELEVATED) with NO contract. The replicated
         `apex_scalars.*` beside them DOES carry contracts — the local block
         is the gap.
  GAP-3  A-FORGE :7071 `apex_scalars.*` replicas — carry value/status/source/
         replicated_at but NEITHER a verbatim measurement_contract NOR the
         `legacy: LEGACY_UNCONTRACTED` marker the sealed P5(d) fixture
         contract promises. A consumer cannot tell contracted from legacy.
  CENSUS frame :18085 — 0 physics-vocab paths at freeze (2026-10-28 02:1x
         MYT); pinned green so new physics vocab there cannot arrive silently.

RED is the honest baseline: these tests fail until the dispositions land
(fq contract with declared scale-uncalibrated status; local-scalar contracts
or plain-name renames; replica contract-or-legacy marker). GREEN when the
register falsifier's surface set is clean:
"no scalar wearing physics vocabulary lacks the five-field contract on the wire".

Census discipline (lesson 2026-10-28): physics-vocab detection uses CURATED
WORD-BOUNDED tokens. A bare `phi` substring regex false-positives on
`graphiti*` (the memory service). Token list lives in VOCAB_TOKENS.

Cross-surface tests hit localhost organs; they skip with reason when an
organ is unreachable (CI has no :3001/:7071/:18085). The arifOS-side fq test
runs in-process like the sealed suite.
"""

from __future__ import annotations

import json
import re
import urllib.request
from typing import Any

import pytest

SCHEMA_VERSION = "kx010.v1"

# Curated, word-bounded physics tokens (graphiti lesson — no bare substrings).
VOCAB_TOKENS = [
    r"\bentropy", r"\bpeace", r"\bthermo", r"\benergy", r"C_dark\b", r"C_light\b",
    r"\bphi_e\b", r"\bcooling", r"\bvitality", r"\bpsi_", r"\btau_", r"\bkappa",
    r"\bfq\b", r"\bshadow\b", r"\becho_debt\b", r"\bW3\b",
]
VOCAB_RE = re.compile("|".join(VOCAB_TOKENS), re.IGNORECASE)

# GAP-1 dispositions (sealed-suite pattern: allowlist = contract required,
# roster = named debt. counts/policy are debt, scalars are contracted).
FQ_CONTRACT_REQUIRED = {"value", "decomposition.raw"}
FQ_ROSTER_DEBT = {
    "decomposition.threshold",       # policy constant (fq_policy.yaml F13 RATIFIED)
    "decomposition.window_size",     # count
    "decomposition.sample_size",     # count
    "decomposition.actors_tracked",  # count
}

SURFACES = {
    "a2a_membrane": "http://127.0.0.1:3001/health",
    "aforge": "http://127.0.0.1:7071/health",
    "frame": "http://127.0.0.1:18085/health",
}


def _reachable(url: str) -> bool:
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except Exception:
        return False


def _fetch(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=4) as r:
        return json.load(r)


def _numeric_leaves(node: Any, prefix: str = "") -> list[str]:
    out: list[str] = []
    if isinstance(node, dict):
        for k, v in node.items():
            out.extend(_numeric_leaves(v, f"{prefix}.{k}" if prefix else str(k)))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            out.extend(_numeric_leaves(v, f"{prefix}[{i}]"))
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        out.append(prefix)
    return out


# ── GAP-1: fq block closed set (in-process, mirrors the sealed fixture) ──────


@pytest.fixture(scope="module")
def health() -> dict[str, Any]:
    from starlette.applications import Starlette
    from starlette.testclient import TestClient

    from arifosmcp.runtime.rest_routes import rest_routes as rr

    app = Starlette()
    rr.register_rest_routes(app, {})
    with TestClient(app) as client:
        return client.get("/health").json()


class TestGap1FqBlock:
    def test_fq_numeric_leaves_classified(self, health) -> None:
        fq = health["fq"]
        leaves = set(_numeric_leaves(fq))
        known = FQ_CONTRACT_REQUIRED | FQ_ROSTER_DEBT
        unclassified = leaves - known
        assert not unclassified, (
            f"fq block numeric leaves {sorted(unclassified)} are neither in the "
            f"contract-required set nor the named-debt roster — classify them"
        )

    def test_fq_scalars_carry_contract(self, health) -> None:
        """RED baseline: fq.value / decomposition.raw need a kx010.v1 contract
        (declared scale-uncalibrated) — they are in KX-010's registered scope."""
        fq = health["fq"]
        contracts = fq.get("measurement_contract")
        assert isinstance(contracts, dict), (
            "fq block carries no measurement_contract sub-block — fq.value is a "
            "physics-labelled scalar in KX-010's registered scope (scale-uncalibrated); "
            "contract it (proposal §B: KONTRAK dengan status DINYATAKAN) or rename"
        )
        for name in FQ_CONTRACT_REQUIRED:
            c = contracts.get(name.rsplit(".", 1)[-1] if "." in name else name) or contracts.get(name)
            assert isinstance(c, dict), f"fq measurement_contract lacks entry for '{name}'"
            assert c.get("schema_version") == SCHEMA_VERSION, (
                f"fq.{name}: schema_version {c.get('schema_version')!r} != {SCHEMA_VERSION!r}"
            )


# ── GAP-2 / GAP-3 / CENSUS: cross-surface (live localhost, skip if down) ────


@pytest.mark.parametrize("surface,url", sorted(SURFACES.items()))
class TestCrossSurface:
    def test_gap2_a2a_local_scalars_carry_contracts(self, surface, url) -> None:
        if surface != "a2a_membrane":
            pytest.skip("a2a-only gap")
        if not _reachable(url):
            pytest.skip(f"{surface} unreachable")
        local = _fetch(url).get("apex_scalars_local")
        assert isinstance(local, dict) and local, "apex_scalars_local block missing"
        scalars = {k: v for k, v in local.items() if isinstance(v, dict) and isinstance(v.get("value"), (int, float))}
        assert scalars, "no numeric local scalars found — census stale, refresh freeze"
        missing = sorted(k for k, v in scalars.items() if not isinstance(v.get("measurement_contract"), dict))
        assert not missing, (
            f"a2a apex_scalars_local scalars {missing} carry no measurement_contract — "
            f"locally-computed physics scalars (e.g. C_dark ELEVATED) must be contracted "
            f"or renamed to plain labels until measured (Hukum 2:1)"
        )

    def test_gap3_aforge_replicas_contract_or_legacy(self, surface, url) -> None:
        if surface != "aforge":
            pytest.skip("aforge-only gap")
        if not _reachable(url):
            pytest.skip(f"{surface} unreachable")
        apex = _fetch(url).get("apex_scalars")
        assert isinstance(apex, dict) and apex, "apex_scalars block missing"
        replicas = {k: v for k, v in apex.items() if isinstance(v, dict) and isinstance(v.get("value"), (int, float))}
        assert replicas, "no numeric replicas found — census stale, refresh freeze"
        ambiguous = sorted(
            k for k, v in replicas.items()
            if not isinstance(v.get("measurement_contract"), dict) and "legacy" not in v
        )
        assert not ambiguous, (
            f"aforge apex_scalars replicas {ambiguous} carry neither measurement_contract "
            f"nor the legacy=LEGACY_UNCONTRACTED marker — the P5(d) fixture contract promises "
            f"one or the other, else a consumer cannot tell contracted from legacy"
        )

    def test_census_frame_has_no_physics_vocab(self, surface, url) -> None:
        if surface != "frame":
            pytest.skip("frame-only census pin")
        if not _reachable(url):
            pytest.skip(f"{surface} unreachable")
        hits: list[str] = []

        def walk(node: Any, prefix: str = "") -> None:
            if isinstance(node, dict):
                for k, v in node.items():
                    p = f"{prefix}.{k}" if prefix else str(k)
                    if VOCAB_RE.search(str(k)):
                        hits.append(p)
                    walk(v, p)
            elif isinstance(node, list):
                for i, v in enumerate(node[:5]):
                    walk(v, f"{prefix}[{i}]")

        walk(_fetch(url))
        assert not hits, (
            f"frame :18085 grew physics-vocab paths {hits} — censused clean at "
            f"2026-10-28 freeze; classify any new path (contract or rename)"
        )
