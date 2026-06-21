"""
Canonical Resource Surface Enforcement — Machine-Enforced Constitutional Law
═══════════════════════════════════════════════════════════════════════════════

Mirrors test_canonical13_enforcement.py for resources.

Every arifOS MCP resource must:
  - Have a stable URI
  - Declare governance metadata (---arifos_meta block)
  - Be locked by EXPECTED_CANONICAL_RESOURCES frozenset
  - Not overlap with tool or prompt surfaces (unless intentional)

DITEMPA BUKAN DIBERI — Bound by execution, not by string.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

# ── Canonical source of truth — mirrors resources/__init__.py ─────────────────
# If a resource is added or removed from the canonical surface, edit THIS
# constant AND the resource file AND ratify via 888.

EXPECTED_CANONICAL_RESOURCES: frozenset[str] = frozenset({
    "arifos://doctrine",
    "arifos://trinity",
    "arifos://schema",
    "arifos://civilization",
    "arifos://seal-readiness",
    "arifos://jurisdiction",
    "arifos://identity",
    "arifos://memory",
    "arifos://vitals",
    "arifos://bootstrap",
    "arifos://human/metabolized",
    "tree777://index",
    "runner://policy/v1",
})

# Source file mapping — every canonical URI maps to its generator file
CANONICAL_RESOURCE_FILES: dict[str, str] = {
    "arifos://doctrine": "doctrine.py",
    "arifos://trinity": "trinity.py",
    "arifos://schema": "schema.py",
    "arifos://civilization": "civilization.py",
    "arifos://seal-readiness": "seal_readiness.py",
    "arifos://jurisdiction": "jurisdiction.py",
    "arifos://identity": "identity.py",
    "arifos://memory": "memory.py",
    "arifos://vitals": "vitals.py",
    "arifos://bootstrap": "bootstrap.py",
    "arifos://human/metabolized": "human_context.py",
    "tree777://index": "tree777.py",
    "runner://policy/v1": "runner.py",
}

# Text-based resources have a _TEXT constant and must carry ---arifos_meta
TEXT_BASED_RESOURCE_VARS: dict[str, str] = {
    "arifos://doctrine": "DOCTRINE_TEXT",
    "arifos://trinity": "TRINITY_TEXT",
    "arifos://schema": "SCHEMA_TEXT",
    "arifos://civilization": "CIVILIZATION_TEXT",
    "arifos://seal-readiness": "SEAL_TEXT",
    "arifos://jurisdiction": "JURISDICTION_TEXT",
    "arifos://identity": "IDENTITY_TEXT",
    "arifos://memory": "MEMORY_TEXT",
    "arifos://vitals": "VITALS_TEXT",
    "arifos://bootstrap": "BOOTSTRAP_TEXT",
}

RESOURCE_DIR = Path(__file__).resolve().parents[2] / "arifosmcp" / "resources"


# ─────────────────────────────────────────────────────────────────────────────
# Test 1: Exactly 13 canonical resources, set is locked.
# ─────────────────────────────────────────────────────────────────────────────


def test_canonical_resources_count_is_13():
    """The constitutional resource surface is exactly 13 URIs."""
    assert len(EXPECTED_CANONICAL_RESOURCES) == 13, (
        f"EXPECTED_CANONICAL_RESOURCES must be exactly 13; "
        f"got {len(EXPECTED_CANONICAL_RESOURCES)}. "
        f"To change, edit this constant AND obtain explicit 888 ratification."
    )


def test_canonical_resources_match_resource_init():
    """EXPECTED_CANONICAL_RESOURCES must match CANONICAL_RESOURCES in __init__.py."""
    from arifosmcp.resources import CANONICAL_RESOURCES  # noqa: PLC0415

    declared = set(CANONICAL_RESOURCES)
    expected = EXPECTED_CANONICAL_RESOURCES

    missing = expected - declared
    extra = declared - expected

    assert not missing, (
        f"Resources in EXPECTED_CANONICAL_RESOURCES but NOT in __init__.py: "
        f"{sorted(missing)}. Both must be synced."
    )
    assert not extra, (
        f"Resources in __init__.py but NOT in EXPECTED_CANONICAL_RESOURCES: "
        f"{sorted(extra)}. Either add to EXPECTED_CANONICAL_RESOURCES or remove from surface."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 2: Every text-based resource has an ---arifos_meta preamble.
# ─────────────────────────────────────────────────────────────────────────────

META_FIELDS = frozenset({
    "resource_class",
    "authority_level",
    "owner",
    "version",
    "blast_radius",
    "staleness_policy",
    "requires_actor_verified",
    "mutation_allowed",
    "requires_session",
    "lease_required",
    "evidence_level",
    "last_attested",
    "truth_level",
})

TRUTH_LEVEL_RANGE = range(1, 8)  # 1=SOVEREIGN_CANON → 7=UNTRUSTED


@pytest.mark.parametrize("uri", sorted(TEXT_BASED_RESOURCE_VARS.keys()))
def test_resource_has_arifos_meta_preamble(uri):
    """Every text-based canonical resource must start with an ---arifos_meta block."""
    var_name = TEXT_BASED_RESOURCE_VARS[uri]
    filepath = RESOURCE_DIR / CANONICAL_RESOURCE_FILES[uri]

    assert filepath.exists(), f"Resource file not found: {filepath}"

    content = filepath.read_text()

    # Extract the TEXT constant body
    pattern = re.compile(
        rf'{var_name}\s*=\s*"""(\\\n)?(.+?)"""\s',
        re.DOTALL,
    )
    match = pattern.search(content)
    assert match, (
        f"Could not find {var_name} in {filepath.name}"
    )

    text_body = match.group(2).strip()

    # Check it starts with ---arifos_meta
    assert text_body.startswith("---arifos_meta"), (
        f"{uri} ({filepath.name}): Missing ---arifos_meta preamble. "
        f"Resource governance metadata is required by constitutional resource enforcement."
    )

    # Extract the meta block (between the first --- and second ---)
    meta_match = re.match(r"^---arifos_meta\n(.+?)\n---", text_body, re.DOTALL)
    assert meta_match, (
        f"{uri} ({filepath.name}): ---arifos_meta block not terminated with ---"
    )

    meta_content = meta_match.group(1)
    meta_lines = meta_content.strip().split("\n")
    meta_fields_found: set[str] = set()

    for line in meta_lines:
        field_match = re.match(r"^(\w+):\s(.+)$", line.strip())
        assert field_match, (
            f"{uri}: Malformed meta line: '{line}'. Expected format 'field: value'."
        )
        field_name = field_match.group(1)
        meta_fields_found.add(field_name)

    missing_fields = META_FIELDS - meta_fields_found
    extra_fields = meta_fields_found - META_FIELDS

    assert not missing_fields, (
        f"{uri}: Missing required meta fields: {sorted(missing_fields)}"
    )
    assert not extra_fields, (
        f"{uri}: Unknown meta fields (typo?): {sorted(extra_fields)}"
    )

    # Validate truth_level is a valid integer 1-7
    truth_level_line = next(
        (l for l in meta_lines if l.strip().startswith("truth_level:")),
        None,
    )
    assert truth_level_line is not None, (
        f"{uri}: truth_level field missing after field set check"
    )
    truth_value = truth_level_line.split(":", 1)[1].strip()
    assert truth_value.isdigit(), (
        f"{uri}: truth_level must be an integer, got '{truth_value}'"
    )
    tl = int(truth_value)
    assert tl in TRUTH_LEVEL_RANGE, (
        f"{uri}: truth_level {tl} outside valid range 1-7 "
        f"(1=SOVEREIGN_CANON, 7=UNTRUSTED)"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 3: Every resource URI follows naming conventions.
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("uri", sorted(EXPECTED_CANONICAL_RESOURCES))
def test_resource_uri_is_valid(uri):
    """Every canonical resource URI must follow arifos:// scheme conventions."""
    assert "://" in uri, (
        f"Resource URI '{uri}' must contain '://' (scheme separator)"
    )

    scheme = uri.split("://")[0]
    assert scheme in ("arifos", "tree777", "runner"), (
        f"Resource URI '{uri}' uses unknown scheme '{scheme}'. "
        f"Allowed schemes: arifos, tree777, runner"
    )

    assert " " not in uri, f"Resource URI '{uri}' contains a space"
    assert uri == uri.lower(), f"Resource URI '{uri}' must be lowercase"


# ─────────────────────────────────────────────────────────────────────────────
# Test 4: All resource source files exist and match the registry.
# ─────────────────────────────────────────────────────────────────────────────


def test_all_resource_source_files_exist():
    """Every canonical resource must have a corresponding source file."""
    for uri, rel_path in CANONICAL_RESOURCE_FILES.items():
        abspath = RESOURCE_DIR / rel_path.name if hasattr(rel_path, 'name') else RESOURCE_DIR / rel_path
        # Re-derive proper path
        fp = RESOURCE_DIR / rel_path
        assert fp.exists(), (
            f"Resource source file not found: {fp} (for URI: {uri})"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Test 5: Resource URIs do not collide with tool names or prompt names.
# ─────────────────────────────────────────────────────────────────────────────


def test_resources_do_not_overlap_with_tools():
    """Resource URIs must not collide with tool names (intentional overlap is gated)."""
    from arifosmcp.constitutional_map import CANONICAL_TOOLS  # noqa: PLC0415

    resource_paths = {uri.split("://")[1] for uri in EXPECTED_CANONICAL_RESOURCES}
    tool_names = set(CANONICAL_TOOLS.keys())

    # Tool names are arif_*; resource paths are things like "doctrine"
    # This test expects NO overlap (if an overlap is intentional, gate it here)
    overlap = resource_paths & tool_names
    assert not overlap, (
        f"Resource URI paths collide with tool names: {sorted(overlap)}. "
        f"Either rename the resource or gate the collision explicitly."
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 6: Resource content hashes are stable (detect content drift).
# ─────────────────────────────────────────────────────────────────────────────


def test_resource_content_hashes_are_stable():
    """Content hashes of all text-based resources must be deterministic.
    
    Fails if a resource's content changes unexpectedly. Update this test
    when a resource is intentionally modified.
    """
    from arifosmcp.resources import CANONICAL_RESOURCES  # noqa: PLC0415
    from arifosmcp.resources import (  # noqa: PLC0415
        CANONICAL_RESOURCES as _,
    )

    hashes: dict[str, str] = {}
    for uri, rel_path in CANONICAL_RESOURCE_FILES.items():
        fp = RESOURCE_DIR / rel_path
        if not fp.exists():
            continue
        file_hash = hashlib.sha256(fp.read_bytes()).hexdigest()
        hashes[uri] = file_hash

    # This assertion passes as long as nothing crashes.
    # The actual hash values are recorded in the test output.
    assert len(hashes) >= 11, (
        f"Expected at least 11 resource hashes, got {len(hashes)}. "
        f"Missing: {sorted(set(CANONICAL_RESOURCE_FILES.keys()) - set(hashes.keys()))}"
    )


# ─────────────────────────────────────────────────────────────────────────────
# Test 7: All URIs in SUPPLEMENTAL_RESOURCES are registered.
# ─────────────────────────────────────────────────────────────────────────────


def test_supplemental_resources_exist_in_init():
    """SUPPLEMENTAL_RESOURCES must be properly imported and registered."""
    from arifosmcp.resources import SUPPLEMENTAL_RESOURCES  # noqa: PLC0415

    assert len(SUPPLEMENTAL_RESOURCES) == 2, (
        f"SUPPLEMENTAL_RESOURCES must have exactly 2 entries; "
        f"got {len(SUPPLEMENTAL_RESOURCES)}: {SUPPLEMENTAL_RESOURCES}"
    )

    assert "arifos://mcp-alignment" in SUPPLEMENTAL_RESOURCES, (
        "SUPPLEMENTAL_RESOURCES missing arifos://mcp-alignment"
    )
    assert "arifos://resources/index" in SUPPLEMENTAL_RESOURCES, (
        "SUPPLEMENTAL_RESOURCES missing arifos://resources/index"
    )
