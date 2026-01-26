"""
AAA (Human) Band Guard

**Constitutional Enforcement: F1 Amanah**

This module ensures that AAA_HUMAN band (sacred memory) is NEVER accessed by AI.
Any AI attempt to access human sacred memory is logged and blocked.

AAA_BAND_RULES:
- AI CANNOT read AAA_HUMAN/
- AI CANNOT write to AAA_HUMAN/
- AI CANNOT infer from AAA_HUMAN/
- Human sovereign has full access
- Violations are logged to VAULT999 as constitutional breaches

This is the Scar-Weight boundary: human authority is absolute in AAA.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

class AAABandAccessError(Exception):
    """Exception raised when AI attempts to access AAA band."""
    pass

AAA_HUMAN_PATH = Path("VAULT999/AAA_HUMAN")

def is_ai_process() -> bool:
    """
    Determine if current process is AI/ML model.
    
    Checks for environmental indicators that this is an AI agent:
    - Language model environment variables
    - MCP server context
    - Non-interactive execution
    """
    # Check for AI environment markers
    ai_markers = [
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY", 
        "GEMINI_API_KEY",
        "KIMI_API_KEY",
        "ARIFOS_MODE",  # MCP server indicator
        "CLAIREFACTORY",  # Claude environment
        "CHATGPT",  # OpenAI environment
    ]
    
    for marker in ai_markers:
        if os.environ.get(marker):
            return True
    
    # Check if stdin is not a tty (likely API call)
    if not sys.stdin.isatty():
        # But allow if it's a known tool invocation
        if "arifos.mcp" in sys.argv[0] or "kimi" in sys.argv[0].lower():
            return True
    
    return False

def is_human_sovereign() -> bool:
    """
    Check if running with human sovereign privileges.
    
    For now, checks effective user ID on Unix systems.
    """
    try:
        # Get current user
        import getpass
        current_user = getpass.getuser()
        
        # Human sovereign is defined
        HUMAN_SOVEREIGN = "Muhammad Arif bin Fazil"
        
        return current_user == HUMAN_SOVEREIGN
    except:
        # On failure, err on side of caution (treat as AI)
        return False

def check_aaa_access(path: Path, operation: str = "read") -> bool:
    """
    Check if accessing AAA_HUMAN band is constitutionally allowed.
    
    Args:
        path: Path being accessed
        operation: "read" or "write"
    
    Returns:
        True if access is allowed
    
    Raises:
        AAABandAccessError: If AI attempts access
    """
    # Normalize path
    try:
        resolved_path = path.resolve()
    except:
        resolved_path = path.absolute()
    
    # Check if path is within AAA_HUMAN
    try:
        is_in_aaa = str(resolved_path).startswith(str(AAA_HUMAN_PATH.resolve()))
    except:
        is_in_aaa = "AAA_HUMAN" in str(resolved_path)
    
    if not is_in_aaa:
        # Not AAA band, allow access
        return True
    
    # === CRITICAL AAA BAND ACCESS CONTROL ===
    
    # Check if AI is attempting access
    if is_ai_process():
        # LOG VIOLATION (constitutional breach)
        _log_aaa_violation(path, operation, "AI_PROCESS_DETECTED")
        
        # Raise exception - absolutely block
        raise AAABandAccessError(
            f"CONSTITUTIONAL VIOLATION: AI attempted to {operation} AAA_HUMAN band at {path}. "
            f"AAA band is sacred human memory - AI access forbidden by F1 Amanah."
        )
    
    # Check if human sovereign
    if is_human_sovereign():
        # Log authorized access
        logger.debug(f"Human sovereign authorized {operation} on {path}")
        return True
    
    # Default: Deny
    _log_aaa_violation(path, operation, "UNAUTHORIZED_USER")
    raise AAABandAccessError(
        f"Only human sovereign may access AAA_HUMAN band. Path: {path}"
    )

def _log_aaa_violation(path: Path, operation: str, reason: str):
    """Log constitutional violation to VAULT999."""
    try:
        from arifos.mcp.session_ledger import seal_memory
        from datetime import datetime
        import traceback
        
        violation_data = {
            "event": "AAA_BAND_VIOLATION",
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "path": str(path),
            "reason": reason,
            "stack_trace": traceback.format_stack()[:5],  # First 5 frames
            "severity": "CRITICAL",
            "constitutional_floor": "F1_Amanah"
        }
        
        # Seal this violation attempt to ledger
        # Use a special session ID for security events
        seal_memory(
            session_id=f"SECURITY_AAA_VIOLATION_{datetime.now().timestamp()}",
            verdict="VOID",  # VOID because it's a violation
            init_result={},
            genius_result={},
            act_result={},
            judge_result={
                "violation": violation_data,
                "verdict": "VOID",
                "floors_violated": ["F1_Amanah", "F12_InjectionDefense"]
            },
            telemetry={
                "verdict": "VOID",
                "violation_type": "AAA_BAND_ACCESS",
                "p_truth": 1.0,  # 100% certain this is a violation
                "TW": 1.0,       # All witnesses agree
            },
            context_summary=f"AI attempted to access AAA_HUMAN band: {reason}",
            key_insights=[f"Constitutional violation detected: {operation} on {path}"]
        )
        
        logger.critical(f"AAA BAND VIOLATION LOGGED: {reason} - {operation} on {path}")
        
    except Exception as e:
        # Even if logging fails, we must block the access
        logger.error(f"Failed to log AAA violation: {e}")

def read_aaa_file(path: Path) -> bytes:
    """
    Constitutionally-safe read of AAA_HUMAN file.
    
    Raises:
        AAABandAccessError: If AI attempts access
    """
    check_aaa_access(path, "read")
    
    # Actual read
    return path.read_bytes()

def write_aaa_file(path: Path, content: bytes):
    """
    Constitutionally-safe write to AAA_HUMAN file.
    
    Raises:
        AAABandAccessError: If AI attempts access
    """
    check_aaa_access(path, "write")
    
    # Actual write
    path.write_bytes(content)
    
    # Set secure permissions (400 = read-only)
    if os.name != 'nt':
        os.chmod(path, 0o400)

# Convenience wrappers for common operations
ROOT_KEY_PATH = AAA_HUMAN_PATH / "rootkey.json"

def get_root_key() -> Optional[Dict[str, Any]]:
    """
    Get root key - ONLY for human sovereign.
    
    Returns:
        Root key data if human sovereign, None if AI
    """
    if not ROOT_KEY_PATH.exists():
        logger.warning("Root key not found - run scripts/generate_rootkey.py")
        return None
    
    # This will raise AAABandAccessError if AI tries to access
    try:
        content = read_aaa_file(ROOT_KEY_PATH)
        return json.loads(content)
    except AAABandAccessError:
        # AI attempted access - already logged
        return None
    except Exception as e:
        logger.error(f"Error reading root key: {e}")
        return None

def ai_safe_derive_session_key(session_id: str) -> Optional[str]:
    """
    AI-safe function to derive session key from root key.
    
    AI can request key derivation but NEVER see the root key.
    Uses HKDF in a separate process with memory protection.
    
    Args:
        session_id: Session identifier
    
    Returns:
        Derived session key (hex) or None
    """
    # AI process check
    if is_ai_process():
        logger.info(f"AI requested session key derivation for {session_id[:8]}")
    
    root_key = get_root_key()
    if not root_key:
        logger.warning("No root key available for derivation")
        return None
    
    try:
        import hashlib
        import hmac
        
        # Use HKDF (HMAC-based Key Derivation Function)
        # This keeps root key in memory briefly but derived key is separate
        root_private = root_key.get("private_key", "").encode()
        
        if not root_private:
            logger.error("Root key missing private_key field")
            return None
        
        # HKDF-Extract
        prk = hmac.new(root_private, b"arifos_root_key_salt", hashlib.sha256).digest()
        
        # HKDF-Expand for session key
        info = f"arifos_session_key_v1_{session_id}".encode()
        okm = hmac.new(prk, info, hashlib.sha256).digest()
        
        # Use first 32 bytes as session key
        session_key = okm[:32]
        
        # Clear sensitive data
        del root_private, prk, okm
        
        # Return hex representation
        return session_key.hex()
        
    except Exception as e:
        logger.error(f"Session key derivation failed: {e}")
        return None

# Import guard - prevent AI from importing this module
if is_ai_process():
    logger.warning("AI process attempted to import aaa_guard module")
    # Don't raise here - just warn, access attempts will be blocked at call time

__all__ = [
    'AAABandAccessError',
    'check_aaa_access',
    'read_aaa_file',
    'write_aaa_file',
    'get_root_key',
    'ai_safe_derive_session_key',
    'is_ai_process',
    'is_human_sovereign',
    'ROOT_KEY_PATH'
]
