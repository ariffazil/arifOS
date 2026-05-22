"""tests/test_js_symbols.py — Verify JS/TS symbol extraction captures full names."""

from __future__ import annotations

import sys
from pathlib import Path
root_dir = Path(__file__).parents[1].resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))
if str(root_dir / "core") not in sys.path:
    sys.path.insert(0, str(root_dir / "core"))

from arifos_wiki_tools.symbols import extract_js_symbols

def test_js_symbol_full_name_capture():
    """Verify that full camelCase and PascalCase names are captured, not just first 2 chars."""
    code = """
    async function authenticateSovereignUser(user, key) {
        return true;
    }

    export default class AuthControlGateway {
        constructor() {}
    }

    const validateAccessRequest = (req) => {
        return true;
    };

    let sessionPulseMonitor = async function() {
        await sleep(1000);
    };

    export function authenticateUser(user, key) {
        return true;
    }

    export async function authorizeAdmin(user) {
        return true;
    }

    export const searchIndex = (q) => {
        return [];
    };
    """
    symbols = extract_js_symbols(code)
    
    names = [s["name"] for s in symbols]
    
    assert "authenticateSovereignUser" in names
    assert "AuthControlGateway" in names
    assert "validateAccessRequest" in names
    assert "sessionPulseMonitor" in names
    assert "authenticateUser" in names
    assert "authorizeAdmin" in names
    assert "searchIndex" in names
    
    # Ensure no truncation (bug fix verification)
    assert "au" not in names
    assert "Au" not in names
    assert "va" not in names
    assert "se" not in names

def test_js_symbol_kinds():
    """Verify correct kind assignment for classes and functions."""
    code = """
    class SovereignKernel {}
    function initSovereign() {}
    const runForge = () => {};
    """
    symbols = extract_js_symbols(code)
    
    symbol_map = {s["name"]: s["kind"] for s in symbols}
    
    assert symbol_map["SovereignKernel"] == "class"
    assert symbol_map["initSovereign"] == "function"
    assert symbol_map["runForge"] == "function"
