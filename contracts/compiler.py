"""
contracts/compiler.py — Constitutional Contract Compiler v0.1.0
═════════════════════════════════════════════════════════════════

Eight passes (per sovereign directive 2026-06-22):
  1. load_yaml()
  2. validate_meta_schema()
  3. normalize_names_and_aliases()  — resolve legacy aliases to canonical
  4. expand_taxonomies()             — freeze enums, derive sets
  5. generate_capability_graph()    — runtime capability graph (JSON)
  6. generate_audit_schemas()        — JSON schemas per audit event
  7. generate_conformance_fixtures() — happy + schema-pass/constitution-fail + legacy-alias
  8. emit_runtime_validators()       — Pydantic input/output models

DITEMPA BUKAN DIBERI — Compiled, not hand-waved.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


CONTRACTS_DIR = Path(__file__).parent
PROJECT_ROOT = CONTRACTS_DIR.parent
SSOT_PATH = CONTRACTS_DIR / "tools.yaml"
GENERATED_DIR = CONTRACTS_DIR / "generated"


# ════════════════════════════════════════════════════════════════════════════════
# Pass 1: load_yaml
# ════════════════════════════════════════════════════════════════════════════════


def load_yaml(path: Path) -> dict:
    print(f"  [1/8] load_yaml: {path}")
    if not path.exists():
        sys.exit(f"SSOT not found: {path}")
    doc = yaml.safe_load(path.read_text())
    print(
        f"        contract: {doc['meta_schema']['contract_family']} v{doc['meta_schema']['version']}"
    )
    return doc


# ════════════════════════════════════════════════════════════════════════════════
# Pass 2: validate_meta_schema
# ════════════════════════════════════════════════════════════════════════════════


def _all_tools(doc: dict) -> list[dict]:
    out = []
    for sec in ("canonical_tools", "diagnostic", "federated_organs", "sanctioned_non_arif"):
        out.extend(doc.get(sec, []))
    return out


def validate_meta_schema(doc: dict) -> None:
    print("  [2/8] validate_meta_schema")
    errors: list[str] = []
    tax = doc.get("taxonomies", {})
    axes = {a["id"] for a in doc.get("axes", [])}
    pipeline_stages = set(tax.get("pipeline_stages", []))
    contract_classes = set(tax.get("contract_class", []))
    mutation_classes = set(tax.get("mutation_class", []))
    denial_codes = {d["code"] for d in doc.get("denial_codes", [])}
    audit_events = {a["event"] for a in doc.get("audit_events", [])}
    witness_legs = set(tax.get("witness_legs", []))
    retryabilities = set(tax.get("retryability", []))
    seen_names: set[str] = set()

    for t in _all_tools(doc):
        cn = t.get("canonical_name", "")
        if not cn:
            errors.append("tool missing canonical_name")
        elif cn in seen_names:
            errors.append(f"duplicate canonical_name: {cn}")
        else:
            seen_names.add(cn)
        if t.get("axis") not in axes:
            errors.append(f"{cn}: axis '{t.get('axis')}' not in axes")
        if t.get("pipeline_stage") not in pipeline_stages:
            errors.append(f"{cn}: pipeline_stage '{t.get('pipeline_stage')}' not in taxonomy")
        if t.get("reversibility") not in tax.get("reversibility", []):
            errors.append(f"{cn}: reversibility '{t.get('reversibility')}' not in taxonomy")
        if t.get("blast_radius") not in tax.get("blast_radius", []):
            errors.append(f"{cn}: blast_radius '{t.get('blast_radius')}' not in taxonomy")
        if t.get("authority_required") not in tax.get("authority_required", []):
            errors.append(
                f"{cn}: authority_required '{t.get('authority_required')}' not in taxonomy"
            )
        if t.get("channel") not in tax.get("channel", []):
            errors.append(f"{cn}: channel '{t.get('channel')}' not in taxonomy")
        if t.get("contract_class") not in contract_classes:
            errors.append(f"{cn}: contract_class '{t.get('contract_class')}' not in taxonomy")
        if t.get("mutation_class") not in mutation_classes:
            errors.append(f"{cn}: mutation_class '{t.get('mutation_class')}' not in taxonomy")
        if not t.get("modes"):
            errors.append(f"{cn}: modes is empty")
        for d in t.get("denial_codes", []):
            if d not in denial_codes:
                errors.append(f"{cn}: denial_code '{d}' not in taxonomy")
        for a in t.get("audit_events", []):
            if a not in audit_events:
                errors.append(f"{cn}: audit_event '{a}' not in taxonomy")
        for w in t.get("witness_requirements", []):
            if w not in witness_legs:
                errors.append(f"{cn}: witness_requirement '{w}' not in witness_legs")
        if (
            t.get("channel") == "beta"
            and t.get("authority_required") != "sovereign"
            and not t.get("hold_conditions")
        ):
            errors.append(
                f"{cn}: beta channel needs authority_required=sovereign OR hold_conditions"
            )
        if t.get("channel") == "sandbox" and t.get("reversibility") != "reversible":
            errors.append(f"{cn}: sandbox channel must be reversible")
        if t.get("reversibility") == "irreversible" and t.get("authority_required") != "sovereign":
            errors.append(f"{cn}: irreversible tools need authority_required=sovereign")
        if t.get("blast_radius") == "civilizational" and t.get("authority_required") != "sovereign":
            errors.append(f"{cn}: civilizational blast needs authority_required=sovereign")
        # SEAL-class stricter rules
        if t.get("contract_class") == "seal":
            for req in (
                "requires_verdict_token",
                "requires_epoch_id",
                "requires_receipt_parent_ids",
            ):
                if not t.get(req):
                    errors.append(f"{cn}: SEAL class requires {req}=true")
            if t.get("mutation_class") != "seal":
                errors.append(f"{cn}: SEAL class must have mutation_class=seal")
        if t.get("contract_class") == "gateway" and not t.get("requires_plan"):
            errors.append(f"{cn}: gateway class must have requires_plan=true")

    # Denial codes
    for d in doc.get("denial_codes", []):
        if d.get("retryability") not in retryabilities:
            errors.append(
                f"denial {d.get('code')}: retryability '{d.get('retryability')}' not in taxonomy"
            )
        if d.get("floor") is None:
            errors.append(f"denial {d.get('code')}: missing floor")
        if d.get("severity") is None:
            errors.append(f"denial {d.get('code')}: missing severity")
        if d.get("remediation") is None:
            errors.append(f"denial {d.get('code')}: missing remediation")

    # Legacy aliases
    for la in doc.get("legacy_aliases", []):
        if la.get("canonical") not in seen_names:
            errors.append(
                f"legacy alias {la.get('alias')}: canonical '{la.get('canonical')}' not in tools"
            )

    if errors:
        for e in errors:
            print(f"        ❌ {e}")
        sys.exit(f"Validation failed with {len(errors)} error(s)")
    print(f"        ✓ {len(seen_names)} tools pass all seeds")


# ════════════════════════════════════════════════════════════════════════════════
# Pass 3: normalize_names_and_aliases
# ════════════════════════════════════════════════════════════════════════════════


def normalize_names_and_aliases(doc: dict) -> dict:
    print("  [3/8] normalize_names_and_aliases")
    alias_map: dict[str, str] = {}
    deprecated: dict[str, str] = {}  # alias → sunset date
    for la in doc.get("legacy_aliases", []):
        alias_map[la["alias"]] = la["canonical"]
        deprecated[la["alias"]] = la.get("deprecated_after", "TBD")
    print(f"        ✓ {len(alias_map)} legacy aliases registered")
    return {"alias_map": alias_map, "deprecated": deprecated}


# ════════════════════════════════════════════════════════════════════════════════
# Pass 4: expand_taxonomies
# ════════════════════════════════════════════════════════════════════════════════


def expand_taxonomies(doc: dict) -> dict:
    print("  [4/8] expand_taxonomies")
    tax = doc.get("taxonomies", {})
    out = {
        "reversibility": set(tax.get("reversibility", [])),
        "blast_radius": set(tax.get("blast_radius", [])),
        "authority_required": set(tax.get("authority_required", [])),
        "channel": set(tax.get("channel", [])),
        "verdicts": set(tax.get("verdicts", [])),
        "witness_legs": set(tax.get("witness_legs", [])),
        "pipeline_stages": set(tax.get("pipeline_stages", [])),
        "contract_class": set(tax.get("contract_class", [])),
        "mutation_class": set(tax.get("mutation_class", [])),
        "retryability": set(tax.get("retryability", [])),
    }
    print("        ✓ 10 taxonomies expanded to sets")
    return out


# ════════════════════════════════════════════════════════════════════════════════
# Pass 5: generate_capability_graph
# ════════════════════════════════════════════════════════════════════════════════


def _tool_fingerprint(tool: dict) -> str:
    canonical = json.dumps(tool, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical.encode()).hexdigest()[:16]}"


REV_MAP = {
    "reversible": "R1_EPHEMERAL_READ",
    "guarded": "R2_REVERSIBLE_WRITE",
    "irreversible": "R4_IRREVERSIBLE",
}
BLAST_MAP = {"low": "LOCAL", "medium": "ORGAN", "high": "FEDERATION", "civilizational": "EXTERNAL"}
AUTH_MAP = {"public": "LOW", "operator": "HIGH", "sovereign": "SOVEREIGN"}


def generate_capability_graph(doc: dict, norm: dict, tax: dict) -> dict:
    print("  [5/8] generate_capability_graph")
    nodes: list[dict] = []
    for t in _all_tools(doc):
        section = next(
            (
                s
                for s in (
                    "canonical_tools",
                    "diagnostic",
                    "federated_organs",
                    "sanctioned_non_arif",
                )
                if t in doc.get(s, [])
            ),
            "unknown",
        )
        rev = t.get("reversibility", "reversible")
        blast = t.get("blast_radius", "low")
        auth = t.get("authority_required", "public")
        node = {
            "capability_id": f"{section}.{t['canonical_name']}",
            "tool_name": t["canonical_name"],
            "server_id": "local",
            "description": t.get("role", ""),
            "authority_required": AUTH_MAP.get(auth, "LOW"),
            "requires_888_hold": auth == "sovereign" or rev == "irreversible",
            "mutation_class": t.get("mutation_class", "read"),
            "irreversible": rev == "irreversible",
            "blast_radius": BLAST_MAP.get(blast, "LOCAL"),
            "resource_class": "MEMORY",
            "organ_id": "arifOS" if section != "federated_organs" else "federation",
            "trust_state": "TRUSTED_READ"
            if t.get("mutation_class") in ("read",)
            else "TRUSTED_MUTATE",
            "requires_external_witness": bool(t.get("witness_requirements")),
            "channel": t.get("channel", "stable"),
            "contract_class": t.get("contract_class", "ordinary"),
            "axis": t.get("axis", ""),
            "pipeline_stage": t.get("pipeline_stage", ""),
            "modes": t.get("modes", []),
            "input_schema": t.get("input_schema", {}),
            "output_schema": t.get("output_schema", {}),
            "denial_codes": t.get("denial_codes", []),
            "audit_events": t.get("audit_events", []),
            "witness_requirements": t.get("witness_requirements", []),
            "hold_conditions": t.get("hold_conditions", []),
            "allowed_actors": t.get("allowed_actors"),
            "bootstrap": t.get("bootstrap", False),
            "requires_plan": t.get("requires_plan", False),
            "requires_verdict_token": t.get("requires_verdict_token", False),
            "requires_epoch_id": t.get("requires_epoch_id", False),
            "requires_receipt_parent_ids": t.get("requires_receipt_parent_ids", False),
            "contract_version": t.get("contract_version", "1.0.0"),
            "fingerprint": _tool_fingerprint(t),
            "section": section,
            "legacy_aliases": [
                la["alias"]
                for la in doc.get("legacy_aliases", [])
                if la["canonical"] == t["canonical_name"]
            ],
        }
        nodes.append(node)
    return {
        "contract_family": doc["meta_schema"]["contract_family"],
        "contract_version": doc["meta_schema"]["version"],
        "generated_at": doc["meta_schema"]["generated_at"],
        "graph_version": f"v{doc['meta_schema']['version']}",
        "node_count": len(nodes),
        "nodes": nodes,
        "taxonomies": doc["taxonomies"],
        "denial_codes": doc["denial_codes"],
        "audit_events": doc["audit_events"],
        "axes": doc["axes"],
        "alias_map": norm["alias_map"],
        "deprecated": norm["deprecated"],
    }


# ════════════════════════════════════════════════════════════════════════════════
# Pass 6: generate_audit_schemas
# ════════════════════════════════════════════════════════════════════════════════


def generate_audit_schemas(doc: dict) -> dict:
    print("  [6/8] generate_audit_schemas")
    base = {
        "type": "object",
        "required": ["event", "ts", "actor_id", "session_id", "epoch_id", "plan_id", "task_id"],
        "properties": {
            "event": {"type": "string"},
            "ts": {"type": "string", "format": "date-time"},
            "actor_id": {"type": "string"},
            "session_id": {"type": "string"},
            "epoch_id": {"type": "string"},
            "plan_id": {"type": "string"},
            "task_id": {"type": "string"},
            "tool_name": {"type": "string"},
            "verdict": {"type": "string", "enum": doc["taxonomies"]["verdicts"]},
            "denial_code": {"type": "string"},
            "receipts": {"type": "array", "items": {"type": "object"}},
        },
    }
    schemas: dict[str, Any] = {"base": base, "events": {}}
    for ev in doc["audit_events"]:
        name = ev["event"]
        schemas["events"][name] = {
            **base,
            "properties": {**base["properties"], "event": {"const": name}},
        }
    print(f"        ✓ {len(schemas['events'])} event schemas generated")
    return schemas


# ════════════════════════════════════════════════════════════════════════════════
# Pass 7: generate_conformance_fixtures (5 classes per sovereign)
# ════════════════════════════════════════════════════════════════════════════════


def generate_conformance_fixtures(doc: dict) -> dict:
    print("  [7/8] generate_conformance_fixtures")
    happy: list[dict] = []
    schema_pass_constitution_fail: list[dict] = []
    schema_pass_channel_fail: list[dict] = []
    schema_pass_witness_fail: list[dict] = []
    legacy_alias_pass: list[dict] = []

    for t in _all_tools(doc):
        cn = t["canonical_name"]
        props = t.get("input_schema", {}).get("properties", {})
        required = t.get("input_schema", {}).get("required", [])

        def _example_input():
            return {
                k: (
                    "example"
                    if props.get(k, {}).get("type") == "string"
                    else 1
                    if props.get(k, {}).get("type") == "integer"
                    else {}
                )
                for k in required
            }

        # 1. Happy path
        happy.append(
            {
                "tool": cn,
                "fixture_class": "happy",
                "input": _example_input(),
                "expected_verdict": "SEAL",
                "actor_id": "arifbfazil",
            }
        )

        # 2. Schema-pass, constitution-fail: valid input shape, missing required field
        dc_list = t.get("denial_codes") or ["UNKNOWN_CAPABILITY"]
        schema_pass_constitution_fail.append(
            {
                "tool": cn,
                "fixture_class": "schema_pass_constitution_fail",
                "input": {},  # missing required fields
                "expected_verdict": "HOLD",
                "expected_denial_code": dc_list[0],
                "actor_id": "arifbfazil",
            }
        )

        # 3. Schema-pass, channel-fail: beta mutation by non-sovereign
        if t.get("contract_class") in ("gateway", "seal") and t.get("channel") == "stable":
            schema_pass_channel_fail.append(
                {
                    "tool": cn,
                    "fixture_class": "schema_pass_channel_fail",
                    "input": _example_input(),
                    "expected_verdict": "HOLD",
                    "expected_denial_code": "CHANNEL_VIOLATION",
                    "actor_id": "public_actor",  # not sovereign
                    "scenario": "non-sovereign actor on sovereign-only mutation",
                }
            )

        # 4. Schema-pass, witness-fail: action requires human+ai+earth but none attached
        if set(t.get("witness_requirements", [])) == {"human", "ai", "earth"}:
            schema_pass_witness_fail.append(
                {
                    "tool": cn,
                    "fixture_class": "schema_pass_witness_fail",
                    "input": _example_input(),
                    "expected_verdict": "HOLD",
                    "expected_denial_code": "WITNESS_DEFICIT",
                    "actor_id": "arifbfazil",
                    "attached_witnesses": ["human"],  # only 1 of 3
                }
            )

    # 5. Legacy-alias pass: old name resolves to canonical with deprecation metadata
    for la in doc.get("legacy_aliases", []):
        legacy_alias_pass.append(
            {
                "tool": la["canonical"],
                "fixture_class": "legacy_alias_pass",
                "input": {"alias_used": la["alias"]},
                "expected_resolved_to": la["canonical"],
                "deprecation_metadata": {
                    "deprecated_after": la.get("deprecated_after"),
                    "shim_layer": la.get("shim_layer", False),
                },
                "expected_verdict": "SEAL",
                "actor_id": "arifbfazil",
            }
        )

    print(
        f"        ✓ happy={len(happy)}, schema_pass_constitution_fail={len(schema_pass_constitution_fail)}, "
        f"schema_pass_channel_fail={len(schema_pass_channel_fail)}, "
        f"schema_pass_witness_fail={len(schema_pass_witness_fail)}, "
        f"legacy_alias_pass={len(legacy_alias_pass)}"
    )
    return {
        "happy": happy,
        "schema_pass_constitution_fail": schema_pass_constitution_fail,
        "schema_pass_channel_fail": schema_pass_channel_fail,
        "schema_pass_witness_fail": schema_pass_witness_fail,
        "legacy_alias_pass": legacy_alias_pass,
    }


# ════════════════════════════════════════════════════════════════════════════════
# Pass 8: emit_runtime_validators
# ════════════════════════════════════════════════════════════════════════════════


def emit_runtime_validators(doc: dict) -> str:
    print("  [8/8] emit_runtime_validators")
    out: list[str] = [
        '"""',
        "GENERATED by contracts/compiler.py — DO NOT EDIT BY HAND",
        f"Generated: {doc['meta_schema']['generated_at']}",
        f"Contract: {doc['meta_schema']['contract_family']} v{doc['meta_schema']['version']}",
        "",
        "Pydantic input/output validators per canonical tool + envelope.",
        "",
        "Sealing tools (contract_class=seal) require verdict_token + epoch_id + receipt_parent_ids.",
        "Gateway tools (contract_class=gateway) require plan_id.",
        '"""',
        "from __future__ import annotations",
        "from typing import Any, Optional, List",
        "try:",
        "    from pydantic import BaseModel, Field",
        "except ImportError:",
        "    BaseModel = object",
        "    Field = lambda *a, **k: None",
        "",
        "",
        "# ══ Kernel Envelope ══",
        "class KernelEnvelope(BaseModel):",
        "    epoch_id: str",
        "    plan_id: str",
        "    task_id: str",
        "    actor_id: str",
        '    witness_type: str = "ai"',
        "    verdict_token: Optional[str] = None",
        "    receipt_parent_ids: List[str] = []",
        "",
        "",
    ]
    for t in _all_tools(doc):
        cn = t["canonical_name"]
        out.append(
            f"# ── {cn} (contract_class={t.get('contract_class', 'ordinary')}, "
            f"mutation_class={t.get('mutation_class', 'read')}) ──"
        )
        out.append(f"class {cn}_Input(BaseModel):")
        out.append("    envelope: KernelEnvelope = None  # required for mutations")
        props = t.get("input_schema", {}).get("properties", {})
        required = t.get("input_schema", {}).get("required", [])
        for k, v in props.items():
            tname = v.get("type", "Any") if isinstance(v, dict) else "Any"
            default = "..." if k in required else "None"
            out.append(f"    {k}: {tname} = {default}")
        if t.get("contract_class") == "seal":
            out.append("    verdict_token: str  # REQUIRED for SEAL class")
            out.append("    epoch_id: str       # REQUIRED for SEAL class")
            out.append("    receipt_parent_ids: List[str] = []  # REQUIRED for SEAL class")
        if t.get("contract_class") == "gateway":
            out.append(
                "    plan_id: str  # REQUIRED for GATEWAY class (envelope.plan_id also acceptable)"
            )
        out.append("")
        out.append(f"class {cn}_Output(BaseModel):")
        out.append("    result: Any = None")
        out.append("    status: str = 'OK'")
        out.append("")
        out.append("")
    return "\n".join(out)


# ════════════════════════════════════════════════════════════════════════════════
# Pass 9: emit_contract_registry (runtime CONTRACT_REGISTRY + validate_tool_call)
# ════════════════════════════════════════════════════════════════════════════════


def emit_contract_registry(doc: dict) -> str:
    """Generate the runtime contract registry + validation function from SSOT.

    This replaces the hand-written contracts/validators.py with a SSOT-derived
    version. Same API: CONTRACT_REGISTRY, validate_tool_call(), ToolContract.
    DenialCode enum is imported from contracts.denial_codes (no duplication).
    """
    print("  [9/9] emit_contract_registry")
    tools = _all_tools(doc)
    tax = doc.get("taxonomies", {})

    out: list[str] = [
        '"""',
        "contracts/generated/validators_runtime.py — SSOT-Derived Runtime Validators",
        "═" * 72,
        "",
        "GENERATED by contracts/compiler.py — DO NOT EDIT BY HAND",
        f"Generated: {doc['meta_schema']['generated_at']}",
        f"Contract: {doc['meta_schema']['contract_family']} v{doc['meta_schema']['version']}",
        f"Tools: {len(tools)}",
        "",
        "This file replaces the hand-written contracts/validators.py.",
        "DenialCode enum is imported from contracts.denial_codes (single source).",
        "",
        "DITEMPA BUKAN DIBERI — Validated, not trusted.",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from dataclasses import dataclass, field",
        "from enum import StrEnum",
        "from typing import Any",
        "",
        "# DenialCode lives in contracts.denial_codes — no duplication here.",
        "from contracts.denial_codes import DenialCode",
        "",
        "",
        "# ═══════════════════════════════════════════════════════════════════════════════",
        "# CONTRACT ENUMS (non-DenialCode — these are tool contract primitives)",
        "# ═══════════════════════════════════════════════════════════════════════════════",
        "",
        "",
        "class Channel(StrEnum):",
    ]
    for ch in tax.get("channel", []):
        out.append(f'    {ch.upper()} = "{ch}"')
    out.append("")
    out.append("")
    out.append("class Reversibility(StrEnum):")
    for rv in tax.get("reversibility", []):
        out.append(f'    {rv.upper()} = "{rv}"')
    out.append("")
    out.append("")
    out.append("class BlastRadius(StrEnum):")
    for br in tax.get("blast_radius", []):
        out.append(f'    {br.upper()} = "{br}"')
    out.append("")
    out.append("")
    out.append("class Authority(StrEnum):")
    for au in tax.get("authority_required", []):
        out.append(f'    {au.upper()} = "{au}"')
    out.append("")
    out.append("")
    out.append("# ═══════════════════════════════════════════════════════════════════════════════")
    out.append("# TOOL CONTRACT VALIDATOR")
    out.append("# ═══════════════════════════════════════════════════════════════════════════════")
    out.append("")
    out.append("")
    out.append("@dataclass(frozen=True)")
    out.append("class ToolContract:")
    out.append('    """Machine-readable contract for a single canonical tool."""')
    out.append("    canonical_name: str")
    out.append("    role: str")
    out.append("    axis: str")
    out.append("    pipeline_stage: str")
    out.append("    contract_class: str")
    out.append("    mutation_class: str")
    out.append("    modes: tuple[str, ...]")
    out.append("    reversibility: Reversibility")
    out.append("    blast_radius: BlastRadius")
    out.append("    authority_required: Authority")
    out.append("    channel: Channel")
    out.append("    hold_conditions: tuple[str, ...]")
    out.append("    denial_codes: tuple[str, ...]")
    out.append("    audit_events: tuple[str, ...]")
    out.append("    witness_requirements: tuple[str, ...]")
    out.append("    contract_version: str")
    out.append("    requires_plan: bool = False")
    out.append("    irreversible: bool = False")
    out.append("")
    out.append("    def allows_mode(self, mode: str) -> bool:")
    out.append('        """Check if this tool allows the given mode."""')
    out.append("        return mode in self.modes")
    out.append("")
    out.append("    def requires_verdict_token(self) -> bool:")
    out.append('        """Whether this tool requires a judge verdict token."""')
    out.append(
        "        return self.contract_class in ('seal', 'verdict') or self.blast_radius == BlastRadius.CIVILIZATIONAL"
    )
    out.append("")
    out.append("    def check_authority(self, actor_authority: Authority) -> bool:")
    out.append('        """Check if actor authority meets tool requirement."""')
    out.append(
        "        order = {Authority.PUBLIC: 0, Authority.OPERATOR: 1, Authority.SOVEREIGN: 2}"
    )
    out.append(
        "        return order.get(actor_authority, -1) >= order.get(self.authority_required, 999)"
    )
    out.append("")
    out.append("")
    out.append("")

    # Generate CONTRACT_REGISTRY
    out.append("# ═══════════════════════════════════════════════════════════════════════════════")
    out.append(f"# CONTRACT REGISTRY — all {len(tools)} SSOT tools (generated)")
    out.append("# ═══════════════════════════════════════════════════════════════════════════════")
    out.append("")
    out.append("")
    out.append("CONTRACT_REGISTRY: dict[str, ToolContract] = {")

    for t in tools:
        cn = t["canonical_name"]
        role = t.get("role", "")
        axis = t.get("axis", "")
        stage = t.get("pipeline_stage", "")
        cc = t.get("contract_class", "ordinary")
        mc = t.get("mutation_class", "read")
        modes = tuple(t.get("modes", []))
        rev = t.get("reversibility", "reversible")
        blast = t.get("blast_radius", "low")
        auth = t.get("authority_required", "public")
        ch = t.get("channel", "stable")
        hc = tuple(t.get("hold_conditions", []))
        dc = tuple(t.get("denial_codes", []))
        ae = tuple(t.get("audit_events", []))
        wr = tuple(t.get("witness_requirements", []))
        cv = t.get("contract_version", "1.0.0")
        rp = t.get("requires_plan", False)
        irr = rev == "irreversible"

        out.append(f'    "{cn}": ToolContract(')
        out.append(f'        canonical_name="{cn}",')
        out.append(f'        role="{role}",')
        out.append(f'        axis="{axis}",')
        out.append(f'        pipeline_stage="{stage}",')
        out.append(f'        contract_class="{cc}",')
        out.append(f'        mutation_class="{mc}",')
        out.append(f"        modes={modes!r},")
        out.append(f"        reversibility=Reversibility.{rev.upper()},")
        out.append(f"        blast_radius=BlastRadius.{blast.upper()},")
        out.append(f"        authority_required=Authority.{auth.upper()},")
        out.append(f"        channel=Channel.{ch.upper()},")
        out.append(f"        hold_conditions={hc!r},")
        out.append(f"        denial_codes={dc!r},")
        out.append(f"        audit_events={ae!r},")
        out.append(f"        witness_requirements={wr!r},")
        out.append(f'        contract_version="{cv}",')
        out.append(f"        requires_plan={rp!r},")
        out.append(f"        irreversible={irr!r},")
        out.append("    ),")

    out.append("}")
    out.append("")
    out.append("")

    # Generate validation functions
    out.append("# ═══════════════════════════════════════════════════════════════════════════════")
    out.append("# VALIDATION FUNCTIONS")
    out.append("# ═══════════════════════════════════════════════════════════════════════════════")
    out.append("")
    out.append("")
    out.append("@dataclass")
    out.append("class ValidationResult:")
    out.append('    """Result of a contract validation check."""')
    out.append("    valid: bool")
    out.append("    tool_name: str")
    out.append("    denial_code: DenialCode | None = None")
    out.append('    reason: str = ""')
    out.append("    hold_conditions_met: list[str] = field(default_factory=list)")
    out.append("")
    out.append("")
    out.append("def validate_tool_call(")
    out.append("    tool_name: str,")
    out.append("    mode: str,")
    out.append('    actor_authority: str = "public",')
    out.append("    has_plan: bool = False,")
    out.append("    plan_approved: bool = False,")
    out.append("    has_verdict_token: bool = False,")
    out.append("    has_envelope: bool = False,")
    out.append(") -> ValidationResult:")
    out.append('    """')
    out.append("    Validate a tool call against its contract.")
    out.append("    Returns ValidationResult with denial code if blocked.")
    out.append('    """')
    out.append("    contract = CONTRACT_REGISTRY.get(tool_name)")
    out.append("    if contract is None:")
    out.append("        return ValidationResult(")
    out.append("            valid=False,")
    out.append("            tool_name=tool_name,")
    out.append("            denial_code=DenialCode.CONTRACT_DRIFT,")
    out.append("            reason=f\"Tool '{tool_name}' not in contract registry\",")
    out.append("        )")
    out.append("")
    out.append("    # Check mode")
    out.append("    if not contract.allows_mode(mode):")
    out.append("        return ValidationResult(")
    out.append("            valid=False,")
    out.append("            tool_name=tool_name,")
    out.append("            denial_code=DenialCode.SCHEMA_VALIDATION_FAILED,")
    out.append("            reason=f\"Mode '{mode}' not in allowed modes: {contract.modes}\",")
    out.append("        )")
    out.append("")
    out.append("    # Check envelope")
    out.append("    if not has_envelope:")
    out.append("        return ValidationResult(")
    out.append("            valid=False,")
    out.append("            tool_name=tool_name,")
    out.append("            denial_code=DenialCode.ENVELOPE_MISSING,")
    out.append('            reason="Tool call lacks required kernel envelope",')
    out.append("        )")
    out.append("")
    out.append("    # Check authority")
    out.append(
        "    auth = Authority(actor_authority) if actor_authority in Authority.__members__.values() else Authority.PUBLIC"
    )
    out.append("    if not contract.check_authority(auth):")
    out.append("        return ValidationResult(")
    out.append("            valid=False,")
    out.append("            tool_name=tool_name,")
    out.append("            denial_code=DenialCode.AUTHORITY_INSUFFICIENT,")
    out.append(
        "            reason=f\"Authority '{actor_authority}' insufficient, requires '{contract.authority_required.value}'\","
    )
    out.append("        )")
    out.append("")
    out.append("    # Check plan requirement")
    out.append("    if contract.requires_plan and not has_plan:")
    out.append("        return ValidationResult(")
    out.append("            valid=False,")
    out.append("            tool_name=tool_name,")
    out.append("            denial_code=DenialCode.PLAN_MISSING,")
    out.append("            reason=f\"Channel '{contract.channel.value}' requires approved plan\",")
    out.append("        )")
    out.append("")
    out.append("    if contract.requires_plan and has_plan and not plan_approved:")
    out.append("        return ValidationResult(")
    out.append("            valid=False,")
    out.append("            tool_name=tool_name,")
    out.append("            denial_code=DenialCode.PLAN_NOT_APPROVED,")
    out.append('            reason="Plan exists but is not in APPROVED state",')
    out.append("        )")
    out.append("")
    out.append("    # Check verdict token for high-risk")
    out.append("    if contract.requires_verdict_token() and not has_verdict_token:")
    out.append("        return ValidationResult(")
    out.append("            valid=False,")
    out.append("            tool_name=tool_name,")
    out.append("            denial_code=DenialCode.VERDICT_TOKEN_MISSING,")
    out.append('            reason="High-risk tool requires judge verdict token",')
    out.append("        )")
    out.append("")
    out.append("    return ValidationResult(valid=True, tool_name=tool_name)")
    out.append("")
    out.append("")
    out.append("def get_contract(tool_name: str) -> ToolContract | None:")
    out.append('    """Get the contract for a tool, or None if not found."""')
    out.append("    return CONTRACT_REGISTRY.get(tool_name)")
    out.append("")
    out.append("")
    out.append("def list_contracts() -> dict[str, ToolContract]:")
    out.append('    """Return all registered contracts."""')
    out.append("    return dict(CONTRACT_REGISTRY)")
    out.append("")
    out.append("")
    out.append("def find_orphan_tools(registered_tools: list[str]) -> list[str]:")
    out.append('    """Find tools registered at runtime but missing from contracts."""')
    out.append("    return [t for t in registered_tools if t not in CONTRACT_REGISTRY]")
    out.append("")
    out.append("")
    out.append("def find_contract_drift(registered_tools: list[str]) -> dict[str, str]:")
    out.append('    """Find tools in contracts but missing from runtime."""')
    out.append("    return {")
    out.append('        name: "contract_exists_but_runtime_missing"')
    out.append("        for name in CONTRACT_REGISTRY")
    out.append("        if name not in registered_tools")
    out.append("    }")

    code = "\n".join(out)
    print(f"        ✓ {len(tools)} tools in CONTRACT_REGISTRY, DenialCode from denial_codes.py")
    return code


# ════════════════════════════════════════════════════════════════════════════════
# Main: drive 9 passes
# ════════════════════════════════════════════════════════════════════════════════


def compile_all() -> dict:
    print("=" * 70)
    print("arifOS Constitutional Contract Compiler v0.1.0 (9 passes)")
    print("=" * 70)

    print(f"\n[SSOT]: {SSOT_PATH}")
    doc = load_yaml(SSOT_PATH)
    validate_meta_schema(doc)
    norm = normalize_names_and_aliases(doc)
    tax = expand_taxonomies(doc)

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)

    print("\n[Emit]")
    gpath = GENERATED_DIR / "capability_graph.json"
    graph = generate_capability_graph(doc, norm, tax)
    gpath.write_text(json.dumps(graph, indent=2, sort_keys=False))
    print(f"        ✓ {gpath.name} ({gpath.stat().st_size} bytes, {graph['node_count']} nodes)")

    apath = GENERATED_DIR / "audit_schemas.json"
    aschemas = generate_audit_schemas(doc)
    apath.write_text(json.dumps(aschemas, indent=2, sort_keys=False))
    print(f"        ✓ {apath.name} ({apath.stat().st_size} bytes)")

    cpath = GENERATED_DIR / "conformance_fixtures.json"
    cfix = generate_conformance_fixtures(doc)
    cpath.write_text(json.dumps(cfix, indent=2, sort_keys=False))
    print(f"        ✓ {cpath.name} ({cpath.stat().st_size} bytes)")

    vpath = GENERATED_DIR / "tool_validators.py"
    vcode = emit_runtime_validators(doc)
    vpath.write_text(vcode)
    print(f"        ✓ {vpath.name} ({vpath.stat().st_size} bytes)")

    rpath = GENERATED_DIR / "validators_runtime.py"
    rcode = emit_contract_registry(doc)
    rpath.write_text(rcode)
    print(f"        ✓ {rpath.name} ({rpath.stat().st_size} bytes)")

    print("\n" + "=" * 70)
    print("COMPILATION COMPLETE — 9 passes")
    print("=" * 70)
    tools = _all_tools(doc)
    print(
        f"  Tools: {len(tools)} (canonical={len(doc.get('canonical_tools', []))}, "
        f"diagnostic={len(doc.get('diagnostic', []))}, "
        f"federated={len(doc.get('federated_organs', []))}, "
        f"sanctioned={len(doc.get('sanctioned_non_arif', []))})"
    )
    print(
        f"  Channels: stable={sum(1 for t in tools if t.get('channel') == 'stable')}, "
        f"beta={sum(1 for t in tools if t.get('channel') == 'beta')}, "
        f"sandbox={sum(1 for t in tools if t.get('channel') == 'sandbox')}"
    )
    print(
        f"  Contract classes: {sum(1 for t in tools if t.get('contract_class') == 'seal')} seal, "
        f"{sum(1 for t in tools if t.get('contract_class') == 'gateway')} gateway, "
        f"{sum(1 for t in tools if t.get('contract_class') == 'verdict')} verdict, "
        f"{sum(1 for t in tools if t.get('contract_class') == 'diagnostic')} diagnostic, "
        f"{sum(1 for t in tools if t.get('contract_class') == 'ordinary')} ordinary"
    )
    print(f"  Legacy aliases: {len(norm['alias_map'])}")
    print(f"  Denial codes: {len(doc.get('denial_codes', []))}")
    print(f"\nArtifacts in {GENERATED_DIR}/")
    print("\nDITEMPA BUKAN DIBERI — Compiled, not hand-waved.")

    return {
        "tool_count": len(tools),
        "graph_path": str(gpath),
        "validators_path": str(vpath),
        "runtime_validators_path": str(rpath),
        "audit_schemas_path": str(apath),
        "conformance_fixtures_path": str(cpath),
    }


if __name__ == "__main__":
    compile_all()
