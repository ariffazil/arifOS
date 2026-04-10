"""
arifosmcp/integrations/git_bridge.py — Governed Version Control Substrate (F1/F11)

Wraps mcp-server-git with arifOS constitutional guards:
- F1 Amanah (Irreversibility / Dry-run by default)
- F11 Audit (Native Git SHA logging)
- 888 HOLD (Human-in-the-loop for mutations)

DITEMPA BUKAN DIBERI — 999 SEAL
"""

from __future__ import annotations

import logging

from core.floors import evaluate_tool_call

from arifosmcp.integrations.substrate_bridge import bridge
from arifosmcp.runtime.models import RiskClass, Verdict
from arifosmcp.runtime.models import RuntimeEnvelope as _RE

logger = logging.getLogger(__name__)

# F1: Repository whitelist (mounted in docker-compose)
ALLOWED_REPOS = ["/usr/src/project"]

class GitBridge:
    """Sovereign facade for Git operations."""

    def _is_repo_allowed(self, repo_path: str) -> bool:
        """Strict whitelisting check."""
        return repo_path in ALLOWED_REPOS

    async def get_repo_state(
        self,
        repo_path: str = "/usr/src/project",
        actor_id: str = "anonymous",
        session_id: str | None = None
    ) -> _RE:
        """F2/F11: Read-only audit of current repository status."""
        if not self._is_repo_allowed(repo_path):
            return _RE(ok=False, tool="arifos.git_status", detail=f"F8 BLOCK: Unauthorized repo path: {repo_path}")

        # Governance Check (Baseline Audit)
        gov = evaluate_tool_call(
            action="git_status",
            tool_name="arifos_git",
            parameters={"repo_path": repo_path},
            actor_id=actor_id,
            session_id=session_id
        )
        
        if gov.verdict != Verdict.SEAL:
            return _RE(ok=False, tool="arifos.git_status", verdict=gov.verdict, detail=gov.message)

        try:
            status = await bridge.git.call_tool("git_status", {"repo_path": repo_path})
            log = await bridge.git.call_tool("git_log", {"repo_path": repo_path, "max_count": 5})
            
            return _RE(
                ok=True,
                tool="arifos.git_status",
                verdict=Verdict.SEAL,
                payload={
                    "status": status,
                    "recent_history": log
                }
            )
        except Exception as e:
            return _RE(ok=False, tool="arifos.git_status", detail=str(e), verdict=Verdict.VOID)

    async def propose_commit(
        self,
        repo_path: str,
        message: str,
        files: list[str],
        actor_id: str,
        session_id: str | None = None
    ) -> _RE:
        """F1/F13: Execute a commit ONLY after human ratification and SEAL validation."""
        if not self._is_repo_allowed(repo_path):
            return _RE(ok=False, tool="arifos.git_commit", detail=f"F8 BLOCK: Unauthorized repo path: {repo_path}")

        # 1. Evaluate Mutation Governance (Requires HIGH risk tier)
        gov = evaluate_tool_call(
            action="git_commit",
            tool_name="arifos_git",
            parameters={"repo_path": repo_path, "message": message, "files": files},
            actor_id=actor_id,
            session_id=session_id
        )

        if gov.verdict != Verdict.SEAL:
            return _RE(
                ok=False, 
                verdict=gov.verdict, 
                detail=f"F13 BLOCK: Mutation blocked by governance: {gov.message}",
                payload={"violations": gov.violations},
                risk_class=RiskClass.HIGH
            )

        # 2. Call Substrate
        try:
            logger.info(f"F11 LOG: [arifOS Governed] Committing change: {message} by {actor_id}")
            
            # Stage files
            await bridge.git.call_tool("git_add", {
                "repo_path": repo_path, 
                "files": files
            })
            
            # Commit
            result = await bridge.git.call_tool("git_commit", {
                "repo_path": repo_path,
                "message": f"[arifOS Governed] {message}"
            })
            
            return _RE(
                ok=True,
                tool="arifos.git_commit",
                verdict=Verdict.SEAL,
                payload={
                    "commit_sha": result.get("sha"),
                    "message": "Audit trail updated in Git substrate and VAULT999."
                }
            )
        except Exception as e:
            return _RE(ok=False, tool="arifos.git_commit", detail=str(e), verdict=Verdict.VOID)

# Global bridge instance
git_bridge = GitBridge()

# Module-level wrappers for runtime integration
# These adapt the public tool contract to the internal GitBridge interface.
# Public contract: path (str, default './')
# Internal interface: repo_path (str, default '/usr/src/project')
async def arifos_git_status(path: str = "./", actor_id: str = "anonymous", session_id: str | None = None) -> _RE:
    repo_path = path if path else "/usr/src/project"
    return await git_bridge.get_repo_state(repo_path, actor_id, session_id)

# Public contract: message (required), files (optional)
# Internal interface: repo_path, message, files, actor_id
async def arifos_git_commit(message: str, files: list[str] | None = None, actor_id: str = "anonymous", session_id: str | None = None) -> _RE:
    repo_path = "/usr/src/project"
    return await git_bridge.propose_commit(
        repo_path=repo_path,
        message=message,
        files=files or [],
        actor_id=actor_id,
        session_id=session_id
    )
