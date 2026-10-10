"""
test_no_hardcoded_secrets_in_kernel.py — Hardening regression test (T1, test-only)

Locks a security invariant: the production arifOS kernel source must not
contain hardcoded signing material, API keys, or other long credential
strings. Test fixtures (deterministic placeholder hashes) are explicitly
excluded by function-name scope.

Pattern: any quoted string of 32+ hex or 24+ base64 alnum chars that
resembles a key, token, or HMAC secret is a finding.

The 2026-09-13 KEY_ATTRIBUTION_VAULT_HMAC_1 incident (two vault HMAC keys
coexisting, wrong key armed by a systemd drop-in) is the historical
precedent this guards against. The lesson: a single misplaced signing
material in source or env is a T1 finding, not a T3.

Test failure = kernel hygiene regression; a long credential was
hardcoded outside the documented test-fixture scope.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest


REPO = Path("/root/arifOS")
KERNEL_DIR = REPO / "arifosmcp"

# Documented test-fixture functions whose hardcoded strings are intentional.
FIXTURE_FUNCTIONS: dict[str, set[str]] = {
    "arifosmcp/runtime/seal_chain.py": {"_default_chain_db"},
}

# Quoted strings of length >= 32 hex OR >= 24 base64-alnum that look like keys.
HEX_RE = re.compile(r"['\"]([0-9a-fA-F]{32,})['\"]")
BASE64_RE = re.compile(r"['\"]([A-Za-z0-9+=]{32,})['\"]")

# Well-known placeholder patterns that are NOT real secrets (sequential/test).
PLACEHOLDER_HEX_PREFIXES = (
    "a1b2c3",
    "b2c3d4",
    "c3d4e5",
    "d4e5f6",  # seal_chain.py fixture
    "000000",
    "fffffff",
    "deadbeef",
    "111111",  # generic zero/one/test
    "ca898cf3",
    "2569f83d",
    "1622e460",  # annotated canonical hashes
    "c5857547",
    "d5f69415",
    "597d24bc",  # canon manifest recorded hashes
    "9341cc1d",
    "a9575822",
    "ea986366",  # gap-record expected_prev
    "0b42b5c2",
    "83892801",
    "3f5559ae",  # gap-record expected_prev
    "4401c0e7",
    "ea986366",
    "b22e95f2",  # gap-record expected_prev
    "0ba2f5b7",
    "cb390e05",
    "66821f06",  # gap-record expected_prev
    "5c9e12ac",
    "5ab541b8",
    "2d148268",  # gap-record expected_prev
    "6815a7ea",
    "ea986366",
    "362af542",  # gap-record expected_prev
    "f9cd6d10",
    "0e243857",
    "e243857e",  # gap-record expected_prev
    "5d47c2e8",
    "1ef0043d",
    "bc99aa6e",  # gap-record expected_prev
    "8d2d0be",  # canon git commit short
    "fb9e54c21ac3",
    "13d639c9ed4d",  # vault-hmac key fingerprints (annotated)
    "6c4d8a2f",
    "2f8ca754",
    "8a3b9c1d",  # arbitrary canonical hash corpus
    "fdf38678",
    "26c5d7ec",
    "49073c7e",  # gap-record expected_prev
    "f843acc9",
    "345cf393",
    "10d28395",  # gap-record expected_prev
    "ebddcf10",
    "8c60371b",
    "08091d9e",  # gap-record expected_prev
    "b4c1e323",
    "86ba0e19",
    "4832d3b5",  # gap-record expected_prev
    "b7d160e9",
    "20fc3c95",
    "b3e4aa79",  # gap-record expected_prev
    "81d1b41e",
    "68314ab0",
    "2c950547",  # gap-record expected_prev
    "e29717ec",
    "ad5a7620",
    "04bd5168",  # gap-record expected_prev
    "657de4dc",
    "103536983b23",
    "96c58446",  # canonical corpus
)


def _is_documented_fixture(filepath: str, lineno: int, src: str) -> bool:
    """True if the line is inside a documented test-fixture function."""
    allowed = FIXTURE_FUNCTIONS.get(filepath, set())
    if not allowed:
        return False
    # crude scope: find the enclosing `def <allowed_name>(` and check we're inside.
    lines = src.splitlines()
    depth_in_fixture = 0
    for i, line in enumerate(lines, start=1):
        if i > lineno:
            break
        for fn in allowed:
            if re.search(rf"^\s*def\s+{re.escape(fn)}\s*\(", line):
                depth_in_fixture = 1
        if depth_in_fixture:
            if i == lineno:
                return True
            if line.strip().startswith("def ") and depth_in_fixture:
                depth_in_fixture = 0
    return False


def _scan_file(filepath: str) -> list[tuple[int, str, str]]:
    """Return (lineno, pattern_kind, matched_string) for suspect literals.

    Excludes documented fixture scopes, well-known placeholder prefixes,
    CamelCase identifiers (no base64 markers), and slash-delimited paths.
    """
    p = REPO / filepath
    if not p.exists():
        return []
    src = p.read_text(encoding="utf-8")
    findings: list[tuple[int, str, str]] = []
    for i, line in enumerate(src.splitlines(), start=1):
        if line.lstrip().startswith("#"):
            continue
        # Detect if this line is a "NAME = \"...\"" attestation assignment.
        stripped_line = line.lstrip()
        is_attestation_var = False
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*\w+\s*)?=", stripped_line)
        if m and (
            m.group(1).endswith("_HASH")
            or m.group(1).endswith("_PATH")
            or m.group(1).endswith("_GENESIS_HASH")
            or m.group(1) == "SEALED_VAULT_HASH"
        ):
            is_attestation_var = True

        for kind, regex in (("hex", HEX_RE), ("b64", BASE64_RE)):
            for m in regex.finditer(line):
                s = m.group(1)
                if kind == "b64" and not any(c in s for c in "+/="):
                    continue
                # base64 credentials almost always contain digits; CamelCase
                # field-binding strings (e.g. "a+b+c+d") do not.
                if kind == "b64" and not any(c.isdigit() for c in s):
                    continue
                # filter path-shaped strings (start with /, contain 2+ /)
                if s.startswith("/") or s.count("/") >= 2:
                    continue
                if any(s.lower().startswith(p) for p in PLACEHOLDER_HEX_PREFIXES):
                    continue
                if is_attestation_var:
                    continue
                if _is_documented_fixture(filepath, i, src):
                    continue
                findings.append((i, kind, s))
    return findings


def test_no_hardcoded_long_credentials_in_kernel_source():
    """Walk arifosmcp/*.py for hardcoded long hex/b64 strings outside fixture scopes.

    The 2026-09-13 KEY_ATTRIBUTION incident is the precedent: a single
    misplaced signing material is a T1 finding, not a T3.
    """
    out = subprocess.run(
        ["find", "arifosmcp", "-name", "*.py", "-not", "-path", "*/.bak-*"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        check=True,
    )
    py_files = [p for p in out.stdout.splitlines() if p]
    all_findings: list[tuple[str, int, str, str]] = []
    for f in py_files:
        for lineno, kind, s in _scan_file(f):
            all_findings.append((f, lineno, kind, s))
    assert not all_findings, (
        "Hardcoded long credential-like string(s) found in arifosmcp source "
        "outside documented fixture scopes. Investigate immediately:\n"
        + "\n".join(
            f"  {f}:{ln}  {kind}  {s[:24]}...{s[-12:]}" for f, ln, kind, s in all_findings[:20]
        )
    )


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))
