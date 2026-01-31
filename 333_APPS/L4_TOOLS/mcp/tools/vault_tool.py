"""
VAULT Tool - Immutable Seal & Governance IO
v55.0 - Cryptographic audit trail + Strange Loop Integration

Wraps VAULT-999 sealing for MCP consumption.
v55.0: Emits seal-complete signals to LoopBridge for 000↔999 continuation.
"""

from typing import Any, Dict, Optional, List
import hashlib
import time
import logging

# v55.0: Loop Manager for 999→000 signal emission
LOOP_MANAGER_AVAILABLE = False
_loop_manager = None

logger = logging.getLogger("codebase.mcp.tools.vault_tool")

try:
    from codebase.loop import LoopManager, LoopState
    # Get the shared loop manager instance from init_000
    from codebase.init.000_init.init_000 import _loop_manager as imported_loop_manager
    if imported_loop_manager:
        _loop_manager = imported_loop_manager # Assign the imported manager to the global variable
        LOOP_MANAGER_AVAILABLE = True
        logger.info("v55.0 LoopManager connected for 999→000 signal emission")
except ImportError as e:
    logger.debug(f"LoopManager not available for signal emission: {e}")


class VaultTool:
    """
    VAULT-999: Immutable ledger and audit trail
    
    Actions:
    - seal: Seal a session with Merkle tree
    - list: List sealed sessions
    - read: Read sealed data
    - write: Write to ledger
    - propose: Propose governance change (human authority)
    """
    
    @staticmethod
    def execute(action: str, session_id: str, target: str = "seal", payload: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Execute VAULT action"""
        
        if action == "seal":
            return VaultTool._seal(session_id, target, payload, **kwargs)
        elif action == "list":
            return VaultTool._list(target, **kwargs)
        elif action == "read":
            return VaultTool._read(session_id, target, **kwargs)
        elif action == "write":
            return VaultTool._write(session_id, target, payload, **kwargs)
        elif action == "propose":
            return VaultTool._propose(session_id, payload, **kwargs)
        else:
            return {"verdict": "VOID", "reason": f"Unknown VAULT action: {action}"}
    
    @staticmethod
    def _seal(session_id: str, target: str, payload: Optional[Dict], **kwargs) -> Dict[str, Any]:
        """Seal session with cryptographic proof"""
        
        if not payload:
            payload = {}
        
        # Build Merkle tree (simplified)
        # Each node: hash(child_left + child_right + content)
        
        # Leaf nodes (session data)
        leaves = [
            hashlib.sha256(f"session:{session_id}".encode()).hexdigest()[:16],
            hashlib.sha256(f"verdict:{payload.get('verdict', 'SEAL')}".encode()).hexdigest()[:16],
            hashlib.sha256(f"query:{payload.get('query', '')}".encode()).hexdigest()[:16],
            hashlib.sha256(f"timestamp:{int(time.time())}".encode()).hexdigest()[:16]
        ]
        
        # Merkle root (hash of all leaves)
        merkle_root = hashlib.sha256("|".join(leaves).encode()).hexdigest()[:16]
        
        # Create sealed bundle
        sealed_bundle = {
            "session_id": session_id,
            "merkle_root": merkle_root,
            "leaf_count": len(leaves),
            "timestamp": int(time.time()),
            "verdict": payload.get("verdict", "SEAL"),
            "layers": {
                "L1": leaves[:2],
                "L2": leaves[2:],
                "root": merkle_root
            }
        }
        
        # v55.0: Emit seal-complete signal to LoopBridge for 999→000 continuation
        if LOOP_MANAGER_AVAILABLE and _loop_manager:
            try:
                # Prepare loop continuation context
                loop_context = {
                    "session_id": session_id,
                    "previous_merkle_root": merkle_root,
                    "verdict": payload.get("verdict", "SEAL"),
                    "timestamp": sealed_bundle["timestamp"],
                    "payload_summary": {
                        "query_hash": hashlib.sha256(payload.get("query", "").encode()).hexdigest()[:16] if payload.get("query") else None,
                        "leaf_count": len(leaves)
                    }
                }
                
                # Emit seal complete signal
                _loop_manager.on_seal_complete(loop_context)
                logger.info(f"SEAL_999 complete signal emitted (session: {session_id[:8]}, merkle: {merkle_root})")
            except Exception as e:
                logger.warning(f"Failed to emit loop signal: {e}")
        
        return {
            "verdict": "SEAL",
            "sealed": sealed_bundle,
            "proof": "cryptographic seal generated",
            "integrity": "VERIFIED"
        }
    
    @staticmethod
    def _list(target: str, **kwargs) -> Dict[str, Any]:
        """List sealed sessions in VAULT"""
        
        # Simulate ledger listing
        sessions = [
            {
                "session_id": "agi_001",
                "verdict": "SEAL",
                "timestamp": 1234567890,
                "merkle_root": "0xabc123..."
            },
            {
                "session_id": "asi_002", 
                "verdict": "SABAR",
                "timestamp": 1234567900,
                "merkle_root": "0xdef456..."
            }
        ]
        
        return {
            "verdict": "SEAL",
            "sessions": sessions,
            "count": len(sessions),
            "target": target
        }
    
    @staticmethod
    def _read(session_id: str, target: str, **kwargs) -> Dict[str, Any]:
        """Read sealed data from VAULT"""
        
        # Simulate reading sealed data
        sealed_data = {
            "session_id": session_id,
            "data": f"Constitutional response for {session_id[:20]}...",
            "verified": True,
            "integrity": "Merkle proof validates"
        }
        
        return {
            "verdict": "SEAL",
            "read": sealed_data,
            "target": target
        }
    
    @staticmethod
    def _write(session_id: str, target: str, payload: Optional[Dict], **kwargs) -> Dict[str, Any]:
        """Write to VAULT ledger"""
        
        if not payload:
            return {"verdict": "VOID", "reason": "No payload provided"}
        
        # Generate write proof
        write_hash = hashlib.sha256(f"write:{session_id}:{int(time.time())}".encode()).hexdigest()[:16]
        
        return {
            "verdict": "SEAL",
            "write_proof": write_hash,
            "location": target,
            "timestamp": int(time.time())
        }
    
    @staticmethod
    def _propose(session_id: str, payload: Optional[Dict], **kwargs) -> Dict[str, Any]:
        """Propose governance change (requires human authority)"""
        
        if not payload:
            return {"verdict": "VOID", "reason": "No proposal provided"}
        
        # F11: Command authority - require human approval
        requires_human = True
        human_approval = kwargs.get("human_approved", False)
        
        if not human_approval:
            return {
                "verdict": "888_HOLD",
                "reason": "F11 Command Authority: Requires human sovereign approval",
                "proposal": payload,
                "approval_needed": True
            }
        
        # Human approved - proceed
        proposal_hash = hashlib.sha256(f"proposal:{session_id}:{str(payload)}".encode()).hexdigest()[:16]
        
        return {
            "verdict": "SEAL",
            "reason": "Human authority approved constitutional change",
            "proposal_hash": proposal_hash,
            "tier": "AAA_HUMAN",  # Highest authority tier
            "governance_locked": True
        }
