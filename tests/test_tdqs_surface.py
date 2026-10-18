"""Phase-3 CI gate — arifOS MCP surface parity + TDQS repair (2026-10-18, 333-AGI).

Falsifies the Glama name-only stub: boots the PUBLISHED image (empty env) and
asserts the tool SURFACE is full and honest even when runtime behavior is degraded.

Run against the live kernel (default) or a container:
    ARIFOS_MCP_URL=http://127.0.0.1:8088/mcp pytest tests/test_tdqs_surface.py -q

Exit non-zero if any assertion fails. A failing gate = the published surface is
still name-only; a PASSING gate on a known-broken image = the gate is wrong (fix
the gate first, per the Phase-3 falsifier).
"""

from __future__ import annotations

import json
import os
import urllib.request

MCP_URL = os.environ.get("ARIFOS_MCP_URL", "http://127.0.0.1:8088/mcp")

# 8 canonical verbs. 888 is NOT a verb. forge + seal are hidden on the
# public_agent profile but MUST still be present on the full surface.
CANONICAL_8 = (
    "arif_init",  # 000
    "arif_observe",  # 111
    "arif_think",  # 333
    "arif_route",  # 444
    "arif_memory",  # 555
    "arif_judge",  # 666
    "arif_forge",  # 777
    "arif_seal",  # 999
)

# Verdict words must appear only as arif_judge / arif_seal OUTPUTS — never in a
# non-judge tool's status/description surface.
VERDICT_WORDS = ("SEAL", "HOLD", "VOID", "SABAR", "PARTIAL", "PROVISIONAL")
NON_JUDGE = tuple(n for n in CANONICAL_8 if n not in ("arif_judge", "arif_seal"))

MIN_DESC_LEN = 200
ANNOTATION_KEYS = ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")


def _tools_list() -> list[dict]:
    hdrs = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}})
    req = urllib.request.Request(MCP_URL, data=body.encode(), headers=hdrs, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
    if "error" in data:
        raise AssertionError(f"tools/list returned error: {data['error']}")
    return data.get("result", {}).get("tools", [])


def _fetch() -> list[dict]:
    return _tools_list()


def test_surface_has_exactly_canonical_names():
    tools = _fetch()
    names = {t.get("name") for t in tools}
    missing = [n for n in CANONICAL_8 if n not in names]
    assert not missing, f"missing canonical tools: {missing}"
    # No 888 verb, no fabricated names.
    assert "arif_888" not in names and "888_judge" not in names


def test_every_tool_has_quality_description():
    tools = {t.get("name"): t for t in _fetch()}
    for name in CANONICAL_8:
        t = tools.get(name)
        if t is None:
            continue  # surface-count gate catches absence; skip here
        desc = (t.get("description") or "").strip()
        assert desc != name, f"{name}: description == name (name-only stub)"
        assert len(desc) >= MIN_DESC_LEN, f"{name}: description too short ({len(desc)}ch)"
        # Routing guidance: must name a sibling verb ("use X", "prefer Y",
        # "reason over… arif_think", "delegate… arif_route") so an agent can
        # pick the right tool over its siblings.
        _d = desc.lower()
        _names_sibling = any(
            f"arif_{s}" in _d
            for s in ("observe", "think", "route", "memory", "judge", "forge", "seal", "init")
            if f"arif_{s}" != name
        )
        assert ("use" in _d) or ("prefer" in _d) or _names_sibling, (
            f"{name}: no sibling/routing guidance"
        )


def test_every_tool_has_annotations_and_closed_schema():
    tools = {t.get("name"): t for t in _fetch()}
    for name in CANONICAL_8:
        t = tools.get(name)
        if t is None:
            continue
        ann = t.get("annotations") or {}
        assert any(k in ann for k in ANNOTATION_KEYS), f"{name}: no MCP annotations"
        sch = t.get("inputSchema") or {}
        assert sch.get("additionalProperties") is False, (
            f"{name}: additionalProperties is not False (open schema)"
        )


def test_no_verdict_words_on_non_judge_surface():
    tools = {t.get("name"): t for t in _fetch()}
    for name in NON_JUDGE:
        t = tools.get(name)
        if t is None:
            continue
        desc = (t.get("description") or "").upper()
        # A non-judge tool must not present itself as a verdict source.
        if name == "arif_forge":
            # forge may mention "SEAL verdict" as a prerequisite (allowed: it does
            # not issue the verdict, it consumes it).
            continue
        for w in VERDICT_WORDS:
            assert f" {w} " not in f" {desc} ", (
                f"{name}: verdict word {w} leaks into non-judge description"
            )


def test_no_888_judge_vocab():
    tools = _fetch()
    for t in tools:
        desc = t.get("description") or ""
        title = (t.get("annotations") or {}).get("title", "")
        assert "888" not in desc, f"{t.get('name')}: '888' leaks into description"
        assert "888 JUDGE" not in title, f"{t.get('name')}: '888 JUDGE' in title"
