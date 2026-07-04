"""
seal_token_guard.py — MCP-SYMBOLIC-HARDEN-v1 — Rule Zero (Kernel-Wide Invariant)
════════════════════════════════════════════════════════════════════════════════

Spec:  /root/arifOS/forge_work/MCP-SYMBOLIC-HARDEN-v1.md §1
Real path: /root/arifOS/arifosmcp/core/seal_token_guard.py
            (spec said /opt/arifos/app/mcp_servers/_core/seal_token_guard.py — that path does not exist)

F13 OVERRIDE TASK (2026-06-28 05:08 UTC): "Go and execute. Don't ask again."
F2 TRUTH OVERRIDE: spec paths /opt/arifos/app/mcp_servers/* do NOT exist; real paths
                    under /root/arifOS/arifosmcp/.

Doctrine:
  Never allow the word `seal` to pass without domain.

A bare "seal" / "SEAL" / "Seal" token is ambiguous between:
  - geological_seal        (trap / lithology seal — petrophysical)
  - constitutional_SEAL    (arifOS verdict — arif_judge → arif_seal)
  - vault_seal             (VAULT999 immutable record)
  - trap_seal_lithology    (petrophysical variant)
  - seal_disambiguation_required  (quarantine flag this guard emits)

If the token is not accompanied by a known domain qualifier within a
small surrounding window (either before OR after), this guard
QUARANTINES the input and refuses to proceed. Logging is non-optional.

This module is INTERNAL middleware. It does NOT expose a new externally-
visible MCP tool. It runs before any tool/receipt/vault parse.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable


# ═══════════════════════════════════════════════════════════════════════════════
# §1.1 Domain vocabulary (canonical, required)
# ═══════════════════════════════════════════════════════════════════════════════


class SealDomain(str, Enum):
    """Canonical seal domain qualifiers — the only ones allowed after a bare `seal` token."""

    GEOLOGICAL = "geological_seal"
    CONSTITUTIONAL = "constitutional_SEAL"
    VAULT = "vault_seal"
    TRAP_LITHOLOGY = "trap_seal_lithology"
    DISAMBIGUATION_REQUIRED = "seal_disambiguation_required"


DOMAIN_QUALIFIERS: tuple[str, ...] = (
    SealDomain.TRAP_LITHOLOGY.value,
    SealDomain.CONSTITUTIONAL.value,
    SealDomain.VAULT.value,
    SealDomain.GEOLOGICAL.value,
    SealDomain.DISAMBIGUATION_REQUIRED.value,
)

_ADJECTIVE_QUALIFIERS: tuple[str, ...] = (
    "geological",
    "constitutional",
    "vault",
    "trap",
)


_BARE_SEAL_RE = re.compile(
    r"(?<![\w-])seal(?![\w-])",
    re.IGNORECASE,
)

_QUALIFIER_PHRASE_RE = re.compile(
    r"\b(" + "|".join(re.escape(q) for q in DOMAIN_QUALIFIERS) + r")\b",
    re.IGNORECASE,
)
_QUALIFIER_ADJ_RE = re.compile(
    r"\b(" + "|".join(_ADJECTIVE_QUALIFIERS) + r")\b[ \t_-]+(?<![\w-])(seal|SEAL|Seal)(?![\w-])",
    re.IGNORECASE,
)

_QUALIFIER_WINDOW = 64


class GuardMode(str, Enum):
    STRICT = "strict"
    AUDIT = "audit"


DEFAULT_MODE: GuardMode = GuardMode.STRICT


@dataclass(frozen=True)
class SealTokenHit:
    surface: str
    token: str
    offset: int
    context_snippet: str
    fingerprint: str


@dataclass(frozen=True)
class SealGuardVerdict:
    mode: GuardMode
    text_sha256: str
    hits: tuple[SealTokenHit, ...]
    quarantined: bool
    disambiguation_required: bool
    detected_domains: tuple[str, ...]
    guard_log_entry: dict[str, Any] = field(default_factory=dict)

    @property
    def is_clean(self) -> bool:
        return not self.hits and not self.quarantined


def _find_domains(text: str) -> set[str]:
    found: set[str] = set()
    for m in _QUALIFIER_PHRASE_RE.finditer(text):
        val = m.group(1).lower()
        if "trap" in val:
            found.add(SealDomain.TRAP_LITHOLOGY.value)
        elif "constitutional" in val:
            found.add(SealDomain.CONSTITUTIONAL.value)
        elif "vault" in val:
            found.add(SealDomain.VAULT.value)
        elif "geological" in val:
            found.add(SealDomain.GEOLOGICAL.value)
        elif "disambiguation" in val:
            found.add(SealDomain.DISAMBIGUATION_REQUIRED.value)
    for m in _QUALIFIER_ADJ_RE.finditer(text):
        adj = m.group(1).lower()
        if adj == "trap":
            found.add(SealDomain.TRAP_LITHOLOGY.value)
        elif adj == "constitutional":
            found.add(SealDomain.CONSTITUTIONAL.value)
        elif adj == "vault":
            found.add(SealDomain.VAULT.value)
        elif adj == "geological":
            found.add(SealDomain.GEOLOGICAL.value)
    return found


def _classify(text: str) -> tuple[tuple[SealTokenHit, ...], tuple[str, ...]]:
    if not text:
        return (), ()
    detected = _find_domains(text)
    bare_hits: list[SealTokenHit] = []
    classified_spans: list[tuple[int, int]] = []
    for m in _QUALIFIER_PHRASE_RE.finditer(text):
        classified_spans.append((m.start(), m.end()))
    for m in _QUALIFIER_ADJ_RE.finditer(text):
        classified_spans.append((m.start(0), m.end(0)))
    for m in _BARE_SEAL_RE.finditer(text):
        inside_classified = any(s <= m.start() and m.end() <= e for s, e in classified_spans)
        if inside_classified:
            continue
        start = max(0, m.start() - _QUALIFIER_WINDOW)
        end = min(len(text), m.end() + _QUALIFIER_WINDOW)
        window = text[start:end]
        window_has_qualifier = bool(
            _QUALIFIER_PHRASE_RE.search(window)
            or _QUALIFIER_ADJ_RE.search(window)
        )
        if window_has_qualifier:
            continue
        tok = m.group(0)
        offset = m.start()
        snippet_start = max(0, offset - 40)
        snippet_end = min(len(text), offset + len(tok) + 40)
        snippet = text[snippet_start:snippet_end]
        fp_src = f"{tok}|{offset}"
        fp = hashlib.sha256(fp_src.encode("utf-8")).hexdigest()[:16]
        bare_hits.append(
            SealTokenHit(
                surface="text",
                token=tok,
                offset=offset,
                context_snippet=snippet,
                fingerprint=fp,
            )
        )
    return tuple(bare_hits), tuple(sorted(detected))


def scan(
    text: str,
    *,
    surface: str = "text",
    mode: GuardMode = DEFAULT_MODE,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> SealGuardVerdict:
    bare_hits, detected = _classify(text)
    hits = tuple(
        SealTokenHit(
            surface=surface,
            token=h.token,
            offset=h.offset,
            context_snippet=h.context_snippet,
            fingerprint=h.fingerprint,
        )
        for h in bare_hits
    )
    quarantined = bool(hits) and mode == GuardMode.STRICT
    disambiguation_required = bool(hits)
    text_sha = hashlib.sha256((text or "").encode("utf-8")).hexdigest()
    log_entry: dict[str, Any] = {
        "ts": time.time(),
        "actor_id": actor_id,
        "session_id": session_id,
        "surface": surface,
        "mode": mode.value,
        "text_sha256": text_sha,
        "bare_seal_hits": [
            {
                "token": h.token,
                "offset": h.offset,
                "fingerprint": h.fingerprint,
                "snippet": h.context_snippet,
            }
            for h in hits
        ],
        "detected_domains": list(detected),
        "quarantined": quarantined,
        "disambiguation_required": disambiguation_required,
    }
    return SealGuardVerdict(
        mode=mode,
        text_sha256=text_sha,
        hits=hits,
        quarantined=quarantined,
        disambiguation_required=disambiguation_required,
        detected_domains=detected,
        guard_log_entry=log_entry,
    )


def scan_many(
    texts: Iterable[tuple[str, str]],
    *,
    mode: GuardMode = DEFAULT_MODE,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> list[SealGuardVerdict]:
    return [
        scan(t, surface=s, mode=mode, actor_id=actor_id, session_id=session_id)
        for s, t in texts
    ]


def raises(verdict: SealGuardVerdict) -> None:
    if verdict.quarantined:
        raise SealQuarantineError(verdict)


class SealQuarantineError(Exception):
    def __init__(self, verdict: SealGuardVerdict):
        self.verdict = verdict
        n = len(verdict.hits)
        super().__init__(
            f"Seal token quarantine: {n} bare `seal` token(s) detected "
            f"without domain qualifier. Add one of {sorted(DOMAIN_QUALIFIERS)} "
            f"or set mode=audit."
        )


def log_to_sink(verdict: SealGuardVerdict, sink_path: str | None = None) -> None:
    target = sink_path or "/root/VAULT999/guard.log"
    try:
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "a", encoding="utf-8") as f:
            f.write(json.dumps(verdict.guard_log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _selftest() -> int:
    cases = [
        ("Seal this contract.", "user_message", False, []),
        ("Please apply the geological_seal to the trap.", "user_message", True, ["geological_seal"]),
        ("Constitutional SEAL granted by arif_judge.", "vault_entry", True, ["constitutional_SEAL"]),
        ("Vault seal recorded at 2026-06-28.", "log_line", True, ["vault_seal"]),
        ("The trap_seal_lithology is fractured.", "geox_text", True, ["trap_seal_lithology"]),
        ("seal_disambiguation_required", "log_line", True, ["seal_disambiguation_required"]),
        ("I want to seal this deal.", "user_message", False, []),
        ("Approve and SEAL the receipt now.", "receipt_field", False, []),
        ("No seal words here at all.", "log_line", False, []),
        ("sealant for the joint", "log_line", True, []),
        ("Geological SEAL active in this well.", "geox_text", True, ["geological_seal"]),
        ("999 SEAL ALIVE", "user_message", False, []),
    ]
    fails = 0
    for i, (text, surface, expected_clean, expected_domains) in enumerate(cases, 1):
        v = scan(text, surface=surface)
        got_clean = v.is_clean
        got_domains = set(v.detected_domains)
        want_domains = set(expected_domains)
        ok = (got_clean == expected_clean) and (got_domains == want_domains)
        status = "PASS" if ok else "FAIL"
        print(
            f"[{status}] case {i:>2}: surface={surface:<14} "
            f"clean={got_clean!s:<5} domains={sorted(got_domains)} | "
            f"text={text!r}"
        )
        if not ok:
            fails += 1
    if fails:
        print(f"\n{fails}/{len(cases)} cases FAILED")
        return 1
    print(f"\nAll {len(cases)} cases PASSED")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_selftest())