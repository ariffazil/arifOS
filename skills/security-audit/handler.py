"""
security-audit skill handler
F12 injection defense and security scanning.
Wired to Reality Bridge for filesystem scanning.
"""

from typing import Any


class SecurityAuditSkill:
    """Skill for security auditing with F12 protection."""
    
    NAME = "security-audit"
    FLOOR = "F12"
    
    INJECTION_PATTERNS = [
        "IGNORE ALL PREVIOUS INSTRUCTIONS",
        "bypass", "override", "sudo", "rm -rf /",
        ";", "&&", "||", "`", "$(", ">>", ">/"
    ]
    
    async def execute(
        self,
        action: str,
        params: dict[str, Any],
        session_id: str,
        dry_run: bool = True,
        reality_bridge: Any | None = None,
        checkpoint: str | None = None
    ) -> dict[str, Any]:
        """Execute security audit action."""
        handlers = {
            "check_injection": self._check_injection,
            "scan_files": self._scan_files,
        }
        
        handler = handlers.get(action)
        if not handler:
            return {"verdict": "VOID", "reason": f"Unknown action: {action}"}
        
        return await handler(params, dry_run, reality_bridge, checkpoint)
    
    async def _check_injection(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """F12: Scan for injection attempts."""
        content = params.get("content", "")
        
        threats = []
        for pattern in self.INJECTION_PATTERNS:
            if pattern.lower() in content.lower():
                threats.append(pattern)
        
        if threats:
            return {
                "verdict": "VOID",
                "mode": "scan",
                "floor_violated": "F12",
                "threats_detected": threats,
                "action": "BLOCK",
                "checkpoint": checkpoint
            }
        
        return {
            "verdict": "SEAL",
            "mode": "scan",
            "f12_passed": True,
            "threats": 0,
            "checkpoint": checkpoint
        }
    
    async def _scan_files(
        self,
        params: dict,
        dry_run: bool,
        reality_bridge: Any | None,
        checkpoint: str | None
    ) -> dict[str, Any]:
        """Scan files for security issues."""
        path = params.get("path", ".")
        
        if dry_run:
            return {
                "verdict": "SEAL",
                "mode": "dry_run",
                "action": "scan_files",
                "path": path,
                "checkpoint": checkpoint
            }
        
        # REALITY: Use Reality Bridge for filesystem scan
        if reality_bridge:
            result = reality_bridge.execute(
                tool="shell",
                command=f"find {path} -type f -name '*.py' -exec grep -l 'password' {{}} \\;",
                params={},
                checkpoint_id=checkpoint
            )
            
            return {
                "verdict": "SEAL" if result.get("success") else "PARTIAL",
                "mode": "real",
                "path": path,
                "suspicious_files": result.get("stdout", "").split("\n") if result.get("success") else [],
                "checkpoint": checkpoint
            }
        
        return {
            "verdict": "VOID",
            "error": "No reality bridge available"
        }


skill = SecurityAuditSkill()


async def execute(
    action: str,
    params: dict[str, Any],
    session_id: str,
    dry_run: bool = True,
    reality_bridge: Any | None = None,
    checkpoint: str | None = None
) -> dict[str, Any]:
    """Main entry point."""
    skill = SecurityAuditSkill()
    return await skill.execute(action, params, session_id, dry_run, reality_bridge, checkpoint)


metadata = {
    "name": "security-audit",
    "floor": "F12",
    "actions": ["check_injection", "scan_files"],
    "reversible": False
}
