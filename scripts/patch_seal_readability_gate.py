"""Apply the seal-readability gate to floor_producers.py (F13 888_HOLD repair, 2026-10-24).

WHY (measured, not assumed):
  888's ruling named "{} becomes PASS" in floor_producers.py. Probe of HEAD,
  the working tree AND the deployed venv copy shows {} -> UNMEASURED already,
  for every producer. The named defect does not reproduce.

  The REAL leak is one level deeper, and it is the same failure class the
  ruling's requirement #4 forbids ("malformed or insufficient producer
  evidence must resolve to UNMEASURED"):

      sources = {"seals": [{}]}            -> F5 PASS, F13 PASS
      sources = {"seals": [{"payload": {}}]} -> F5 PASS, F13 PASS

  A seal list whose every entry is uninterpretable falls through the
  `for ... continue` loop and lands on the PASS return. Present-but-junk
  evidence is not evidence. F5 and F13 are exactly the two floors that gate
  SEAL, so this is the highest-consequence instance of the class.

FIX: count interpretable seal records. Zero readable records -> UNMEASURED
with a named origin. Real seal chains are unaffected: any record carrying
verdict/actor/payload/ratification is readable, and the existing PASS/FAIL
logic runs unchanged on those.

This patcher is idempotent and applies the SAME two hunks to any copy of the
file (working tree, or a HEAD blob staged for an isolated commit).
"""

from __future__ import annotations

import sys
from pathlib import Path

GATE = '''    # ── SEAL-READABILITY GATE (F13 888_HOLD repair, 2026-10-24) ──────────
    # 888_HOLD named "{} -> PASS". Measured: {} and None already return
    # UNMEASURED. The live leak is present-but-JUNK evidence:
    #   {"seals": [{}]}  and  {"seals": [{"payload": {}}]}
    # fell through the `continue` loop to PASS on F5 and F13 — the two floors
    # that gate SEAL. Requirement #4 of the ruling forbids exactly that:
    # "malformed or insufficient producer evidence must resolve to
    # UNMEASURED". Present-but-unreadable records are not evidence; nothing
    # was observed, so nothing may pass.
    if not any(_readable_seal(s) for s in seals):
        return {
            "floor": "%(fid)s",
            "status": "UNMEASURED",
            "origin": "unmeasured_default:seal_records_unreadable",
        }
'''

HELPER_ANCHOR = '''SOVEREIGN_ACTORS = frozenset({"arif", "ARIF", "Arif"})'''

HELPER = '''SOVEREIGN_ACTORS = frozenset({"arif", "ARIF", "Arif"})

# Fields that make a seal record interpretable. A record carrying none of
# these cannot be judged: it is a shape without evidence, not a passing seal.
_SEAL_RECORD_KEYS = (
    "verdict",
    "actor",
    "payload",
    "reversibility",
    "human_ratifier",
    "human_signature",
)


def _readable_seal(record: Any) -> bool:
    """True only if this record carries enough to be judged at all.

    Empty dicts, non-dicts, and dicts of unrelated keys are unreadable.
    Cheap on purpose: this gate decides whether evidence EXISTS, not whether
    it is good — the floor's own logic decides that afterwards.
    """
    if not isinstance(record, dict):
        return False
    return any(record.get(k) not in (None, "", {}, []) for k in _SEAL_RECORD_KEYS)
'''


def patch(text: str, fid: str) -> str:
    """Insert the readability gate before the PASS return of one floor."""
    if "SEAL-READABILITY GATE" in text and f'"_readable_seal"' in text:
        # already applied for this floor?
        if f'"floor": "{fid}",\n            "status": "UNMEASURED",\n            "origin": "unmeasured_default:seal_records_unreadable",' in text:
            return text

    # 1. helper (once)
    if "_readable_seal" not in text:
        if HELPER_ANCHOR not in text:
            raise SystemExit("anchor SOVEREIGN_ACTORS not found")
        text = text.replace(HELPER_ANCHOR, HELPER, 1)

    # 2. gate: place immediately BEFORE the seal loop.
    #    It must run before iteration: a junk record (None, "x", 123) would
    #    otherwise raise AttributeError inside the loop instead of resolving
    #    to UNMEASURED. The gate answers "is there anything readable here?".
    fn_marker = f"def _f{int(fid[1:])}_{'sovereign' if fid == 'F13' else 'peace'}(sources: dict[str, Any]) -> dict[str, Any]:"
    fn_idx = text.find(fn_marker)
    if fn_idx < 0:
        raise SystemExit(f"function for {fid} not found")
    anchor = "    for s in seals:"
    idx = text.find(anchor, fn_idx)          # FIRST loop AFTER this function starts
    if idx < 0:
        raise SystemExit(f"seal loop for {fid} not found")
    if "SEAL-READABILITY GATE" in text[fn_idx:idx]:
        return text                            # already gated for this floor
    gate = GATE % {"fid": fid}
    text = text[:idx] + gate + text[idx:]
    return text


def main() -> None:
    path = Path(sys.argv[1])
    fid = sys.argv[2] if len(sys.argv) > 2 else None
    src = path.read_text(encoding="utf-8")
    fids = [fid] if fid else ["F13", "F5"]
    for f in fids:
        src = patch(src, f)
    path.write_text(src, encoding="utf-8")
    print(f"patched {path} floors={fids} readable_gate={'_readable_seal' in src}")


if __name__ == "__main__":
    main()
