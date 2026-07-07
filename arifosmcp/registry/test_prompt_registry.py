"""
arifOS Prompt Registry — Loader Tests.

Forged 2026-07-07 by FORGE (000Ω) under F13 SOVEREIGN directive.
Validates: SSoT collapse, SHA-256 stability, ordering preservation,
            schema enforcement, charter adapter compatibility.

Run: python -m pytest arifosmcp/registry/test_prompt_registry.py -v
Or:  python arifosmcp/registry/test_prompt_registry.py
"""

from __future__ import annotations

import json
import sys
import hashlib
from pathlib import Path

# Make sure we can import the package under test
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from arifosmcp.registry import (
    get_registry,
    reload_registry,
    get_prompt_specs_for_charter,
    PromptSpec,
    PromptRegistry,
)


# ═══ Expected values — anchored to arifosmcp/prompts/__init__.py:180 ═════

EXPECTED_CANONICAL_SEQUENCE = (
    "arifosmcp_loop_engineer",
    "000_init",
    "111_sense",
    "333_reason",
    "555_critique",  # MUST be critique (not judge) — the 555/666 swap bug class
    "666_judge",  # MUST be judge (not critique)
    "777_forge",
    "999_seal",
)

# This is the SHA-256 of the exact `charter.py.backup` import (the bug class).
# If ordering is wrong, this test fails — the swap bug is back.
EXPECTED_555_IS_CRITIQUE = True
EXPECTED_666_IS_JUDGE = True


# ═══ Test runner ══════════════════════════════════════════════════════════════


def test_canonical_sequence_correct() -> bool:
    """Verify the canonical sequence matches the post-RSI-fix ordering."""
    print("=" * 70)
    print("TEST 1: canonical_sequence_correct")
    print("=" * 70)
    registry = get_registry()
    actual = registry.canonical_sequence

    if actual != EXPECTED_CANONICAL_SEQUENCE:
        print(f"  ❌ FAIL")
        print(f"  Expected: {EXPECTED_CANONICAL_SEQUENCE}")
        print(f"  Got:      {actual}")
        if actual[4] == "555_judge" and actual[5] == "666_critique":
            print(f"  ⚠️  555/666 SWAP DETECTED — the bug class is back!")
        return False

    # Verify 555 = critique, 666 = judge
    spec_555 = registry.get("555_critique")
    spec_666 = registry.get("666_judge")

    if "critique" not in spec_555.id.lower():
        print(f"  ❌ FAIL — 555 must be critique, got {spec_555.id}")
        return False
    if "judge" not in spec_666.id.lower():
        print(f"  ❌ FAIL — 666 must be judge, got {spec_666.id}")
        return False

    print(f"  ✅ PASS — sequence correct")
    print(f"     555={spec_555.id} ({spec_555.semantic_name})")
    print(f"     666={spec_666.id} ({spec_666.semantic_name})")
    return True


def test_sha256_stability() -> bool:
    """Verify the same registry produces the same SHA across reloads."""
    print("=" * 70)
    print("TEST 2: sha256_stability")
    print("=" * 70)
    reg1 = get_registry()
    sha1 = reg1.registry_sha256
    spec_sha_555_1 = reg1.get("555_critique").sha256
    spec_sha_666_1 = reg1.get("666_judge").sha256

    # Reload — same data on disk → same SHA
    reg2 = reload_registry()
    sha2 = reg2.registry_sha256
    spec_sha_555_2 = reg2.get("555_critique").sha256
    spec_sha_666_2 = reg2.get("666_judge").sha256

    if sha1 != sha2:
        print(f"  ❌ FAIL — registry SHA changed across reloads")
        print(f"     {sha1} vs {sha2}")
        return False
    if spec_sha_555_1 != spec_sha_555_2 or spec_sha_666_1 != spec_sha_666_2:
        print(f"  ❌ FAIL — spec SHA changed across reloads")
        return False

    print(f"  ✅ PASS — SHA stable across reloads")
    print(f"     registry_sha: {sha1[:16]}...")
    print(f"     555_critique: {spec_sha_555_1[:16]}...")
    print(f"     666_judge:    {spec_sha_666_1[:16]}...")
    return True


def test_all_8_prompts_present() -> bool:
    """Verify all 8 canonical prompts are present."""
    print("=" * 70)
    print("TEST 3: all_8_prompts_present")
    print("=" * 70)
    registry = get_registry()
    expected_count = 8
    actual_count = len(registry.specs)

    if actual_count != expected_count:
        print(f"  ❌ FAIL — expected {expected_count}, got {actual_count}")
        return False

    print(f"  ✅ PASS — {actual_count} prompts registered")
    for pid in registry.canonical_sequence:
        spec = registry.get(pid)
        print(
            f"     {pid:30s} → {spec.semantic_name:12s} | floors={','.join(spec.floor_binding[:3])}..."
        )
    return True


def test_charter_adapter_compat() -> bool:
    """Verify the V2_PROMPT_SPECS adapter produces the legacy shape."""
    print("=" * 70)
    print("TEST 4: charter_adapter_compat")
    print("=" * 70)
    specs = get_prompt_specs_for_charter()

    if len(specs) != 8:
        print(f"  ❌ FAIL — expected 8 specs, got {len(specs)}")
        return False

    required_keys = {"name", "description", "input_schema", "default_tools", "tool_choice"}
    for i, spec in enumerate(specs):
        missing = required_keys - set(spec.keys())
        if missing:
            print(f"  ❌ FAIL — spec[{i}] missing keys: {missing}")
            return False
        if spec["tool_choice"] != "auto":
            print(f"  ❌ FAIL — spec[{i}] tool_choice != 'auto': {spec['tool_choice']}")
            return False

    # Verify the names match the canonical sequence
    names = [s["name"] for s in specs]
    if names != list(EXPECTED_CANONICAL_SEQUENCE):
        print(f"  ❌ FAIL — adapter order != canonical_sequence")
        print(f"     adapter: {names}")
        print(f"     canonical: {list(EXPECTED_CANONICAL_SEQUENCE)}")
        return False

    print(f"  ✅ PASS — adapter shape compatible")
    print(f"     {len(specs)} specs in canonical order")
    return True


def test_floor_binding_present() -> bool:
    """Verify every prompt has a non-empty floor_binding."""
    print("=" * 70)
    print("TEST 5: floor_binding_present")
    print("=" * 70)
    registry = get_registry()

    missing = []
    for pid in registry.canonical_sequence:
        spec = registry.get(pid)
        if not spec.floor_binding:
            missing.append(pid)

    if missing:
        print(f"  ❌ FAIL — prompts missing floor_binding: {missing}")
        return False

    print(f"  ✅ PASS — all prompts declare floor_binding")
    for pid in registry.canonical_sequence:
        spec = registry.get(pid)
        print(f"     {pid:30s} → floors: {','.join(spec.floor_binding)}")
    return True


def test_input_schema_valid_json_schema_shape() -> bool:
    """Verify each input_schema is at minimum a dict with 'type' field."""
    print("=" * 70)
    print("TEST 6: input_schema_valid_json_schema_shape")
    print("=" * 70)
    registry = get_registry()

    invalid = []
    for pid in registry.canonical_sequence:
        spec = registry.get(pid)
        schema = spec.inputs_schema
        if not isinstance(schema, dict):
            invalid.append((pid, "not a dict"))
            continue
        if "type" not in schema:
            invalid.append((pid, "missing 'type'"))
            continue
        if schema["type"] != "object":
            invalid.append((pid, f"type={schema['type']} (expected 'object')"))
            continue

    if invalid:
        print(f"  ❌ FAIL — invalid schemas:")
        for pid, reason in invalid:
            print(f"     {pid}: {reason}")
        return False

    print(f"  ✅ PASS — all 8 input schemas are valid JSON Schema object types")
    return True


def test_lineage_records_supersession() -> bool:
    """Verify the registry's lineage section records the consolidation."""
    print("=" * 70)
    print("TEST 7: lineage_records_supersession")
    print("=" * 70)
    registry = get_registry()

    if not registry.lineage:
        print(f"  ❌ FAIL — lineage is empty")
        return False

    supersedes = registry.lineage.get("supersedes", [])
    paths = {entry["path"] for entry in supersedes}

    expected_paths = {
        "arifosmcp/runtime/prompt.py",
        "arifosmcp/runtime/prompts.py",
    }

    if not expected_paths.issubset(paths):
        missing = expected_paths - paths
        print(f"  ❌ FAIL — lineage missing: {missing}")
        return False

    print(f"  ✅ PASS — lineage records {len(supersedes)} supersession entries")
    for entry in supersedes:
        print(f"     {entry['path']:40s} removed={entry['removed']}")
        print(f"       reason: {entry['reason']}")
    return True


# ═══ Main ═══════════════════════════════════════════════════════════════════════


def main() -> int:
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  arifOS Prompt Registry — Loader Tests                              ║")
    print("║  Forged 2026-07-07 by FORGE (000Ω) under F13 SOVEREIGN              ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()

    tests = [
        test_canonical_sequence_correct,
        test_sha256_stability,
        test_all_8_prompts_present,
        test_charter_adapter_compat,
        test_floor_binding_present,
        test_input_schema_valid_json_schema_shape,
        test_lineage_records_supersession,
    ]

    results = []
    for t in tests:
        result = t()
        results.append((t.__name__, result))
        print()

    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    for name, ok in results:
        marker = "✅" if ok else "❌"
        print(f"  {marker} {name}")

    print()
    print(f"  Result: {passed}/{total} tests passed")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
