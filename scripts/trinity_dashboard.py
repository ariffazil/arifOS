from __future__ import annotations


class TrinityDashboard:
    def __init__(self) -> None:
        self._sessions: list[dict[str, str]] = []

    def register_session(self, session_id: str, skill_name: str, operator_id: str) -> None:
        self._sessions.append(
            {
                "session_id": session_id,
                "skill_name": skill_name,
                "operator_id": operator_id,
            }
        )

    def get_dashboard_view(self) -> dict:
        return {
            "total_sessions": len(self._sessions),
            "sessions": list(self._sessions),
        }
