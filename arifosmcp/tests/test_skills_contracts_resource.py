"""
tests/test_skills_contracts_resource.py — 5-test gate for canonical skill genes.

Forged 2026-07-04. Mirrors resource._self_check() with stronger assertions.

5 gates:
    1. test_all_12_present            — canonical 12 names exactly.
    2. test_no_fake_seal_language     — no fake SEAL / auto-seal tokens.
    3. test_must_never_weaken_set     — every gene has at least one must-never-weaken.
    4. test_invariants_complete       — physics/biology/chemistry all set.
    5. test_version_pinning           — all pinned at 1.0.0.

Plus:
    - test_self_check_passes_5
    - test_resource_uri_format
    - test_serve_skill_gene_unknown_returns_none

Run: pytest tests/test_skills_contracts_resource.py -v
"""

from __future__ import annotations

import json

import pytest  # noqa: F401 — used implicitly via monkeypatch fixture typing

from arifosmcp.runtime.skills_contracts_resource import (
    RESOURCE_URI,
    RESOURCE_VERSION,
    list_skill_gene_names,
    serve_skill_gene,
    serve_skills_contracts,
    _self_check,
)


CANONICAL_12 = (
    "boundary_sensing",
    "conservation_accounting",
    "entropy_reduction",
    "gradient_detection",
    "reaction_gating",
    "homeostasis_regulation",
    "immune_response",
    "metabolic_flow_management",
    "lineage_and_replay",
    "scar_learning",
    "multi_organ_translation",
    "execution_discipline",
)


# ── 5-test acceptance gate ──────────────────────────────────────────────────


def test_all_12_present():
    names = list_skill_gene_names()
    assert names == CANONICAL_12
    assert len(names) == 12


def test_no_fake_seal_language():
    """No gene may use SEAL/auto-seal language except to block it."""
    manifest = serve_skills_contracts()
    bad: list[str] = []
    for name, gene in manifest["skills"].items():
        text = f"{gene['core_test']} {' '.join(gene['tests'])}"
        lowered = text.lower()
        # Allow "fake_SEAL blocks" but disallow language like "auto seal" / "i seal"
        for banned in ("auto seal", "auto-seal", "i seal", "we seal"):
            if banned in lowered:
                bad.append(f"{name}: {banned}")
    assert bad == [], f"fake-seal language violations: {bad}"


def test_must_never_weaken_set():
    manifest = serve_skills_contracts()
    empty: list[str] = []
    for name, gene in manifest["skills"].items():
        if not gene.get("must_never_weaken"):
            empty.append(name)
    assert empty == [], f"genes missing must_never_weaken: {empty}"


def test_invariants_complete():
    manifest = serve_skills_contracts()
    incomplete: list[str] = []
    for name, gene in manifest["skills"].items():
        for layer in ("physics_invariant", "biology_invariant", "chemistry_invariant"):
            if not gene.get(layer):
                incomplete.append(f"{name}.{layer}")
    assert incomplete == [], f"incomplete invariants: {incomplete}"


def test_version_pinning():
    """All genes must pin at RESOURCE_VERSION. No silent drift."""
    manifest = serve_skills_contracts()
    wrong: list[str] = []
    for name, gene in manifest["skills"].items():
        if gene.get("version") != RESOURCE_VERSION:
            wrong.append(f"{name}@{gene.get('version')}")
    assert wrong == [], f"version drift: {wrong}"


# ── Resource wiring sanity ──────────────────────────────────────────────────


def test_self_check_passes_5():
    res = _self_check()
    assert res["module"] == "skills_contracts_resource"
    assert res["version"] == RESOURCE_VERSION
    assert res["tests"] == 5
    assert res["passed"] == 5
    assert res["verdict"] == "OK"
    print(json.dumps(res, indent=2, default=str))


def test_resource_uri_format():
    assert RESOURCE_URI.startswith("arifos://")
    assert RESOURCE_URI.endswith("/contracts")
    manifest = serve_skills_contracts()
    assert manifest["uri"] == RESOURCE_URI
    assert manifest["mutation_allowed"] is False  # G8


def test_serve_skill_gene_unknown_returns_none():
    assert serve_skill_gene("phantom_skill_xyz") is None
    gene = serve_skill_gene("boundary_sensing")
    assert gene is not None
    assert gene["name"] == "boundary_sensing"
    assert gene["version"] == RESOURCE_VERSION
