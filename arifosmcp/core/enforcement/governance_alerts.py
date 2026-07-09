"""
Governance Alerts — append-only G_threshold / scar raise log
═══════════════════════════════════════════════════════════════════════════════
F11 AUDIT: every dynamic threshold raise is human-auditable weekly.

Default path (override with ARIFOS_GOVERNANCE_ALERTS_PATH):
  /root/.local/share/arifos/governance_alerts.log

Line format: JSONL (one event per line). Never rewrite; append only.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_DEFAULT_PATH = Path(
    os.environ.get(
        "ARIFOS_GOVERNANCE_ALERTS_PATH",
        "/root/.local/share/arifos/governance_alerts.log",
    )
)

_lock = threading.Lock()
# In-process last known G_threshold per agent (for raise detection)
_last_g: dict[str, float] = {}


@dataclass
class GovernanceAlert:
    event: str
    agent_id: str
    g_threshold_old: float
    g_threshold_new: float
    cumulative_scar: float
    scar_weight: float
    verdict: str
    reason: str
    ts: float = field(default_factory=time.time)
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_line(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, ensure_ascii=False)


def compute_g_threshold(
    cumulative_scar: float,
    *,
    base: float = 0.80,
    sensitivity: float = 0.18,
    ceiling: float = 0.99,
) -> float:
    """
    Dynamic autonomy bar.

    High scar weight (S_w) raises G_threshold — agent must clear a higher bar.
    Self-correcting sovereignty: chronic failure tightens the gate.
    """
    s = max(0.0, min(1.0, float(cumulative_scar)))
    return min(ceiling, base + sensitivity * s)


def emit_g_threshold_raise(
    *,
    agent_id: str,
    g_threshold_new: float,
    cumulative_scar: float,
    scar_weight: float,
    verdict: str,
    reason: str = "",
    session_id: str | None = None,
    path: Path | None = None,
    min_delta: float = 0.001,
    metadata: dict[str, Any] | None = None,
) -> GovernanceAlert | None:
    """
    Append alert only when G_threshold rises for this agent.
    Returns the alert if written, else None.
    """
    old = _last_g.get(agent_id)
    if old is not None and g_threshold_new <= old + min_delta:
        _last_g[agent_id] = max(old, g_threshold_new)
        return None

    alert = GovernanceAlert(
        event="G_THRESHOLD_RAISE",
        agent_id=agent_id,
        g_threshold_old=float(old if old is not None else 0.80),
        g_threshold_new=float(g_threshold_new),
        cumulative_scar=float(cumulative_scar),
        scar_weight=float(scar_weight),
        verdict=str(verdict),
        reason=reason
        or (
            f"S_w cumulative={cumulative_scar:.4f} raised G_threshold "
            f"{(old if old is not None else 0.80):.4f} → {g_threshold_new:.4f}"
        ),
        session_id=session_id,
        metadata=metadata or {},
    )
    _append(alert, path=path)
    _last_g[agent_id] = g_threshold_new
    return alert


def _append(alert: GovernanceAlert, *, path: Path | None = None) -> None:
    target = path or _DEFAULT_PATH
    target.parent.mkdir(parents=True, exist_ok=True)
    line = alert.to_line() + "\n"
    with _lock:
        with open(target, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()


def reset_agent_baseline(agent_id: str | None = None) -> None:
    """Test helper — clear in-process last-G map."""
    if agent_id is None:
        _last_g.clear()
    else:
        _last_g.pop(agent_id, None)


def read_alerts(
    path: Path | None = None,
    *,
    agent_id: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Tail/read governance alerts for weekly manual audit."""
    target = path or _DEFAULT_PATH
    if not target.exists():
        return []
    rows: list[dict[str, Any]] = []
    with open(target, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if agent_id and obj.get("agent_id") != agent_id:
                continue
            rows.append(obj)
    return rows[-limit:]


def worst_agents(
    path: Path | None = None,
    *,
    top_n: int = 10,
) -> list[tuple[str, int, float]]:
    """
    Weekly audit helper: agents with most G_THRESHOLD_RAISE events.
    Returns (agent_id, raise_count, max_g_threshold).
    """
    rows = read_alerts(path, limit=10_000)
    stats: dict[str, list[float]] = {}
    for r in rows:
        if r.get("event") != "G_THRESHOLD_RAISE":
            continue
        aid = str(r.get("agent_id", "unknown"))
        stats.setdefault(aid, []).append(float(r.get("g_threshold_new", 0.0)))
    ranked = sorted(
        ((aid, len(vals), max(vals) if vals else 0.0) for aid, vals in stats.items()),
        key=lambda t: (-t[1], -t[2]),
    )
    return ranked[:top_n]


__all__ = [
    "GovernanceAlert",
    "compute_g_threshold",
    "emit_g_threshold_raise",
    "reset_agent_baseline",
    "read_alerts",
    "worst_agents",
]
