from __future__ import annotations

from typing import Any

from skills import SKILL_REGISTRY


async def execute_skill(
    skill_name: str,
    action: str,
    params: dict[str, Any],
    session_id: str,
    dry_run: bool = True,
    reality_bridge: Any | None = None,
    checkpoint: str | None = None,
) -> dict[str, Any]:
    skill_info = SKILL_REGISTRY.get(skill_name)
    if not skill_info:
        return {"verdict": "VOID", "error": f"Unknown skill: {skill_name}"}
    return await skill_info["execute"](
        action=action,
        params=params,
        session_id=session_id,
        dry_run=dry_run,
        reality_bridge=reality_bridge,
        checkpoint=checkpoint,
    )
