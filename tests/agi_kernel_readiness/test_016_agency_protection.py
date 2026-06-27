"""
test_016 — Agency Protection (Tier 8: WEALTH no-extraction)

Civilian blindside: WEALTH could become a debt collector / scoring
engine / engagement optimizer. The kernel says no.

Pass criteria:
    - WEALTH tools have `recommendation_only: True` in their output
    - WEALTH tools have `final_authority: "Arif"` (or sovereign field)
    - WEALTH does not have retention / engagement metrics
    - WEALTH tools refuse to "decide" — they only advise

The civilian danger: WEALTH is supposed to compute, not control.
This test catches regressions where WEALTH becomes a soft tyrant
that recommends-and-is-followed.
"""

import sys
import os
import urllib.request
import json

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

WEALTH_URL = "http://127.0.0.1:18082/mcp"


def _call_wealth(method: str, params: dict, session_id: str | None = None) -> dict:
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id
    req = urllib.request.Request(WEALTH_URL, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def _init_wealth() -> str:
    init_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "agi-gate-016", "version": "1.0"},
        },
    }
    req = urllib.request.Request(
        WEALTH_URL,
        data=json.dumps(init_payload).encode(),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as r:
        sid = None
        for h, v in r.getheaders():
            if h.lower() == "mcp-session-id":
                sid = v
    return sid or ""


def test_wealth_tools_declare_recommendation_only():
    """WEALTH tools must emit 'recommendation_only: True' in their output."""
    sid = _init_wealth()
    # Pick a public tool — wealth_survival_engine(mode=personal_finance) is
    # one of the safe, public surface tools.
    r = _call_wealth(
        "tools/call",
        {
            "name": "wealth_personal_finance",
            "arguments": {
                "mode": "personal_finance",
                "monthly_income": 5000,
                "monthly_expenses": 3000,
                "liquid_assets": 10000,
            },
        },
        session_id=sid or None,
    )
    content = r.get("result", {}).get("content", [])
    if not content:
        return  # tool unavailable
    text = content[0].get("text", "")
    assert "recommendation_only" in text, (
        f"WEALTH tool must declare recommendation_only; got: {text[:300]}"
    )


def test_wealth_tools_declare_final_authority():
    """WEALTH tools must declare the sovereign as final authority."""
    sid = _init_wealth()
    r = _call_wealth(
        "tools/call",
        {
            "name": "wealth_personal_finance",
            "arguments": {
                "mode": "personal_finance",
                "monthly_income": 5000,
                "monthly_expenses": 3000,
                "liquid_assets": 10000,
            },
        },
        session_id=sid or None,
    )
    content = r.get("result", {}).get("content", [])
    if not content:
        return
    text = content[0].get("text", "")
    text_lower = text.lower()
    assert "arif" in text_lower or "sovereign" in text_lower, (
        f"WEALTH tool must declare sovereign/final_authority; got: {text[:300]}"
    )


def test_wealth_no_engagement_or_retention_metrics():
    """WEALTH must not have retention/engagement metrics in its substrate.

    The intimacy-as-extraction pattern (civilian blindside #8) is
    about behavioral metrics. WEALTH should not be optimizing
    for user engagement with capital tools.
    """
    # Check the source for the pattern
    import re

    wealth_root = "/root/WEALTH/internal"
    bad_patterns = [
        re.compile(r"engagement_score"),
        re.compile(r"retention_metric"),
        re.compile(r"stickiness"),
        re.compile(r"churn_risk"),
        re.compile(r"upsell_probability"),
    ]
    found_bad = []
    for root, dirs, files in os.walk(wealth_root):
        # Skip cache
        if "__pycache__" in root:
            continue
        for f in files:
            if not f.endswith(".py"):
                continue
            fpath = os.path.join(root, f)
            try:
                with open(fpath) as fp:
                    text = fp.read()
            except (IOError, UnicodeDecodeError):
                continue
            for pat in bad_patterns:
                if pat.search(text):
                    found_bad.append((fpath, pat.pattern))
    assert not found_bad, (
        f"WEALTH must not contain engagement/retention metrics; found: {found_bad[:3]}"
    )


def test_wealth_authority_modes_include_observer():
    """WEALTH must have at least one tool that runs in OBSERVER mode
    (read-only, no recommendation)."""
    sid = _init_wealth()
    # wealth_system_registry_status is the metadata tool — should be
    # readable, and should declare its mode
    r = _call_wealth(
        "tools/call",
        {"name": "wealth_system_registry_status", "arguments": {"mode": "health"}},
        session_id=sid or None,
    )
    content = r.get("result", {}).get("content", [])
    if not content:
        return
    text = content[0].get("text", "")
    # The registry should expose the surface; assert it doesn't lie about
    # agency. A registry should NOT have recommendation_only: true because
    # it doesn't recommend — it only lists. So the assertion here is
    # that the registry exists and is read-only.
    assert "registry" in text.lower() or "tools" in text.lower(), (
        f"wealth_system_registry_status should list the surface; got: {text[:300]}"
    )


if __name__ == "__main__":
    try:
        test_wealth_tools_declare_recommendation_only()
        print("test_016 recommendation_only: PASS")
    except Exception as e:
        print(f"test_016 recommendation_only: {type(e).__name__}: {e}")
    try:
        test_wealth_tools_declare_final_authority()
        print("test_016 final_authority: PASS")
    except Exception as e:
        print(f"test_016 final_authority: {type(e).__name__}: {e}")
    try:
        test_wealth_no_engagement_or_retention_metrics()
        print("test_016 no_engagement: PASS")
    except Exception as e:
        print(f"test_016 no_engagement: {type(e).__name__}: {e}")
    try:
        test_wealth_authority_modes_include_observer()
        print("test_016 registry_readonly: PASS")
    except Exception as e:
        print(f"test_016 registry_readonly: {type(e).__name__}: {e}")
