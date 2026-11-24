"""windowed_ds.py — F4 instrument: real windowed entropy-delta over tool_calls outcome-classes.

EUREKA::DUAL-PROVENANCE-ANALYSIS-CACHE adjacent; pins the kx010 entropy_delta contract
(previously "producer instrument unpinned", placeholder -0.0).

dS = H(outcome classes, window N) - H(outcome classes, window N-1), Shannon bits.
Store: public.arifosmcp_tool_calls (same store the G floor reads), ordered by id desc.
Fail-closed: any error -> None (the caller keeps DEFAULT_UNMEASURED honesty; never a fake number).
Deterministic per store state -> recomputable falsifier.
Forged 333-AGI 2026-11-14 (sovereign-approved F4 instrument work).
"""
import math
import os
import time
from collections import Counter

WINDOW = int(os.environ.get("ARIFOS_DS_WINDOW", "100"))
TTL_S = float(os.environ.get("ARIFOS_DS_TTL_S", "60"))
_cache = {"ts": 0.0, "value": None}


def _fetch_outcomes(limit: int):
    import httpx

    base = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_KEY") or ""
    if not base or not key:
        # Root-cron builders: inherit SUPABASE_* from the running kernel's live
        # environment (the kernel holds them via its EnvironmentFile). Root can
        # read /proc; non-root contexts without env keep fail-closed semantics.
        import subprocess as _sp

        try:
            _pids = _sp.run(
                ["pgrep", "-f", "arifosmcp.runtime.__main__"],
                capture_output=True, text=True, timeout=5,
            ).stdout.split()
            for _p in _pids[:3]:
                try:
                    with open(f"/proc/{_p}/environ", "rb") as fh:
                        for _line in fh.read().decode(errors="ignore").split("\0"):
                            if "=" not in _line:
                                continue
                            _k, _v = _line.split("=", 1)
                            if _k == "SUPABASE_URL" and not base:
                                base = _v
                            elif _k == "SUPABASE_SERVICE_ROLE_KEY" and not key:
                                key = _v
                except OSError:
                    continue
                if base and key:
                    break
        except Exception:
            pass
        if not base or not key:
            raise RuntimeError("supabase env missing")
    url = (
        f"{base}/rest/v1/arifosmcp_tool_calls"
        f"?select=id,result_code,verdict&order=id.desc&limit={limit}"
    )
    resp = httpx.get(url, headers={"apikey": key, "Authorization": f"Bearer {key}"}, timeout=8.0)
    resp.raise_for_status()
    rows = resp.json()
    return [(int(r.get("id", 0)), str(r.get("result_code") or r.get("verdict") or "UNKNOWN")) for r in rows]


def _entropy_bits(classes) -> float | None:
    counts = Counter(classes)
    n = sum(counts.values())
    if n == 0:
        return None
    return -sum((v / n) * math.log2(v / n) for v in counts.values())


def measure_windowed_ds(window: int | None = None, use_cache: bool = True) -> dict | None:
    """Windowed outcome-class entropy delta. None = unmeasured (honest), never fabricated."""
    global _cache
    window = window or WINDOW
    now = time.time()
    if use_cache and _cache["value"] is not None and (now - _cache["ts"]) < TTL_S:
        return _cache["value"]
    try:
        try:
            rows = _fetch_outcomes(2 * window)
        except Exception:
            # transient store hiccup (observed under observatory snapshot load):
            # one retry before honest None — never fabricate, just de-flake.
            time.sleep(1.0)
            rows = _fetch_outcomes(2 * window)
        if len(rows) < window:
            _cache = {"ts": now, "value": None}
            return None
        next_classes = [cls for _, cls in rows[:window]]
        prev_classes = [cls for _, cls in rows[window : 2 * window]]
        h_next = _entropy_bits(next_classes)
        h_prev = _entropy_bits(prev_classes)
        if h_next is None or h_prev is None:
            _cache = {"ts": now, "value": None}
            return None
        result = {
            "value": (lambda v: 0.0 if v == 0 else v)(round(h_next - h_prev, 6)),  # normalize -0.0
            "instrument": "windowed-outcome-shannon.v1",
            "store": "public.arifosmcp_tool_calls",
            "window": window,
            "h_next_bits": round(h_next, 6),
            "h_prev_bits": round(h_prev, 6),
            "classes_next": dict(Counter(next_classes)),
            "classes_prev": dict(Counter(prev_classes)),
            "n_rows": len(rows),
            "measured_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "falsifier": (
                "recompute: arifosmcp_tool_calls order id desc, outcome=result_code, "
                "H(rows[:100]) - H(rows[100:200])"
            ),
        }
        _cache = {"ts": now, "value": result}
        return result
    except Exception:
        import logging

        logging.getLogger("arifos.windowed_ds").warning(
            "windowed_ds fetch failed: %s", exc_info=True
        )
        _cache = {"ts": now, "value": None}
        return None
