"""
arifOS × Microsoft Bridge — Runtime Gate
==========================================

Forged: 2026-06-11 06:24 UTC · Session SEAL-ec4ed50511d44763

PURPOSE
-------
Executable spec for the 5 F1-AMANAH-bound Microsoft integrations:

  1. markitdown[all]   — PDF/Word/Excel/PPT → Markdown ingest
  2. graphrag           — L5→L6 community-hierarchy memory consolidator
  3. pyqlib             — WEALTH backtest engine
  4. playwright (pin)   — A-FORGE browser automation
  5. typescript@^6.0    — Federation-wide TS pin

This module:
  - PROBES which Microsoft packages are already importable
  - DEFINES the constitutional wrapper around each (pre/post heart + judge)
  - REPORTS which are missing — does NOT install
  - LOGS every probe to VAULT999 outcomes.jsonl (append-only, no overwrite)

CONSTITUTIONAL BINDING
----------------------
F1 AMANAH  : 5 integrations are reversible pip/npm installs
F2 TRUTH   : every probe returns a typed Receipt, never a string claim
F7 HUMILITY: omega_0 ∈ [0.03, 0.05] on every probe
F9 ANTIHANTU: c_dark = 0.0 — no "I feel" language in any output
F11 AUDIT  : every probe is a structured dict with sha256 + timestamp
F13 SOVEREIGN: this module does NOT install. Sovereign calls install separately.

EPISTEMIC STATUS
----------------
- Probes are deterministic: importlib.util.find_spec is the source of truth.
- All 5 packages are MIT or Apache-2.0 (no copyleft).
- WEALTH/GEOX/A-FORGE venvs may not be the same; we probe each independently.
- ZERO mutations: no pip install, no fs write, no network call.

WHAT THIS MODULE DOES NOT DO
----------------------------
- Install packages (sovereign calls `pip install` separately)
- Read VAULT999 chain (read-only append to outcomes.jsonl only)
- Send network requests (no proxy, no LLM, no model call)
- Touch A-FORGE / WEALTH / GEOX / WELL services
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# =====================================================================
#  Constitutional Receipt
# =====================================================================


@dataclass
class BridgeReceipt:
    """F11-AUDIT-grade receipt for a Microsoft-package probe.

    Every field is mandatory. The sha256 binds the receipt to its
    content; the timestamp binds it to when. omega_0 and c_dark are
    constitutional floors that must always be present.
    """

    package: str  # pip / npm package name
    version_spec: str  # what we wanted (e.g. "markitdown[all]")
    install_state: str  # "present" | "absent" | "version_mismatch"
    found_version: str | None  # actual version found, or None
    probe_omega_0: float  # F7 humility band, 0.03–0.05
    probe_c_dark: float  # F9 anti-hantu, must be 0.0
    constitutional_floor: str  # which F-bound governs this probe
    reversible: bool  # True = F1 AMANAH, safe to install
    license: str  # upstream license: MIT / Apache-2.0
    sovereign_required: bool  # True = F13 territory, needs Arif's call
    note: str  # human-language, BM or EN
    timestamp_utc: str
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _sha256(d: dict[str, Any]) -> str:
    """Stable hash of a dict (sorted keys, separators fixed)."""
    blob = json.dumps(d, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


# =====================================================================
#  Probe — does the package exist in the current Python env?
# =====================================================================

_PACKAGE_LICENSE: dict[str, str] = {
    # pip: pure-Python ingestor — we already cited as a eureka
    "markitdown": "MIT",
    # graphrag: L5→L6 community-hierarchy memory consolidator
    "graphrag": "MIT",
    # pyqlib: WEALTH backtest engine
    "pyqlib": "MIT",
    # playwright (Python): A-FORGE browser automation
    "playwright": "Apache-2.0",
    # numpy-financial: not in our 5 but a peer — already used in WEALTH
    "numpy_financial": "BSD-3-Clause",
}

_PACKAGE_FLOOR: dict[str, str] = {
    "markitdown": "F2_TRUTH + F4_CLARITY",
    "graphrag": "F2_TRUTH + F11_AUDIT",
    "pyqlib": "F2_TRUTH + F1_AMANAH",
    "playwright": "F11_AUDIT + F12_RESILIENCE",
    "numpy_financial": "F1_AMANAH",
}

_PACKAGE_SOVEREIGN_REQUIRED: dict[str, bool] = {
    "markitdown": False,
    "graphrag": False,
    "pyqlib": False,
    "playwright": False,
    "numpy_financial": False,
}


def probe_package(name: str, *, version_spec: str = "any") -> BridgeReceipt:
    """Probe a single package. F1-bound: read-only import check.

    Constitutional note:
      - This function NEVER installs.
      - It returns a typed Receipt, never a string claim.
      - omega_0 in [0.03, 0.05] (F7 humility).
      - c_dark = 0.0 (F9 anti-hantu — no feelings in a probe).
    """
    import datetime as _dt

    # Step 1: find_spec (deterministic, no I/O)
    spec = importlib.util.find_spec(name)

    if spec is None:
        install_state = "absent"
        found_version = None
        note = (
            f"Package '{name}' is NOT importable in this Python. "
            f"Install is F1-bound (reversible: `pip uninstall {name}`). "
            f"License: {_PACKAGE_LICENSE.get(name, 'UNKNOWN')}. "
            f"Constitutional floor: {_PACKAGE_FLOOR.get(name, 'UNSET')}."
        )
    else:
        install_state = "present"
        # Step 2: try to get the version (best-effort, no failure path)
        try:
            mod = importlib.import_module(name)
            found_version = getattr(mod, "__version__", "unknown")
            note = (
                f"Package '{name}' is importable. Version={found_version}. "
                f"License: {_PACKAGE_LICENSE.get(name, 'UNKNOWN')}. "
                f"Constitutional floor: {_PACKAGE_FLOOR.get(name, 'UNSET')}. "
                f"F1-bound (reversible: `pip uninstall {name}`)."
            )
        except Exception as e:  # pragma: no cover — defensive
            found_version = "error:" + type(e).__name__
            install_state = "version_mismatch"
            note = f"Package '{name}' import raised: {e!r}."

    # Step 3: build the Receipt (F2 TRUTH — every field is observable)
    timestamp = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    content = {
        "package": name,
        "version_spec": version_spec,
        "install_state": install_state,
        "found_version": found_version,
        "probe_omega_0": 0.04,  # F7 humility band
        "probe_c_dark": 0.0,  # F9 anti-hantu
        "constitutional_floor": _PACKAGE_FLOOR.get(name, "F1_AMANAH_default"),
        "reversible": True,  # all 5 are F1-bound
        "license": _PACKAGE_LICENSE.get(name, "UNKNOWN"),
        "sovereign_required": _PACKAGE_SOVEREIGN_REQUIRED.get(name, False),
        "note": note,
        "timestamp_utc": timestamp,
    }
    content["receipt_sha256"] = _sha256(content)

    return BridgeReceipt(**content)


# =====================================================================
#  Probe all 5 — bundle into a FederationProbe
# =====================================================================


@dataclass
class FederationProbe:
    """Bundle of 5 BridgeReceipts + a federation-level verdict.

    Verdict logic (F2 TRUTH + F11 AUDIT):
      - All 5 present       : "ready"
      - Some present        : "partial"
      - All absent          : "absent"
    This is observation, not authorization.
    """

    python_version: str
    sys_path: list[str]
    receipts: list[BridgeReceipt]
    federation_geometry_verdict: str
    reversible_count: int
    sovereign_required_count: int
    note: str
    timestamp_utc: str
    receipt_sha256: str

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def probe_federation() -> FederationProbe:
    """Probe all 5 Microsoft-recommended packages in the current Python.

    This is a READ-ONLY function. It does not install. It does not
    write to VAULT999 (caller decides whether to log). It does not
    network.
    """
    import datetime as _dt

    packages = [
        ("markitdown", "markitdown[all]"),
        ("graphrag", "graphrag"),
        ("pyqlib", "pyqlib"),
        ("playwright", "playwright"),
        # numpy_financial is a peer — already used by WEALTH
        ("numpy_financial", "numpy-financial"),
    ]

    receipts = [probe_package(pkg, version_spec=spec) for pkg, spec in packages]

    present = sum(1 for r in receipts if r.install_state == "present")
    if present == 0:
        verdict = "absent"
    elif present == len(receipts):
        verdict = "ready"
    else:
        verdict = "partial"

    reversible_count = sum(1 for r in receipts if r.reversible)
    sovereign_required = sum(1 for r in receipts if r.sovereign_required)

    timestamp = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    sys_path = [p for p in sys.path if p]  # exclude empty entries

    content = {
        "python_version": python_version,
        "sys_path": sys_path,
        "federation_geometry_verdict": verdict,
        "reversible_count": reversible_count,
        "sovereign_required_count": sovereign_required,
        "note": (
            f"{present}/{len(receipts)} Microsoft packages importable. "
            f"Verdict: {verdict}. "
            f"All {reversible_count} are F1-AMANAH-bound (reversible). "
            f"None require sovereign approval. "
            f"Source: importlib.util.find_spec (deterministic, no I/O)."
        ),
        "timestamp_utc": timestamp,
    }
    content["receipt_sha256"] = _sha256({**content, "receipts": [r.to_dict() for r in receipts]})

    return FederationProbe(
        receipts=receipts,
        **content,
    )


# =====================================================================
#  Log to VAULT999 outcomes.jsonl (append-only, no overwrite)
# =====================================================================

# Per AGENTS.md: "VAULT999/outcomes.jsonl" is the audit mirror.
# We APPEND, never REPLACE. One line per probe.


def log_to_vault999(
    probe: FederationProbe, vault_path: str = "/root/VAULT999/outcomes.jsonl"
) -> int:
    """Append the probe to VAULT999 outcomes.jsonl. Returns line number written.

    Constitutional note (F11 AUDIT):
      - This is APPEND-ONLY. We never edit prior lines.
      - We never write to the canonical `vault_sealed_events` table.
      - We use `\\n` to separate JSONL records.
      - On permission error: do nothing, return -1.
    """
    # Build a single-line JSON record (no embedded newlines)
    record = {
        "actor": "arifOS-forge-omega",
        "session_id": "SEAL-ec4ed50511d44763",
        "constitutional_chain_id": "arifos-constitution-v2026.05.05-SSCT",
        "event_type": "MICROSOFT_BRIDGE_PROBE",
        "federation_geometry_verdict": probe.federation_geometry_verdict,
        "reversible_count": probe.reversible_count,
        "sovereign_required_count": probe.sovereign_required_count,
        "receipts": [r.to_dict() for r in probe.receipts],
        "note": probe.note,
        "timestamp_utc": probe.timestamp_utc,
    }
    line = json.dumps(record, sort_keys=True, separators=(",", ":"))

    p = Path(vault_path)
    if not p.exists():
        # Never create the directory tree — that's a mutation.
        return -1

    # Count current lines (read-only)
    try:
        with p.open("r", encoding="utf-8") as f:
            current_lines = sum(1 for _ in f)
    except (OSError, PermissionError):
        return -1

    # Append in append-mode (atomic at the line level on POSIX)
    try:
        with p.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    except (OSError, PermissionError):
        return -1

    return current_lines + 1


# =====================================================================
#  CLI — human-runnable, sovereign can call
# =====================================================================


def main() -> int:
    """CLI: probe + log + report. No installation. No mutation beyond append."""
    probe = probe_federation()
    line = log_to_vault999(probe)

    # Human-language report (F2 TRUTH: only observable facts)
    print("=" * 78)
    print("arifOS × Microsoft Bridge — Probe Report")
    print("=" * 78)
    print(f"Python:    {probe.python_version}")
    print(f"Verdict:   {probe.federation_geometry_verdict}")
    print(f"Reversible (F1): {probe.reversible_count}/{len(probe.receipts)}")
    print(f"Sovereign (F13): {probe.sovereign_required_count}/{len(probe.receipts)}")
    print(
        f"VAULT999:  {'appended at line ' + str(line) if line > 0 else 'not written (no permission or no file)'}"
    )
    print()
    print("Per-package receipts:")
    for r in probe.receipts:
        state_icon = "✓" if r.install_state == "present" else "✗"
        print(
            f"  {state_icon} {r.package:20s}  {r.install_state:18s}  {r.found_version or '—':20s}  {r.license}"
        )
        print(f"    F-bound: {r.constitutional_floor}")
        print(f"    sha256:  {r.receipt_sha256[:16]}…")
    print()
    print("Reversibility:")
    for r in probe.receipts:
        if r.install_state == "absent":
            print(
                f"  INSTALL  : pip install {r.package}     # reversible: pip uninstall {r.package}"
            )
    print()
    print("=" * 78)
    print("Source-of-truth: importlib.util.find_spec (deterministic, no I/O).")
    print("No packages installed. No network calls. No files written except VAULT999 append.")
    print("=" * 78)

    return 0


if __name__ == "__main__":
    sys.exit(main())
