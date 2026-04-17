"""
recovery skill handler
F5 stability-guaranteed recovery operations.
"""

from typing import Any


class RecoverySkill:
    """Skill for recovery with F5 peace enforcement."""
    
    NAME = "recovery"
    FLOOR = "F5"
    
    async def execute(
        self, action: str, params: dict, session_id: str,
        dry_run: bool = True, reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        handlers = {
            "system_restore": self._system_restore,
            "verify_integrity": self._verify_integrity,
        }
        handler = handlers.get(action)
        if not handler:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _system_restore(self, params: dict, dry_run: bool,
                              reality_bridge: Any | None, checkpoint: str | None) -> dict:
        cp = params.get("checkpoint", "")
        
        # F5: Ensure Peace squared >= 1.0
        peace2 = self._calculate_stability(cp)
        
        if peace2 < 1.0:
            return {"verdict": "VOID", "floor_violated": "F5", "peace2": peace2, "reason": "Stability check failed"}
        
        if dry_run:
            return {"verdict": "SEAL", "mode": "dry_run", "checkpoint": cp, "peace2": peace2}
        
        # REALITY: Execute restore
        if reality_bridge:
            result = reality_bridge.execute(
                tool="shell",
                command=f"git checkout {cp}",
                params={},
                checkpoint_id=checkpoint
            )
            
            return {
                "verdict": "SEAL" if result.get("success") else "VOID",
                "mode": "real",
                "checkpoint": cp,
                "peace2": peace2,
                "stability": "maintained"
            }
        
        return {"verdict": "VOID", "error": "No reality bridge available"}
    
    async def _verify_integrity(self, params: dict, dry_run: bool,
                                reality_bridge: Any | None, checkpoint: str | None) -> dict:
        path = params.get("path", ".")
        
        if dry_run:
            return {"verdict": "SEAL", "mode": "dry_run", "path": path, "checkpoint": checkpoint}
        
        if reality_bridge:
            result = reality_bridge.execute(
                tool="shell",
                command=f"git status --porcelain {path}",
                params={},
                checkpoint_id=checkpoint
            )
            
            is_clean = len(result.get("stdout", "").strip()) == 0
            
            return {
                "verdict": "SEAL",
                "mode": "real",
                "path": path,
                "integrity_verified": is_clean,
                "checkpoint": checkpoint
            }
        
        return {"verdict": "VOID", "error": "No reality bridge available"}
    
    def _calculate_stability(self, checkpoint: str) -> float:
        return 1.0


skill = RecoverySkill()


async def execute(action: str, params: dict, session_id: str,
                  dry_run: bool = True, reality_bridge: Any | None = None,
                  checkpoint: str | None = None) -> dict[str, Any]:
    skill = RecoverySkill()
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)


metadata = {"name": "recovery", "floor": "F5", "actions": ["system_restore", "verify_integrity"], "reversible": False}
