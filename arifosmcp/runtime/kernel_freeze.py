"""
arifosmcp/runtime/kernel_freeze.py — Kernel Enforcement-Freeze Attestation (G7)

Fasa 1 Kernel Immutable Floor, 2026-08-30.

Problem (G7): the kernel is mutable Python on disk. Nothing measured whether
the ENFORCEMENT code that a session started with is still the code that runs
when a mutation is authorized. "Deterministic Runtime Lock" needs a pinned
digest of the enforcement module set, checked at the pre-execution chokepoint.

Design:
  - ENFORCEMENT_MODULES — the constitutional circuit: gates, vault chain,
    ACT/session crypto, self-mod guard, router, floors.
  - compute_freeze_digest() — SHA-256 over (module name, file sha256) pairs
    of the RUNNING import locations. mtime+size memoized per file (rehash
    only on change) so per-call cost is ~zero after warm-up.
  - Pinning (deploy step):
      ARIFOS_KERNEL_FREEZE_PIN=<sha256>        (env, preferred)
      or /var/lib/arifos/kernel_freeze.pin     (state file, one hex line)
    rsync-deploy repins: a deploy is a NEW release, not drift.
  - Enforcement ladder (F1 — reversible until enforced):
      ARIFOS_KERNEL_FREEZE_ENFORCE=1 → digest mismatch BLOCKS every mutating
      action at Gate 8.5 (HOLD, violation KERNEL_FREEZE_DRIFT).
      unset (default) → mismatch is logged telemetry only (no behavior change).

CLI:
  python3 -m arifosmcp.runtime.kernel_freeze          # print digest
  python3 -m arifosmcp.runtime.kernel_freeze --pin    # write pin file (deploy)

DITEMPA BUKAN DIBERI — the freeze is forged, not promised.
"""

from __future__ import annotations

import hashlib
import importlib
import logging
import os
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("arifosmcp.kernel_freeze")

FREEZE_VERSION = 1

# The constitutional circuit. Add modules here when they join the enforcement
# floor; digest changes on next repin (deploy), never silently.
ENFORCEMENT_MODULES: tuple[str, ...] = (
    "arifosmcp.runtime.pre_execution_gate",
    "arifosmcp.runtime.canonical_vault_chain",
    "arifosmcp.runtime.self_mod_lock",
    "arifosmcp.runtime.act_token",
    "arifosmcp.runtime.session",
    "arifosmcp.runtime.kernel_router",
    "arifosmcp.runtime.law",
    "arifosmcp.runtime.kernel_freeze",
)

PIN_FILE = Path(
    os.environ.get("ARIFOS_KERNEL_FREEZE_PIN_FILE", "/var/lib/arifos/kernel_freeze.pin")
)

# (path, mtime_ns, size) → sha256 memo — rehash only when the file changes.
_hash_memo: dict[tuple[str, int, int], str] = {}


def _file_sha256(path: str) -> str | None:
    try:
        st = os.stat(path)
        key = (path, st.st_mtime_ns, st.st_size)
        cached = _hash_memo.get(key)
        if cached:
            return cached
        h = hashlib.sha256()
        with open(path, "rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        digest = h.hexdigest()
        # Bound the memo: keep only live keys for our module set.
        if len(_hash_memo) > 64:
            _hash_memo.clear()
        _hash_memo[key] = digest
        return digest
    except OSError:
        return None


def module_file(module_name: str) -> str | None:
    """Running source file for a module (None for namespace/missing)."""
    try:
        mod = sys.modules.get(module_name) or importlib.import_module(module_name)
        return getattr(mod, "__file__", None)
    except Exception:  # noqa: BLE001 — attestation must never crash the gate
        return None


def compute_freeze_digest() -> dict[str, Any]:
    """Digest over the enforcement module set at RUNNING import locations."""
    files: list[dict[str, str]] = []
    parts: list[str] = []
    for name in ENFORCEMENT_MODULES:
        path = module_file(name)
        digest = _file_sha256(path) if path else None
        short = name.rsplit(".", 1)[-1]
        files.append(
            {
                "module": short,
                "path": path or "",
                "sha256": digest or "UNAVAILABLE",
            }
        )
        parts.append(f"{short}:{digest or 'UNAVAILABLE'}")
    combined = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return {
        "freeze_version": FREEZE_VERSION,
        "digest": combined,
        "modules": files,
        "unavailable": sum(1 for f in files if f["sha256"] == "UNAVAILABLE"),
    }


def pinned_digest() -> str | None:
    """The pinned digest from env or pin file (bare hex, 64 chars)."""
    env_pin = (os.environ.get("ARIFOS_KERNEL_FREEZE_PIN") or "").strip().lower()
    if env_pin:
        return env_pin.removeprefix("sha256:") or None
    try:
        text = PIN_FILE.read_text(encoding="utf-8").strip().splitlines()
        for line in text:
            line = line.strip().lower()
            if line and not line.startswith("#"):
                return line.removeprefix("sha256:")
    except OSError:
        pass
    return None


def freeze_enforced() -> bool:
    return os.environ.get("ARIFOS_KERNEL_FREEZE_ENFORCE", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def check_freeze() -> dict[str, Any]:
    """Gate-8.5 verdict input: {ok, drift, enforced, digest, pinned}.

    ok=True when: no pin configured (telemetry mode) OR digest matches pin.
    ok=False when: pin configured AND digest differs → mutating actions must
    HOLD under enforcement (and are logged in warn mode).
    """
    pin = pinned_digest()
    current = compute_freeze_digest()
    drift = bool(pin) and pin != current["digest"]
    return {
        "ok": not drift,
        "drift": drift,
        "enforced": freeze_enforced(),
        "pin_configured": bool(pin),
        "digest": current["digest"],
        "pinned": pin,
        "unavailable_modules": current["unavailable"],
    }


def write_pin(path: Path | None = None) -> dict[str, Any]:
    """Deploy helper: persist the CURRENT digest as the pinned release."""
    target = path or PIN_FILE
    digest = compute_freeze_digest()["digest"]
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f"# arifOS kernel freeze pin — written at deploy; repin on every rsync release\n"
        f"{digest}\n",
        encoding="utf-8",
    )
    try:
        os.chmod(target, 0o644)  # world-readable: verification is public
    except OSError:
        pass
    return {"pin_file": str(target), "digest": digest}


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--pin" in argv:
        result = write_pin()
        print(f"pin written: {result['pin_file']}")
        print(result["digest"])
        return 0
    report = check_freeze()
    import json

    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
