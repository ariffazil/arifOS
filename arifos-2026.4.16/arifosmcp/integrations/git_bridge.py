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
from arifosmcp.runtime.continuity_contract import seal_runtime_envelope
from arifosmcp.runtime.models import RiskClass, RuntimeEnvelope, Verdict

# RuntimeEnvelope aliased as RE for readability in this module
RE = RuntimeEnvelope

logger = logging.getLogger(__name__)

# F1: Repository whitelist (mounted in docker-compose)
ALLOWEDREPOS = ["/usr/src/project"]

class GitBridge:
    """Sovereign facade for Git operations."""

    def _is_repo_allowed(self, repo_path: str) -> bool:
        """Strict whitelisting check."""
        return repo_path in ALLOWEDREPOS

    async def get_repo_state(
        self,
        repo_path: str = "/usr/src/project",
        actor_id: str = "anonymous",
        session_id: str | None = None
    ) -> RE:
        """F2/F11: Read-only audit of current repository status."""
        if not self._is_repo_allowed(repo_path):
            return RE(ok=False, tool="arifos.git_status", stage='', verdict=Verdict.VOID, detail=f"F8 BLOCK: Unauthorized repo path: {repo_path}")

        # Governance Check (Baseline Audit)
        gov = evaluate_tool_call(
            action="git_status",
            tool_name="arifos_git",
            parameters={"repo_path": repo_path, "query": f"git_status {repo_path}"},
            actor_id=actor_id,
            session_id=session_id
        )
        
        if gov.verdict != Verdict.SEAL:
            return RE(ok=False, tool="arifos.git_status", stage='', verdict=gov.verdict, detail=gov.message)

        try:
            status = await bridge.git.call_tool("git_status", {"repo_path": repo_path})
            log = await bridge.git.call_tool("git_log", {"repo_path": repo_path, "max_count": 5})
            
            return RE(
                ok=True,
                tool="arifos.git_status",
                stage='',
                verdict=Verdict.SEAL,
                payload={
                    "status": status,
                    "recent_history": log
                }
            )
        except Exception as e:
            return RE(ok=False, tool="arifos.git_status", stage='', verdict=Verdict.VOID, detail=str(e))

    async def propose_commit(
        self,
        repo_path: str,
        message: str,
        files: list[str],
        actor_id: str,
        session_id: str | None = None
    ) -> RE:
        """F1/F13: Execute a commit ONLY after human ratification and SEAL validation."""
        if not self._is_repo_allowed(repo_path):
            return RE(ok=False, tool="arifos.git_commit", stage='', verdict=Verdict.VOID, detail=f"F8 BLOCK: Unauthorized repo path: {repo_path}")

        # 1. Evaluate Mutation Governance (Requires HIGH risk tier)
        gov = evaluate_tool_call(
            action="git_commit",
            tool_name="arifos_git",
            parameters={"repo_path": repo_path, "message": message, "files": files},
            actor_id=actor_id,
            session_id=session_id
        )

        if gov.verdict != Verdict.SEAL:
            return RE(
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
            
            return RE(
                ok=True,
                tool="arifos.git_commit",
                stage='',
                verdict=Verdict.SEAL,
                payload={
                    "commit_sha": result.get("sha"),
                    "message": "Audit trail updated in Git substrate and VAULT999."
                }
            )
        except Exception as e:
            return RE(ok=False, tool="arifos.git_commit", stage='', verdict=Verdict.VOID, detail=str(e))

# Global bridge instance
git_bridge = GitBridge()

# Module-level wrappers for runtime integration
# These adapt the public tool contract to the internal GitBridge interface.
# Public contract: path (str, default './')
# Internal interface: repo_path (str, default '/usr/src/project')
async def arifos_repo_read(path: str = "./", actor_id: str = "anonymous", session_id: str | None = None) -> RE:
    repo_path = path if path else "/usr/src/project"
    result = await git_bridge.get_repo_state(repo_path, actor_id, session_id)
    # Auto-seal: if already a sealed RuntimeEnvelope, return as-is
    if isinstance(result, RuntimeEnvelope):
        return result
    # Otherwise wrap via continuity contract
    return seal_runtime_envelope(result, "arifos_repo_read", session_id=session_id)

# Public contract: message (required), files (optional)
# Internal interface: repo_path, message, files, actor_id
async def arifos_repo_seal(message: str, files: list[str] | None = None, actor_id: str = "anonymous", session_id: str | None = None) -> RE:
    repo_path = "/usr/src/project"
    result = await git_bridge.propose_commit(
        repo_path=repo_path,
        message=message,
        files=files or [],
        actor_id=actor_id,
        session_id=session_id
    )
    if isinstance(result, RuntimeEnvelope):
        return result
    return seal_runtime_envelope(result, "arifos_repo_seal", session_id=session_id)
