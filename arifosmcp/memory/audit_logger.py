import json
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from .types import AuditEvent

class MemoryAuditLogger:
    def __init__(self, db_client=None):
        self.db = db_client

    async def log(self, 
                  event_type: str, 
                  actor_id: str, 
                  session_id: str, 
                  memory_id: Optional[UUID] = None, 
                  payload: Optional[Dict[str, Any]] = None):
        """Emit an immutable audit event."""
        event = AuditEvent(
            audit_id=uuid4(),
            memory_id=memory_id,
            event_type=event_type,
            actor_id=actor_id,
            session_id=session_id,
            payload=payload or {},
            created_at=datetime.utcnow()
        )
        
        # Mock DB Persistence
        # await self.db.execute("INSERT INTO memory_audit_log ...", event.__dict__)
        print(f"AUDIT [{event_type}]: actor={actor_id} session={session_id} memory={memory_id}")
        
        return event.audit_id

# Usage:
# MEMORY_INTAKE_RECEIVED
# MEMORY_INTAKE_DENIED
# MEMORY_CANDIDATE_EXTRACTED
# MEMORY_SOURCE_REJECTED
# MEMORY_WRITE_DENIED
# MEMORY_WRITE_SKIPPED
# MEMORY_WRITE_ALLOWED
# MEMORY_EMBED_QUEUED
# MEMORY_EMBED_READY
# MEMORY_EMBED_FAILED
# MEMORY_REVOKED
