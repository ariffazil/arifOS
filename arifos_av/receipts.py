"""Receipt ledger: append-only, hash-chained.

Receipt != outcome. This ledger records what was claimed and checked —
it is the audit spine an incident investigation reads later.
"""

import hashlib
import json
import time


class ReceiptLedger:
    def __init__(self):
        self._entries = []
        self._prev = "GENESIS"

    def append(self, kind: str, payload: dict) -> dict:
        entry = {
            "seq": len(self._entries),
            "ts": time.time(),
            "kind": kind,
            "payload": payload,
            "prev": self._prev,
        }
        entry["hash"] = self._digest(entry)
        self._entries.append(entry)
        self._prev = entry["hash"]
        return entry

    def _digest(self, entry: dict) -> str:
        check = {k: v for k, v in entry.items() if k != "hash"}
        return hashlib.sha256(json.dumps(check, sort_keys=True).encode()).hexdigest()

    def verify_chain(self) -> bool:
        prev = "GENESIS"
        for e in self._entries:
            if e["prev"] != prev:
                return False
            if self._digest(e) != e["hash"]:
                return False
            prev = e["hash"]
        return True

    @property
    def entries(self):
        return tuple(self._entries)

    def dump(self) -> str:
        return "\n".join(json.dumps(e, sort_keys=True) for e in self._entries)
