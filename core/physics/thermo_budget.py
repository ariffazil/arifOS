from __future__ import annotations

from dataclasses import dataclass, field

LANDAUER_LIMIT_JOULES = 1.380649e-23 * 300.0 * 0.6931471805599453
BITS_PER_TOKEN = 32


@dataclass
class ThermoSnapshot:
    session_id: str
    token_cost: int = 0
    bits_erased: int = 0
    min_energy_joules: float = 0.0


@dataclass
class ThermoBudget:
    _sessions: dict[str, ThermoSnapshot] = field(default_factory=dict)

    def open_session(self, session_id: str) -> ThermoSnapshot:
        return self._sessions.setdefault(
            session_id, ThermoSnapshot(session_id=session_id)
        )

    def record_step(self, session_id: str, *, tokens: int) -> ThermoSnapshot:
        snap = self.open_session(session_id)
        snap.token_cost += max(0, tokens)
        snap.bits_erased += max(0, tokens) * BITS_PER_TOKEN
        snap.min_energy_joules = snap.bits_erased * LANDAUER_LIMIT_JOULES
        return snap

    def snapshot(self, session_id: str) -> ThermoSnapshot:
        return self.open_session(session_id)


__all__ = ["LANDAUER_LIMIT_JOULES", "ThermoBudget", "ThermoSnapshot"]
