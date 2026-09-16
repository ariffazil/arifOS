"""G0.7 schema ratchet: every published tool schema is JSON Schema 2020-12
valid, self-contained (no unresolved $ref outside $defs), and security-
critical envelope schemas declare an additionalProperties policy.

Unvalidated schemas are illegible-to-hostile ambiguity: a client (or agent)
acting on a drifting schema is executing a different contract than the
kernel. This gate makes schema drift a build failure.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")
from jsonschema import Draft202012Validator  # noqa: E402

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "arifosmcp" / "schema" / "registry" / "tools"
CANONICAL = ["init", "observe", "think", "route", "memory", "judge", "forge", "seal"]
SCHEMA_FILES = sorted(SCHEMA_DIR.glob("arifos.*.json"))


def _tool_name(f: Path) -> str:
    n = f.name
    n = n[len("arifos."):]
    for suffix in (".schema.json", ".json"):
        if n.endswith(suffix):
            n = n[: -len(suffix)]
            break
    return n


def _schemas():
    if not SCHEMA_FILES:
        pytest.skip("no registry schemas found")
    for f in SCHEMA_FILES:
        yield f.name, json.loads(f.read_text())


def test_canonical_eight_schemas_present():
    names = {_tool_name(f) for f in SCHEMA_FILES}
    missing = set(CANONICAL) - names
    assert not missing, f"missing canonical tool schemas: {missing}"


@pytest.mark.parametrize("name,schema", list(_schemas()))
def test_every_schema_is_2020_12_valid(name, schema):
    Draft202012Validator.check_schema(schema)


@pytest.mark.parametrize("name,schema", list(_schemas()))
def test_no_unresolved_external_refs(name, schema):
    """All $ref must resolve inside the document ($defs/#) — external or
    dangling refs make validation environment-dependent."""
    def _walk(node, defs):
        if isinstance(node, dict):
            ref = node.get("$ref")
            if isinstance(ref, str):
                ok = ref.startswith("#") and (
                    ref in {f"#/$defs/{k}" for k in defs} or ref == "#"
                )
                assert ok, f"{name}: unresolved $ref '{ref}'"
            for v in node.values():
                _walk(v, defs)
        elif isinstance(node, list):
            for v in node:
                _walk(v, defs)

    _walk(schema, set((schema.get("$defs") or {}).keys()))


@pytest.mark.parametrize("name,schema", list(_schemas()))
def test_top_level_declares_additional_properties_policy(name, schema):
    """Security-critical envelopes must not silently accept extra fields —
    either explicitly allow, explicitly deny, or use patternProperties."""
    assert (
        "additionalProperties" in schema
        or "patternProperties" in schema
        or schema.get("type") != "object"
    ), f"{name}: object schema without additionalProperties policy"
