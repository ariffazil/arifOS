#!/usr/bin/env python3
"""Generate the MCP-registry manifest from the repo manifest at publish time.

FI-003 2026-11-28. Why: `ship-release.sh` publishes
`$REG_DIR/server.json` (/root/forge_work/arifos-mcp-registry), a hand-kept copy
outside version control. On 2026-11-13 that copy carried two version dialects
(top-level "2026.11.13.post1", packages[0] "1!2026.11.13.post1") and declared
`transport: stdio` for a streamable-http server, so the registry recorded two
releases 2m43s apart and mislabelled the transport.

The authoritative manifest is `$REPO/server.json` (in git, reviewed). This
script copies it forward and pins the version to the package version being
shipped, so the unversioned copy stops being an authority.

Usage:
  gen_registry_manifest.py --repo-manifest REPO/server.json --version 1!2026.11.18 \
      --out REG/server.json [--backup REG/server.json.prev] [--dry-run]

Exit codes: 0 written (or dry-run OK), 2 bad input, 3 name check failed.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys

REGISTRY_NAME_PREFIX = "io.github.ariffazil/"


def die(code: int, msg: str) -> None:
    print(f"gen_registry_manifest: {msg}", file=sys.stderr)
    sys.exit(code)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-manifest", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--backup", default=None)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    try:
        with open(a.repo_manifest) as f:
            doc = json.load(f)
    except FileNotFoundError:
        die(2, f"repo manifest not found: {a.repo_manifest}")
    except json.JSONDecodeError as e:
        die(2, f"repo manifest is not valid JSON: {e}")

    name = str(doc.get("name") or "")
    if not name.startswith(REGISTRY_NAME_PREFIX):
        die(3, f"name '{name}' does not start with {REGISTRY_NAME_PREFIX}")

    old_top = doc.get("version")
    doc["version"] = a.version

    pkgs = doc.get("packages") or []
    if not pkgs:
        die(2, "repo manifest has no packages[] — a registry entry needs one")
    old_pkg = pkgs[0].get("version")
    pkgs[0]["version"] = a.version

    # Transport must describe the served surface. The 2026-11-13 copy declared
    # stdio while the server answers streamable-http; remotes[] is the served
    # truth, so align the package transport to it when both are present.
    remotes = doc.get("remotes") or []
    pkg_transport = pkgs[0].get("transport")
    transport_fixed = False
    if remotes and isinstance(pkg_transport, dict):
        r0 = remotes[0] if isinstance(remotes[0], dict) else {}
        if r0.get("type") and pkg_transport.get("type") != r0.get("type"):
            pkg_transport["type"] = r0["type"]
            transport_fixed = True
            if r0.get("url"):
                pkg_transport["url"] = r0["url"]
            for stale in ("runtimeHint", "registryBaseUrl"):
                pkg_transport.pop(stale, None)

    body = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    print(
        f"  registry manifest: version {old_top} -> {a.version} "
        f"| packages[0] {old_pkg} -> {a.version}"
        + (" | transport aligned to remotes" if transport_fixed else "")
    )

    if a.dry_run:
        print("  [dry-run] not written")
        return 0

    if a.backup:
        if os.path.exists(a.out):
            shutil.copy2(a.out, a.backup)
            print(f"  backup: {a.backup}")
        else:
            print(f"  backup: skipped (no existing {a.out})")

    tmp = f"{a.out}.tmp.{os.getpid()}"
    with open(tmp, "w") as f:
        f.write(body)
    os.replace(tmp, a.out)
    print(f"  written: {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
