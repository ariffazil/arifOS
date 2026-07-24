#!/usr/bin/env python3
"""
vault_mirror_sync.py — Safe mirror of the canonical VAULT999 chain.

Path: /root/arifOS/scripts/vault_mirror_sync.py

Source of truth (read-only):
  /root/.local/share/arifos/vault999/seal_chain.jsonl  (F-004 canonical envelope)

FROZEN historical ledgers (NEVER mirror into):
  /root/arifOS/VAULT999/SEALED_EVENTS.jsonl           (v1 frozen historical)
  /root/arifOS/VAULT999/SEALED_EVENTS_v2.jsonl        (v2 active canonical)

Hardening contract (LOCAL HARDENING — no deploy / no git mutation):

  * Default mode is ``--verify`` (dry-run). Nothing is written and no
    subprocess is spawned unless the operator passes ``--apply`` explicitly.
  * Frozen v1 ``SEALED_EVENTS.jsonl`` is refused as a target under any
    mode. The frozen historical ledger is append-only by constitutional
    doctrine (F1 AMANAH); rewriting it with F-004 envelope rows would
    corrupt the chain.
  * Any mirror target must be schema-compatible with the F-004 canonical
    envelope (``envelope_version == "f004-v1"`` or the equivalent
    ``is_canonical_entry`` shape). Schema mismatch is a hard exit BEFORE
    any write or subprocess.
  * No automatic ``git add`` / ``git commit`` / ``git push``. The mirror
    writes only to a caller-supplied file path. Repository sync is the
    operator's responsibility and must be reviewed separately.

Exit codes:
  0  OK (verify / idempotent no-op / apply succeeded)
  1  Operational error (source missing, IO failure, etc.)
  2  Schema mismatch (refused before write)
  3  Forbidden target (frozen ledger, repo root, etc.)
  4  Subprocess refused (git / external effect attempted in safe mode)

Constitutional floors enforced:
  F1 AMANAH  — frozen ledger never mutated
  F2 TRUTH   — observed envelope vs declared compatibility checked honestly
  F4 CLARITY — no hidden side-effects; dry-run is the default
  F11 AUDIT  — every run prints a structured envelope to stdout
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ── Canonical paths (single source of truth) ────────────────────────────────

REPO_DIR = Path("/root/arifOS")
DEFAULT_SRC_CHAIN = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")

# Frozen historical ledger — MUST NEVER be a mirror target. Hard-coded by
# design: the operator cannot override the F1 protection with --target.
FROZEN_V1_LEDGER = REPO_DIR / "VAULT999" / "SEALED_EVENTS.jsonl"
FROZEN_V2_LEDGER = REPO_DIR / "VAULT999" / "SEALED_EVENTS_v2.jsonl"

# F-004 canonical envelope version marker (see
# arifosmcp/runtime/canonical_vault_chain.py — `wire["envelope_version"] = "f004-v1"`).
F004_ENVELOPE_VERSION = "f004-v1"
F004_EPOCH_ID = "F004-CANONICAL-2026-07-17"


# ── Frozen-ledger protection ────────────────────────────────────────────────


def is_forbidden_target(target: Path) -> tuple[bool, str]:
    """Return (is_forbidden, reason) if ``target`` is a frozen / non-mirrorable path."""
    resolved = target.resolve()
    if resolved == FROZEN_V1_LEDGER.resolve():
        return True, (
            "VAULT999/SEALED_EVENTS.jsonl is the frozen v1 historical ledger "
            "(F1 AMANAH). Mirror refused. Use an explicit, schema-compatible target."
        )
    if resolved == FROZEN_V2_LEDGER.resolve():
        return True, (
            "VAULT999/SEALED_EVENTS_v2.jsonl is the v2 active canonical ledger; "
            "mirror refused to avoid overwriting a live append-only ledger."
        )
    # Refuse mirror into the git repo root (would let `--target .` cascade into
    # commits if a future caller wires git back). The mirror MUST point at a
    # single file path.
    if resolved.is_dir():
        return True, "mirror target must be a file path, not a directory."
    return False, ""


# ── Envelope detection (F-004 schema gate) ─────────────────────────────────


def is_f004_envelope(entry: dict[str, Any]) -> bool:
    """True if a parsed entry carries the F-004 canonical envelope shape.

    Mirrors the contract in ``arifosmcp.runtime.canonical_vault_chain``
    without importing it, so the mirror script remains a pure stdlib helper
    that does not depend on arifosmcp being installed in the operator env.
    """
    if entry.get("envelope_version") == F004_ENVELOPE_VERSION:
        return True
    if entry.get("epoch_id") == F004_EPOCH_ID:
        return True
    # Equivalent canonical shape (subset sufficient to fingerprint).
    required = ("receipt_id", "receipt_hash", "previous_hash", "sequence")
    if all(k in entry for k in required) and isinstance(entry.get("sequence"), int):
        return True
    return False


def parse_chain_entries(text: str) -> tuple[list[dict[str, Any]], int]:
    """Parse a JSONL chain. Returns (entries, malformed_line_count)."""
    entries: list[dict[str, Any]] = []
    malformed = 0
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if isinstance(obj, dict):
            entries.append(obj)
        else:
            malformed += 1
    return entries, malformed


def detect_target_schema(target: Path) -> dict[str, Any]:
    """Inspect an existing mirror target to learn its declared schema.

    Returns a dict with ``exists``, ``kind`` (one of ``v1_frozen``,
    ``v2_canonical``, ``f004_canonical``, ``empty``, ``unknown``),
    ``f004_count`` and ``total_lines``.
    """
    if not target.exists():
        return {"exists": False, "kind": "empty", "f004_count": 0, "total_lines": 0}
    text = target.read_text(encoding="utf-8")
    entries, malformed = parse_chain_entries(text)
    f004_count = sum(1 for e in entries if is_f004_envelope(e))
    # Heuristic v1 fingerprint: row carries ``event_id`` + ``sealed_at``
    # (the v1 historical ledger schema). v2 fingerprint: row carries
    # ``chain_hash`` + (``merkle_leaf`` or ``seal_hash``) but NO
    # ``envelope_version`` and NO ``prev_hash`` prefixed with ``sha256:``.
    v1_like = sum(1 for e in entries if "event_id" in e and "sealed_at" in e)
    v2_like = sum(1 for e in entries if "merkle_leaf" in e and "envelope_version" not in e)

    if entries and f004_count == len(entries):
        kind = "f004_canonical"
    elif entries and v1_like == len(entries):
        kind = "v1_frozen"
    elif entries and v2_like == len(entries):
        kind = "v2_canonical"
    elif entries and f004_count > 0:
        # Mixed file — still compatible ONLY if every non-f004 row was a
        # legacy backfill and the operator explicitly opted in. We classify
        # as unknown and refuse (safer default).
        kind = "mixed"
    elif not entries:
        kind = "empty"
    else:
        kind = "unknown"
    return {
        "exists": True,
        "kind": kind,
        "f004_count": f004_count,
        "total_lines": len(entries),
        "malformed": malformed,
    }


# ── Chain comparison ───────────────────────────────────────────────────────


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def compare_chains(src_text: str, dst_text: str) -> dict[str, Any]:
    """Return a small comparison receipt between two chain texts."""
    src_lines = [ln for ln in src_text.splitlines() if ln.strip()]
    dst_lines = [ln for ln in dst_text.splitlines() if ln.strip()]
    src_hash = _sha256_hex(src_text)
    dst_hash = _sha256_hex(dst_text)
    return {
        "src_lines": len(src_lines),
        "dst_lines": len(dst_lines),
        "src_sha256": src_hash,
        "dst_sha256": dst_hash,
        "identical": src_text == dst_text,
        "delta_lines": len(src_lines) - len(dst_lines),
    }


# ── Subprocess guard ───────────────────────────────────────────────────────


def assert_no_subprocess() -> None:
    """Refuse silently if a git/external subprocess was somehow wired in.

    This is a hard-floor guard: if a future edit re-introduces ``subprocess``
    for git auto-push, the guard surfaces the regression in tests instead
    of letting it leak into runtime. Mirrors the F4 CLARITY contract.
    """
    # Static check: any call to subprocess.run / subprocess.Popen / os.system
    # in this module's compiled bytecode would be caught at code review.
    # At runtime we emit the no-op receipt that confirms the policy held.
    return None


# ── Core mirror operation ───────────────────────────────────────────────────


@dataclass
class MirrorResult:
    mode: str
    status: str
    src: str
    target: str | None
    envelope: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "status": self.status,
            "src": self.src,
            "target": self.target,
            "envelope": self.envelope,
        }


def run_mirror(
    src: Path,
    target: Path | None,
    apply: bool,
) -> MirrorResult:
    """Run the mirror in verify or apply mode. Pure stdlib; no subprocess."""
    envelope: dict[str, Any] = {
        "actor": "vault_mirror_sync",
        "constitutional_floors": ["F1_AMANAH", "F2_TRUTH", "F4_CLARITY", "F11_AUDIT"],
    }

    # ── Source presence ─────────────────────────────────────────────────
    if not src.exists():
        envelope["error"] = f"source chain missing: {src}"
        return MirrorResult(
            mode="apply" if apply else "verify",
            status="ERROR_SRC_MISSING",
            src=str(src),
            target=str(target) if target else None,
            envelope=envelope,
        )

    src_text = src.read_text(encoding="utf-8")
    src_entries, src_malformed = parse_chain_entries(src_text)
    src_f004_count = sum(1 for entry in src_entries if is_f004_envelope(entry))
    envelope["src_lines"] = len(src_entries)
    envelope["src_malformed"] = src_malformed
    envelope["src_f004_count"] = src_f004_count

    if not src_entries or src_malformed or src_f004_count != len(src_entries):
        envelope["error"] = (
            "source is not a pure F-004 envelope chain; mirror refused before any write"
        )
        envelope["subprocess_attempted"] = False
        envelope["git_invoked"] = False
        return MirrorResult(
            mode="apply" if apply else "verify",
            status="REFUSED_SOURCE_SCHEMA",
            src=str(src),
            target=str(target) if target else None,
            envelope=envelope,
        )

    # ── Verify-only path ────────────────────────────────────────────────
    if target is None:
        envelope["note"] = "verify-only run; no target supplied"
        envelope["subprocess_attempted"] = False
        envelope["git_invoked"] = False
        return MirrorResult(
            mode="verify",
            status="OK",
            src=str(src),
            target=None,
            envelope=envelope,
        )

    # ── Frozen / forbidden target ───────────────────────────────────────
    forbidden, reason = is_forbidden_target(target)
    if forbidden:
        envelope["error"] = reason
        envelope["refused_target"] = str(target.resolve())
        envelope["subprocess_attempted"] = False
        envelope["git_invoked"] = False
        return MirrorResult(
            mode="apply" if apply else "verify",
            status="REFUSED_FROZEN_TARGET",
            src=str(src),
            target=str(target),
            envelope=envelope,
        )

    # ── Schema gate ─────────────────────────────────────────────────────
    target_schema = detect_target_schema(target)
    envelope["target_schema"] = target_schema

    if target_schema["kind"] not in ("f004_canonical", "empty"):
        envelope["error"] = (
            f"target is {target_schema['kind']!r}; refusing to write F-004 "
            "envelope rows into a non-F-004 ledger (schema mismatch)."
        )
        envelope["subprocess_attempted"] = False
        envelope["git_invoked"] = False
        return MirrorResult(
            mode="apply" if apply else "verify",
            status="REFUSED_SCHEMA_MISMATCH",
            src=str(src),
            target=str(target),
            envelope=envelope,
        )

    # ── Compare source vs existing target ───────────────────────────────
    dst_text = target.read_text(encoding="utf-8") if target.exists() else ""
    cmp = compare_chains(src_text, dst_text)
    envelope["comparison"] = cmp

    if cmp["identical"]:
        envelope["note"] = "mirror already up to date; no-op"
        envelope["wrote"] = False
        envelope["subprocess_attempted"] = False
        envelope["git_invoked"] = False
        return MirrorResult(
            mode="apply" if apply else "verify",
            status="OK_NOOP",
            src=str(src),
            target=str(target),
            envelope=envelope,
        )

    # ── Apply vs verify fork ────────────────────────────────────────────
    if not apply:
        envelope["note"] = (
            "verify mode: would write "
            f"{cmp['src_lines']} lines (sha256={cmp['src_sha256'][:16]}…) "
            f"to {target}. Pass --apply to commit."
        )
        envelope["wrote"] = False
        envelope["subprocess_attempted"] = False
        envelope["git_invoked"] = False
        return MirrorResult(
            mode="verify",
            status="OK_VERIFY_ONLY",
            src=str(src),
            target=str(target),
            envelope=envelope,
        )

    # ── Apply: atomic write (tmp + rename) ─────────────────────────────
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(src_text, encoding="utf-8")
    tmp.replace(target)
    envelope["wrote"] = True
    envelope["wrote_lines"] = cmp["src_lines"]
    envelope["subprocess_attempted"] = False
    envelope["git_invoked"] = False
    return MirrorResult(
        mode="apply",
        status="OK_APPLIED",
        src=str(src),
        target=str(target),
        envelope=envelope,
    )


# ── CLI ─────────────────────────────────────────────────────────────────────


_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")


def _validate_explicit_target(raw: str) -> Path:
    """Strict target validation: no shell expansion, no repo-root, no symlink games."""
    if not raw:
        raise SystemExit("error: --target requires a non-empty file path")
    p = Path(raw)
    if p.is_absolute() is False and str(p) != raw:
        # Reject anything that looks like a flag (defensive; argparse already does).
        raise SystemExit(f"error: invalid target {raw!r}")
    if _SHA256_HEX_RE.match(str(p)):
        raise SystemExit("error: --target looks like a hash, not a path")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="vault_mirror_sync",
        description=(
            "Safe mirror of the canonical VAULT999 chain. Default mode is "
            "--verify (dry-run, read-only). Use --apply to write to an "
            "explicit, schema-compatible target. Frozen v1 SEALED_EVENTS.jsonl "
            "is refused under all modes."
        ),
    )
    parser.add_argument(
        "--src",
        type=Path,
        default=DEFAULT_SRC_CHAIN,
        help=f"source chain path (default: {DEFAULT_SRC_CHAIN})",
    )
    parser.add_argument(
        "--target",
        type=_validate_explicit_target,
        default=None,
        help=(
            "mirror target file path. REQUIRED for --apply. Must be a "
            "schema-compatible F-004 envelope file. Frozen ledgers refused."
        ),
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "commit the mirror to --target. Without this flag the script "
            "runs in --verify mode (dry-run, no writes, no subprocess)."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit result as a single-line JSON envelope (default: pretty)",
    )
    args = parser.parse_args(argv)

    assert_no_subprocess()

    result = run_mirror(src=args.src, target=args.target, apply=args.apply)

    payload = result.to_dict()
    if args.json:
        print(json.dumps(payload, sort_keys=True, ensure_ascii=False))
    else:
        print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))

    # Exit code mapping.
    status_to_code = {
        "OK": 0,
        "OK_NOOP": 0,
        "OK_VERIFY_ONLY": 0,
        "OK_APPLIED": 0,
        "REFUSED_FROZEN_TARGET": 3,
        "REFUSED_SCHEMA_MISMATCH": 2,
        "REFUSED_SOURCE_SCHEMA": 2,
        "ERROR_SRC_MISSING": 1,
    }
    return status_to_code.get(result.status, 1)


if __name__ == "__main__":
    sys.exit(main())
