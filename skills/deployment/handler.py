"""
deployment skill handler
F11 authority-gated deployment.
Wired to Reality Bridge for kubectl/docker deployment.
"""

from typing import Any


class DeploymentSkill:
    """Skill for deployment with F11 authority checks."""
    
    NAME = "deployment"
    FLOOR = "F11"
    
    async def execute(
        self, action: str, params: dict, session_id: str,
        dry_run: bool = True, reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        handlers = {
            "execute_deployment": self._execute_deployment,
            "rollback": self._rollback,
        }
        handler = handlers.get(action)
        if not handler:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _execute_deployment(self, params: dict, dry_run: bool,
                                  reality_bridge: Any | None, checkpoint: str | None) -> dict:
        environment = params.get("environment", "")
        operator = params.get("operator", "anonymous")
        approved = params.get("approved", False)
        
        # F11: Verify authority
        if not operator or operator == "anonymous":
            return {"verdict": "VOID", "floor_violated": "F11", "reason": "Anonymous deployment not allowed"}
        
        # F13: Human approval for production
        if environment == "production" and not approved:
            return {
                "verdict": "888_HOLD",
                "reason": "F13: Production deployment requires human approval",
                "required": "aclip vault seal --approve=deploy"
            }
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "environment": environment,
                "operator": operator,
                "checkpoint": checkpoint
            }
        
        # REALITY: Execute deployment
        if reality_bridge:
            result = reality_bridge.execute(
                tool="shell",
                command=f"kubectl apply -f deployment/{environment}.yaml",
                params={},
                checkpoint_id=checkpoint
            )
            
            return {
                "verdict": "SEAL" if result.get("success") else "VOID",
                "mode": "real",
                "environment": environment,
                "operator": operator,
                "rollback_plan": f"kubectl rollout undo deployment/{environment}",
                "checkpoint": checkpoint
            }
        
        return {"verdict": "VOID", "error": "No reality bridge available"}
    
    async def _rollback(self, params: dict, dry_run: bool,
                        reality_bridge: Any | None, checkpoint: str | None) -> dict:
        environment = params.get("environment", "")
        
        if dry_run:
            return {"verdict": "SEAL", "mode": "dry_run", "action": "rollback", "checkpoint": checkpoint}
        
        if reality_bridge:
            result = reality_bridge.execute(
                tool="shell",
                command=f"kubectl rollout undo deployment/{environment}",
                params={},
                checkpoint_id=checkpoint
            )
            
            return {
                "verdict": "SEAL" if result.get("success") else "VOID",
                "mode": "real",
                "action": "rollback",
                "checkpoint": checkpoint
            }
        
        return {"verdict": "VOID", "error": "No reality bridge available"}


skill = DeploymentSkill()


async def execute(action: str, params: dict, session_id: str,
                  dry_run: bool = True, reality_bridge: Any | None = None,
                  checkpoint: str | None = None) -> dict[str, Any]:
    skill = DeploymentSkill()
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)


metadata = {"name": "deployment", "floor": "F11", "actions": ["execute_deployment", "rollback"], "reversible": True}
