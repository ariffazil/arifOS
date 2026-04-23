"""
arifOS Skill: git-ops
F1 Amanah - Git operations with worktree sandbox
"""

from typing import Any


class GitOpsSkill:
    """Git operations with F1 reversibility via worktree."""
    
    def __init__(self):
        self.name = "git-ops"
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
        """Execute Git action with F1 checkpoint."""
        handlers = {
            "status": self._status,
            "checkout_branch": self._checkout_branch,
            "commit": self._commit,
        }
        
        handler = handlers.get(action)
        if not handler:
            return {
                "verdict": "VOID",
                "error": f"Unknown action: {action}"
            }
        
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _status(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Check git status."""
        path = params.get("path", ".")
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": "status",
                "path": path,
                "checkpoint": checkpoint
            }
        
        if reality_bridge:
            result = reality_bridge.execute(
                tool="git",
                command="status --porcelain",
                params={"path": path},
                checkpoint_id=checkpoint
            )
            return {
                "verdict": result.get("status", "VOID"),
                "mode": "real",
                "action": "status",
                "path": path,
                "output": result.get("stdout", ""),
                "success": result.get("success", False)
            }
        
        return {
            "verdict": "VOID",
            "error": "No reality bridge available"
        }
    
    async def _checkout_branch(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Checkout a branch."""
        branch = params.get("branch", "main")
        path = params.get("path", ".")
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": "checkout_branch",
                "branch": branch,
                "checkpoint": checkpoint,
                "f1_note": f"Can rollback via worktree: {checkpoint}"
            }
        
        if reality_bridge:
            result = reality_bridge.execute(
                tool="git",
                command=f"checkout {branch}",
                params={"path": path},
                checkpoint_id=checkpoint
            )
            return {
                "verdict": result.get("status", "VOID"),
                "mode": "real",
                "action": "checkout_branch",
                "branch": branch,
                "checkpoint": checkpoint,
                "success": result.get("success", False),
                "f1_note": f"Rollback: aclip checkpoint restore {checkpoint}"
            }
        
        return {
            "verdict": "VOID",
            "error": "No reality bridge available"
        }
    
    async def _commit(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Create a commit."""
        message = params.get("message", "arifOS automated commit")
        path = params.get("path", ".")
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": "commit",
                "message": message,
                "checkpoint": checkpoint
            }
        
        if reality_bridge:
            result = reality_bridge.execute(
                tool="git",
                command=f'commit -m "{message}"',
                params={"path": path},
                checkpoint_id=checkpoint
            )
            return {
                "verdict": result.get("status", "VOID"),
                "mode": "real",
                "action": "commit",
                "message": message,
                "checkpoint": checkpoint,
                "success": result.get("success", False)
            }
        
        return {
            "verdict": "VOID",
            "error": "No reality bridge available"
        }


skill = GitOpsSkill()


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
    "name": "git-ops",
    "floor": "F1",
    "actions": ["status", "checkout_branch", "commit"],
    "reversible": True
}
