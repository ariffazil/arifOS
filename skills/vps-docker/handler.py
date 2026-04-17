"""
arifOS Skill: vps-docker
F1 Amanah - All operations reversible via checkpoint
"""

from typing import Any


class VPSDockerSkill:
    """Docker operations with F1 reversibility."""
    
    def __init__(self):
        self.name = "vps-docker"
        self.floor = "F1"
    
    async def execute(
        self,
        action: str,
        params: dict[str, Any],
        session_id: str,
        dry_run: bool = True,
        reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        """
        Execute Docker action with F1 checkpoint.
        
        Args:
            action: One of check_status, restart_container, inspect_logs
            params: Action parameters
            session_id: Unique session identifier
            dry_run: F7 dry run mode
            reality_bridge: MCP Reality Bridge for actual execution
            checkpoint: F1 reversibility checkpoint ID
        """
        handlers = {
            "check_status": self._check_status,
            "restart_container": self._restart_container,
            "inspect_logs": self._inspect_logs,
        }
        
        handler = handlers.get(action)
        if not handler:
            return {
                "verdict": "VOID",
                "error": f"Unknown action: {action}"
            }
        
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _check_status(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Check Docker container status."""
        container = params.get("container", "arifos-agent")
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": "check_status",
                "container": container,
                "checkpoint": checkpoint,
                "would_check": True
            }
        
        # REALITY: Use Reality Bridge for actual Docker execution
        if reality_bridge:
            result = reality_bridge.execute(
                tool="docker",
                command="ps -f name=" + container,
                params={"container": container},
                checkpoint_id=checkpoint
            )
            return {
                "verdict": result.get("status", "VOID"),
                "mode": "real",
                "action": "check_status",
                "container": container,
                "checkpoint": checkpoint,
                "output": result.get("stdout", ""),
                "error": result.get("stderr", ""),
                "success": result.get("success", False)
            }
        
        return {
            "verdict": "VOID",
            "error": "No reality bridge available for real execution"
        }
    
    async def _restart_container(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Restart Docker container."""
        container = params.get("container", "arifos-agent")
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": "restart_container",
                "container": container,
                "checkpoint": checkpoint,
                "would_restart": True,
                "warning": "Container restart requires F1 checkpoint"
            }
        
        # REALITY: Use Reality Bridge
        if reality_bridge:
            result = reality_bridge.execute(
                tool="docker",
                command="restart",
                params={"container": container},
                checkpoint_id=checkpoint
            )
            return {
                "verdict": result.get("status", "VOID"),
                "mode": "real",
                "action": "restart_container",
                "container": container,
                "checkpoint": checkpoint,
                "success": result.get("success", False),
                "f1_note": f"Rollback: aclip checkpoint restore {checkpoint}"
            }
        
        return {
            "verdict": "VOID",
            "error": "No reality bridge available for real execution"
        }
    
    async def _inspect_logs(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Inspect container logs."""
        container = params.get("container", "arifos-agent")
        tail = params.get("tail", 100)
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": "inspect_logs",
                "container": container,
                "tail": tail,
                "checkpoint": checkpoint
            }
        
        # REALITY: Use Reality Bridge
        if reality_bridge:
            result = reality_bridge.execute(
                tool="docker",
                command=f"logs --tail {tail}",
                params={"container": container},
                checkpoint_id=checkpoint
            )
            return {
                "verdict": result.get("status", "VOID"),
                "mode": "real",
                "action": "inspect_logs",
                "container": container,
                "checkpoint": checkpoint,
                "logs": result.get("stdout", ""),
                "success": result.get("success", False)
            }
        
        return {
            "verdict": "VOID",
            "error": "No reality bridge available for real execution"
        }


# Export
skill = VPSDockerSkill()


async def execute(
    action: str,
    params: dict[str, Any],
    session_id: str,
    dry_run: bool = True,
    reality_bridge: Any | None = None,
    checkpoint: str | None = None
) -> dict[str, Any]:
    """Entry point for skill execution."""
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)


metadata = {
    "name": "vps-docker",
    "floor": "F1",
    "actions": ["check_status", "restart_container", "inspect_logs"],
    "reversible": True
}
