"""
constitutional-check skill handler
F3 Tri-Witness consensus evaluation.
Wired to Reality Bridge for system state verification.
"""

from typing import Any

from core.intelligence import compute_w3


class ConstitutionalCheckSkill:
    """Skill for constitutional verification with F3."""
    
    NAME = "constitutional-check"
    FLOOR = "F3"
    
    async def execute(
        self, action: str, params: dict, session_id: str,
        dry_run: bool = True, reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        handlers = {
            "evaluate_proposal": self._evaluate_proposal,
            "verify_system_state": self._verify_system_state,
        }
        handler = handlers.get(action)
        if not handler:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _evaluate_proposal(self, params: dict, dry_run: bool,
                                 reality_bridge: Any | None, checkpoint: str | None) -> dict:
        human = params.get("human_score", 0)
        ai = params.get("ai_score", 0)
        earth = params.get("earth_score", 0)
        
        w3 = compute_w3(human, ai, earth)
        
        verdicts = {(True, True, True): "SEAL", (True, True, False): "SABAR",
                   (True, False, True): "HOLD", (False, True, True): "PARTIAL"}
        key = (w3 >= 0.95, ai >= 0.9, earth >= 0.9)
        verdict = verdicts.get(key, "VOID")
        
        return {
            "verdict": verdict,
            "w3_score": w3,
            "witnesses": {"human": human, "ai": ai, "earth": earth},
            "threshold": 0.95,
            "passed": w3 >= 0.95,
            "checkpoint": checkpoint
        }
    
    async def _verify_system_state(self, params: dict, dry_run: bool,
                                   reality_bridge: Any | None, checkpoint: str | None) -> dict:
        component = params.get("component", "system")
        
        if dry_run:
            return {"verdict": "SEAL", "mode": "dry_run", "component": component, "checkpoint": checkpoint}
        
        # REALITY: Verify actual system state
        if reality_bridge:
            # Check if component is running
            result = reality_bridge.execute(
                tool="shell",
                command=f"systemctl is-active {component}",
                params={},
                checkpoint_id=checkpoint
            )
            
            is_active = result.get("stdout", "").strip() == "active"
            
            return {
                "verdict": "SEAL",
                "mode": "real",
                "component": component,
                "is_active": is_active,
                "checkpoint": checkpoint
            }
        
        return {"verdict": "VOID", "error": "No reality bridge available"}


skill = ConstitutionalCheckSkill()


async def execute(action: str, params: dict, session_id: str,
                  dry_run: bool = True, reality_bridge: Any | None = None,
                  checkpoint: str | None = None) -> dict[str, Any]:
    skill = ConstitutionalCheckSkill()
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)


metadata = {"name": "constitutional-check", "floor": "F3", "actions": ["evaluate_proposal", "verify_system_state"], "reversible": False}
