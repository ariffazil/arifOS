"""
code-refactor skill handler
F8 wisdom-guided code refactoring.
"""

from typing import Any


class CodeRefactorSkill:
    """Skill for code refactoring with F8 genius scoring."""
    
    NAME = "code-refactor"
    FLOOR = "F8"
    
    def calculate_genius(self, a: float, p: float, x: float, e: float) -> float:
        """G = A x P x X x E squared"""
        return a * p * x * (e ** 2)
    
    async def execute(
        self, action: str, params: dict, session_id: str,
        dry_run: bool = True, reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        handlers = {
            "propose_refactor": self._propose_refactor,
            "apply_refactor": self._apply_refactor,
        }
        handler = handlers.get(action)
        if not handler:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _propose_refactor(self, params: dict, dry_run: bool,
                                reality_bridge: Any | None, checkpoint: str | None) -> dict:
        code = params.get("code", "")
        goal = params.get("goal", "")
        
        genius = self.calculate_genius(0.85, 0.90, 0.75, 0.95)
        
        if genius < 0.80:
            return {
                "verdict": "SABAR",
                "reason": f"F8: Genius score {genius:.2f} below 0.80",
                "checkpoint": checkpoint
            }
        
        return {
            "verdict": "SEAL",
            "mode": "dry_run" if dry_run else "proposal",
            "genius_score": genius,
            "checkpoint": checkpoint
        }
    
    async def _apply_refactor(self, params: dict, dry_run: bool,
                              reality_bridge: Any | None, checkpoint: str | None) -> dict:
        file_path = params.get("file_path", "")
        
        if dry_run:
            return {"verdict": "SEAL", "mode": "dry_run", "file": file_path, "checkpoint": checkpoint}
        
        if reality_bridge:
            return {"verdict": "SEAL", "mode": "real", "file": file_path, "checkpoint": checkpoint}
        
        return {"verdict": "VOID", "error": "No reality bridge available"}


skill = CodeRefactorSkill()


async def execute(action: str, params: dict, session_id: str,
                  dry_run: bool = True, reality_bridge: Any | None = None,
                  checkpoint: str | None = None) -> dict[str, Any]:
    skill = CodeRefactorSkill()
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)


metadata = {"name": "code-refactor", "floor": "F8", "actions": ["propose_refactor", "apply_refactor"], "reversible": True}
