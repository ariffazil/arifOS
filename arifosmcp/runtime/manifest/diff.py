"""
PR4 — manifest drift detector.

Compares a freshly-composed manifest against a published manifest and exits 1
if any audit-mandated drift rule fires.
"""

from __future__ import annotations

import json
import sys
from typing import Any


def manifest_drift(generated: dict[str, Any], published: dict[str, Any]) -> list[str]:
    """Return a list of human-readable drift findings. Empty = no drift."""
    findings: list[str] = []
    gen_totals = generated.get("totals", {})
    pub_totals = published.get("totals", {})

    # Drift rule 1: a tool documented but not registered
    for tool in generated.get("tools", []):
        if tool["runtime"]["declared"] and not tool["runtime"]["registered"]:
            findings.append(f"declared_but_not_registered: {tool['name']}")
    # Drift rule 2: a registered tool absent from the published manifest
    pub_tool_names = {t["name"] for t in published.get("tools", [])}
    for tool in generated.get("tools", []):
        if tool["runtime"]["registered"] and tool["name"] not in pub_tool_names:
            findings.append(f"registered_but_absent_from_manifest: {tool['name']}")
    # Drift rule 3: schema hashes differ
    for tool in generated.get("tools", []):
        for pub_tool in published.get("tools", []):
            if tool["name"] == pub_tool["name"]:
                if tool.get("schemas") != pub_tool.get("schemas"):
                    findings.append(f"schema_hash_drift: {tool['name']}")
    # Drift rule 4: an alias points to no handler
    # alias shape: "<legacy_alias> (<modern_target> → <handler>)" or "<legacy> → <new>"
    for alias in generated.get("manifest_drift", {}).get("deprecated_aliases", []):
        # Try to extract the rightmost '→' target, else the substring inside parens.
        target_name = None
        if "→" in alias:
            target_name = alias.rsplit("→", 1)[-1].strip().rstrip(")")
        elif "(" in alias and ")" in alias:
            inner = alias[alias.find("(") + 1 : alias.find(")")]
            # "arifos_init → arif_init" — take the last token
            parts = inner.split("→") if "→" in inner else inner.split()
            if parts:
                target_name = parts[-1].strip()
        if target_name and not any(t["name"] == target_name for t in generated.get("tools", [])):
            findings.append(f"deprecated_alias_points_to_nothing: {alias}")
    # Drift rule 5: runtime version differs
    gen_v = generated.get("schema_version")
    pub_v = published.get("schema_version")
    if gen_v and pub_v and gen_v != pub_v:
        findings.append(f"schema_version_drift: published={pub_v} generated={gen_v}")
    # Drift rule 6: totals shape
    if gen_totals.get("declared_tools") != pub_totals.get("declared_tools"):
        findings.append("totals.declared_tools_drift")
    if gen_totals.get("registered_tools") != pub_totals.get("registered_tools"):
        findings.append("totals.registered_tools_drift")
    if gen_totals.get("callable_tools") != pub_totals.get("callable_tools"):
        findings.append("totals.callable_tools_drift")
    return findings


def exit_with_drift(findings: list[str]) -> None:
    if findings:
        print(json.dumps({"manifest_drift": findings}, indent=2), file=sys.stderr)
        sys.exit(1)
    print(json.dumps({"manifest_drift": "NONE"}, indent=2))
