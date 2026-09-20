#!/usr/bin/env python3
"""Independent observation process for the arifOS 60-second governance demo.

Spawned as a SEPARATE process by demo.py with one argument: a file path.
It reports only what it observes on the filesystem (existence, size, mtime,
sha256). It does not import the kernel, does not read the executor's log, and
shares no state with demo.py — the only channel is the file it is pointed at
plus its own stdout. That is what makes it usable as an outside witness
under the authority-envelope doctrine (Three Independences: epistemic,
authority, observational).

Usage:
    python3 witness.py <path>
Prints one JSON object on stdout. Exit code 0 always.
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import UTC, datetime


def observe(raw_path: str) -> dict:
    path = os.path.realpath(raw_path)
    observed_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    record: dict = {
        "observer": "witness.py",
        "observer_pid": os.getpid(),
        "observed_at": observed_at,
        "target": path,
        "exists": False,
        "bytes": 0,
        "sha256": None,
        "mtime_iso": None,
    }
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        st = os.stat(path)
        record.update(
            {
                "exists": True,
                "bytes": len(data),
                "sha256": "sha256:" + hashlib.sha256(data).hexdigest(),
                "mtime_iso": datetime.fromtimestamp(st.st_mtime, UTC)
                .isoformat()
                .replace("+00:00", "Z"),
            }
        )
    except FileNotFoundError:
        pass
    except OSError as exc:  # permission / IO trouble must be visible, not silent
        record["error"] = f"{type(exc).__name__}: {exc}"
    return record


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: witness.py <path>", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(observe(sys.argv[1]), sort_keys=True))
