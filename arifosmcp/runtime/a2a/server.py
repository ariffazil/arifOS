"""
A2A Server Implementation
=========================

Real A2A protocol server with constitutional governance integration.
Includes 888_HOLD cross-protocol broadcast via Redis + WebMCP WebSocket.

B3 hardening (2026-07-23):
  - L11 SCT machinery gates all task-owning endpoints.
  - Body actor IDs are display hints; SCT is the only authority.
  - Discovery routes stay public.
  - Synchronous /execute routes only on arif_judge SEAL.
  - status_callback_url is validated with a_rif/ssrf_guard before use.

ΔΩΨ | ARIF — Ditempa Bukan Diberi
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import StreamingResponse

from arifosmcp.runtime.a_rif.ssrf_guard import validate_url_safety
from arifosmcp.runtime.build import get_build_info
from arifosmcp.runtime.mcp_util import call_mcp_tool
from arifosmcp.runtime.optional_deps import aiofiles
from arifosmcp.runtime.sct import resolve_standing
from arifosmcp.server import mcp as _fast_mcp

from .agent_card_v2 import get_arifOS_agent_card, get_axos_summary
from .models import (
    AgentCard,
    Artifact,
    CancelTaskResponse,
    GetTaskResponse,
    SubmitTaskRequest,
    Task,
    TaskMessage,
    TaskState,
    TaskStatusUpdate,
)
from .seal_verifier import (
    SealVerificationRequest,
    get_seal_verifier,
)

# Cross-protocol 888_HOLD bridge
logger = logging.getLogger(__name__)


# ── B3 HARDENING CONSTANTS ─────────────────────────────────────────────
# A2A endpoints that gate task ownership. Discovery / health / seal-verify
# routes stay public and are NOT in this set.
A2A_TASK_ENDPOINTS = frozenset({"/task", "/execute", "/status", "/cancel", "/subscribe"})

# Verdict string returned by arif_judge that authorises routing to execution.
# Anything else (HOLD, VOID, SABAR, missing) is a hard fail — no truthy defaults.
ARIF_JUDGE_SEAL = "SEAL"

# Headers we accept for the SCT (priority: Authorization, then X-Session-Token).
_AUTH_HEADER = "authorization"
_SCT_HEADER = "x-session-token"
_BEARER_PREFIX = "bearer "


def _utcnow() -> datetime:
    return datetime.now(UTC)


# ── B3 HARDENING HELPERS ───────────────────────────────────────────────
def _extract_sct_token(authorization: str | None, x_session_token: str | None) -> str | None:
    """Pull SCT from either Authorization: Bearer … or X-Session-Token."""
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == _BEARER_PREFIX.rstrip() and value.strip():
            return value.strip()
        # Tolerate raw token in Authorization (no scheme).
        if not scheme and value.strip():
            return authorization.strip()
    if x_session_token:
        return x_session_token.strip() or None
    return None


def _resolve_actor_from_request(
    *,
    authorization: str | None = None,
    x_session_token: str | None = None,
) -> tuple[str, str | None, str]:
    """
    L11 SCT authentication for A2A endpoints.

    Returns (actor_id, session_id, session_token). Raises HTTPException(401)
    on any failure. Body actor IDs are NOT consulted — the SCT is the only
    authority.
    """
    token = _extract_sct_token(authorization, x_session_token)
    if not token:
        raise HTTPException(
            status_code=401,
            detail=(
                "L11 AUTH: missing session token "
                "(Authorization: Bearer <sct> or X-Session-Token required)"
            ),
        )

    standing = resolve_standing(session_token=token, allow_store=False)
    if not standing.valid:
        raise HTTPException(
            status_code=401,
            detail=f"L11 AUTH: {standing.reason}",
        )
    actor_id = standing.actor_id or "anonymous"
    return actor_id, standing.session_id, standing.session_token or token


def _validate_callback_url(url: str | None) -> str | None:
    """
    SSRF-safe callback URL gate. Returns the URL if safe, None if absent,
    raises HTTPException(400) if unsafe.
    """
    if not url:
        return None
    verdict = validate_url_safety(url)
    if not verdict.get("safe"):
        flags = verdict.get("risk_flags") or ["unsafe"]
        reason = verdict.get("reason") or "callback URL failed SSRF safety check"
        raise HTTPException(
            status_code=400,
            detail=f"L1 AMANAH: unsafe status_callback_url ({','.join(flags)}): {reason}",
        )
    return url


def _parse_judge_verdict(judge_result: dict[str, Any]) -> str:
    """
    Extract the verdict string from a wrapped FastMCP arif_judge result.
    Returns 'VOID' on any parse failure (no truthy default).
    """
    import json as _json

    content = judge_result.get("content")
    if isinstance(content, list) and content:
        first = content[0] or {}
        if isinstance(first, dict):
            text = first.get("text", "")
            if isinstance(text, str) and text:
                try:
                    payload = _json.loads(text)
                    if isinstance(payload, dict):
                        v = payload.get("verdict")
                        if isinstance(v, str) and v:
                            return v
                except (ValueError, _json.JSONDecodeError):
                    pass
    # Also accept already-normalised dicts.
    if isinstance(judge_result.get("verdict"), str):
        return judge_result["verdict"]
    return "VOID"


class A2ATaskManager:
    """Manages A2A task lifecycle with 888_HOLD cross-protocol broadcast."""

    def __init__(self, mcp_server: Any):
        # Use the global FastMCP from server.py, not the Starlette app
        self.mcp = _fast_mcp
        self.tasks: dict[str, Task] = {}
        self._lock = asyncio.Lock()
        self._hold_bridge = None

    async def create_task(
        self,
        request: SubmitTaskRequest,
        *,
        verified_actor: str,
        verified_session_id: str | None = None,
        verified_session_token: str | None = None,
    ) -> Task:
        """Create a task owned by the SCT-verified actor.

        ``request.client_agent_id`` is a display hint only. Every caller must
        pass the actor resolved from L11/SCT authentication.
        """
        task_id = f"a2a-{uuid.uuid4().hex[:12]}"

        # Extract query from messages
        for msg in request.messages:
            if msg.role == "user":
                break

        # Callback URL must pass the SSRF guard before we accept the task.
        callback_url = _validate_callback_url(request.status_callback_url)
        authoritative_actor = verified_actor

        # Initialize constitutional session via MCP, using the authoritative actor.
        session_id = verified_session_id
        try:
            init_params: dict[str, Any] = {
                "mode": "init",
                "actor_id": authoritative_actor,
            }
            if verified_session_token:
                init_params["session_token"] = verified_session_token
            if session_id:
                init_params["session_id"] = session_id

            init_result = await self._call_mcp_tool("arif_init", init_params)

            if init_result.get("verdict") == "SEAL":
                session_id = init_result.get("session_id") or session_id
        except Exception as e:
            print(f"[A2A] Session init warning: {e}", file=sys.stderr)

        task = Task(
            id=task_id,
            client_agent_id=request.client_agent_id,
            creator_actor_id=verified_actor,
            session_id=session_id,
            messages=request.messages,
            skill_id=request.skill_id,
            parameters=request.parameters,
            status_callback_url=callback_url,
        )

        async with self._lock:
            self.tasks[task_id] = task

        # Start task execution in background
        asyncio.create_task(self._execute_task(task_id))

        return task

    async def get_task(self, task_id: str) -> Task | None:
        """Get task by ID."""
        async with self._lock:
            return self.tasks.get(task_id)

    async def cancel_task(self, task_id: str) -> CancelTaskResponse:
        """Cancel a task."""
        async with self._lock:
            task = self.tasks.get(task_id)
            if not task:
                return CancelTaskResponse(success=False, message=f"Task {task_id} not found")

            if task.state in [
                TaskState.COMPLETED,
                TaskState.FAILED,
                TaskState.CANCELLED,
            ]:
                return CancelTaskResponse(
                    success=False,
                    message=f"Task already in terminal state: {task.state}",
                )

            task.state = TaskState.CANCELLED
            task.updated_at = _utcnow()

            return CancelTaskResponse(success=True, message="Task cancelled", task=task)

    async def _execute_task(self, task_id: str):
        """Execute task with constitutional governance."""
        task = await self.get_task(task_id)
        if not task:
            return

        # B3: author of the execution is the verified creator, not the
        # body-supplied client_agent_id. Owner of authority is the SCT actor.
        execution_actor = task.creator_actor_id or task.client_agent_id

        try:
            # Update to working state
            await self._update_task_state(
                task_id, TaskState.WORKING, "Starting constitutional review..."
            )

            # Extract query
            query = ""
            for msg in task.messages:
                if msg.role == "user":
                    query = msg.content
                    break

            # Step 1: Constitutional Review (asi_critique)
            await self._update_task_state(
                task_id, TaskState.WORKING, "Running constitutional critique..."
            )

            _critique_result = await self._call_mcp_tool(
                "arif_critique",
                {
                    "mode": "critique",
                    "target": f"A2A task [{task.id}]: {query[:200]}",
                    "session_id": task.session_id,
                    "actor_id": execution_actor,
                },
            )

            # Step 2: APEX Judgment
            await self._update_task_state(task_id, TaskState.WORKING, "Awaiting APEX judgment...")

            judge_result = await self._call_mcp_tool(
                "arif_judge",
                {
                    "mode": "judge",
                    "candidate": f"A2A task execution: {query[:200]}",
                    "session_id": task.session_id,
                    "actor_id": execution_actor,
                },
            )

            # Parse verdict from the nested MCP result structure
            # judge_result = {"content": [{"type": "text", "text": "{\"verdict\": \"SEAL\", ...}"}]}
            import json as _json

            _raw = judge_result.get("content", [{}])[0].get("text", "{}")
            try:
                _judge_payload = _json.loads(_raw)
            except Exception:
                _judge_payload = {}
            verdict = _judge_payload.get("verdict", "VOID")
            task.verdict = verdict

            if verdict == "VOID":
                task.state = TaskState.FAILED
                task.error_message = "Constitutional violation detected"
                task.violations = _judge_payload.get("violations", [])

            elif verdict == "888_HOLD":
                # ═══════════════════════════════════════════════════════════
                # 888_HOLD CROSS-PROTOCOL HANDOFF
                # ═══════════════════════════════════════════════════════════

                task.state = TaskState.INPUT_REQUIRED

                # Import and initialize cross-protocol bridge
                try:
                    from arifosmcp.runtime.cross_protocol_bridge import (
                        HoldEvent,
                        get_hold_bridge,
                    )

                    # Create immutable hold event
                    hold_event = HoldEvent(
                        hold_id=f"HOLD-A2A-{task.id}",
                        source_protocol="a2a",
                        action_type=task.skill_id or "general_execution",
                        reason="L13 Sovereign: Human ratification required",
                        risk_level="high",
                        floor_violations=["F1", "L13"],
                        session_id=task.session_id or "unknown",
                        actor_id=task.client_agent_id,
                    )

                    # Build action payload for F1 hash
                    action_payload = {
                        "task_id": task.id,
                        "client_agent_id": task.client_agent_id,
                        "skill_id": task.skill_id,
                        "mode": "route",
                        "task": query,
                        "parameters": task.parameters,
                    }

                    # PUBLISH to Redis → WebMCP WebSocket
                    bridge = await get_hold_bridge()
                    pre_hash = await bridge.publish_hold(hold_event, action_payload)

                    # Log to VAULT999 with pre-execution hash (F1 AMANAH)
                    await self._log_hold_to_vault(task, hold_event, pre_hash, action_payload)

                    # Update task with hold metadata
                    task.hold_id = hold_event.hold_id
                    task.pre_execution_hash = pre_hash

                    task.messages.append(
                        TaskMessage(
                            role="system",
                            content=(
                                f"⏸️ 888_HOLD TRIGGERED\n"
                                f"Hold ID: {hold_event.hold_id}\n"
                                f"Pre-hash: {pre_hash[:16]}...\n"
                                f"Review at: https://arifosmcp.arif-fazil.com/hold/{hold_event.hold_id}"
                            ),
                        )
                    )

                except Exception as bridge_error:
                    logger.error(f"Failed to broadcast 888_HOLD: {bridge_error}")
                    # Fallback: still create hold but without broadcast
                    task.messages.append(
                        TaskMessage(
                            role="system",
                            content=(
                                "Task requires human ratification (L13 Sovereign). "
                                "Please approve via arifOS dashboard."
                            ),
                        )
                    )

            elif verdict == "SEAL":
                # Execute the actual task
                await self._update_task_state(task_id, TaskState.WORKING, "Executing with SEAL...")

                execution_result = await self._call_mcp_tool(
                    "arif_kernel_route",
                    {
                        "mode": "route",
                        "task": query,
                        "session_id": task.session_id,
                    },
                )

                # Add result as artifact
                task.artifacts.append(
                    Artifact(
                        name="execution_result",
                        content_type="application/json",
                        content=json.dumps(execution_result, indent=2),
                    )
                )

                task.state = TaskState.COMPLETED
                task.completed_at = _utcnow()

            else:
                task.state = TaskState.FAILED
                task.error_message = f"Unexpected verdict: {verdict}"

            task.updated_at = _utcnow()

            # Send callback if configured
            if task.status_callback_url:
                await self._send_callback(task)

        except Exception as e:
            task.state = TaskState.FAILED
            task.error_message = str(e)
            task.updated_at = _utcnow()
            print(f"[A2A] Task execution error: {e}", file=sys.stderr)

    async def _update_task_state(self, task_id: str, state: TaskState, message: str = None):
        """Update task state."""
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].state = state
                self.tasks[task_id].updated_at = _utcnow()
                if message:
                    self.tasks[task_id].messages.append(TaskMessage(role="system", content=message))

    async def _call_mcp_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Call the MCP tool through the internal FastMCP kernel."""
        return await call_mcp_tool(self.mcp, tool_name, params)

    async def _send_callback(self, task: Task):
        """Send status callback to client agent."""
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    task.status_callback_url,
                    json={
                        "task_id": task.id,
                        "state": task.state,
                        "verdict": task.verdict,
                    },
                    timeout=10.0,
                )
        except Exception as e:
            print(f"[A2A] Callback failed: {e}", file=sys.stderr)

    async def _log_hold_to_vault(
        self,
        task: Task,
        hold_event,
        pre_hash: str,
        action_payload: dict,
    ):
        """
        F1 AMANAH: Log pre-execution intent to VAULT999.

        This ensures reversibility proof exists even if connection drops.
        """
        vault_entry = {
            "timestamp": _utcnow().isoformat(),
            "action": "888_HOLD_INITIATED",
            "source_protocol": "a2a",
            "cross_protocol_handoff": {
                "from_protocol": "a2a",
                "to_protocol": "webmcp",
                "bridge_method": "redis_pubsub",
            },
            "f1_amanah": {
                "pre_execution_hash": pre_hash,
                "connection_drop_safe": True,
            },
            "hold_context": {
                "hold_id": hold_event.hold_id,
                "task_id": task.id,
                "session_id": task.session_id,
                "client_agent_id": task.client_agent_id,
                "action_type": task.skill_id or "general_execution",
                "risk_level": "high",
                "floor_violations": ["F1", "L13"],
            },
            "payload_hash": hashlib.sha256(
                json.dumps(action_payload, sort_keys=True).encode()
            ).hexdigest(),
            "verdict": "888_HOLD",
            "stage": "A2A_CROSS_PROTOCOL_HANDOFF",
        }

        # Write to VAULT999 (async append to JSONL)
        vault_path = Path("VAULT999/a2a_holds.jsonl")
        vault_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            async with aiofiles.open(vault_path, "a") as f:
                await f.write(json.dumps(vault_entry) + "\n")
            logger.info(f"[F1 AMANAH] 888_HOLD logged to VAULT999: {hold_event.hold_id}")
        except Exception as e:
            logger.error(f"[F1 AMANAH] Failed to log to VAULT999: {e}")

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks (for debugging)."""
        return list(self.tasks.values())


class A2AServer:
    """
    A2A Protocol Server with constitutional governance.

    Implements Google's A2A specification with arifOS's 13-floor governance.
    """

    def __init__(self, mcp_server: Any):
        self.mcp = mcp_server
        self.task_manager = A2ATaskManager(mcp_server)
        self.build_info = get_build_info()
        self.app = FastAPI(
            title="arifOS A2A Server",
            description="Agent-to-Agent protocol with constitutional governance",
            version=self.build_info["version"],
        )
        self._setup_routes()

    def _setup_routes(self):
        """Setup A2A protocol routes."""

        # Agent Card Discovery (/.well-known/agent.json)
        # PUBLIC per B3 — discovery stays open.
        @self.app.get("/.well-known/agent.json")
        async def agent_card():
            """
            A2A Agent Card - Published for agent discovery.

            Other agents discover arifOS capabilities via this endpoint.
            """
            card = AgentCard()
            return card.model_dump()

        # Submit Task — requires SCT (B3: body actor_id is NOT authority).
        @self.app.post("/task")
        async def submit_task(
            request: SubmitTaskRequest,
            authorization: str | None = Header(default=None),
            x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
        ):
            """
            Submit a new task to arifOS.

            Task will be processed through constitutional governance (F1-L13).
            Authentication requires a valid SCT (Authorization: Bearer <sct>
            or X-Session-Token header). The body actor IDs are display hints;
            the verified SCT actor owns the task.
            """
            actor_id, session_id, session_token = _resolve_actor_from_request(
                authorization=authorization,
                x_session_token=x_session_token,
            )

            task = await self.task_manager.create_task(
                request,
                verified_actor=actor_id,
                verified_session_id=session_id,
                verified_session_token=session_token,
            )
            return {
                "task_id": task.id,
                "state": task.state,
                "session_id": task.session_id,
                "creator_actor_id": task.creator_actor_id,
                "message": "Task submitted for constitutional review",
            }

        # Trinity Probe: Execute Task Synchronously — SCT-gated, SEAL-only routing.
        @self.app.post("/execute")
        async def execute_task(
            request: Request,
            authorization: str | None = Header(default=None),
            x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
        ):
            """
            Synchronously execute a governed task (Phase 3: The Trinity Probe).
            Supports 'governed_execution' mode for immediate AGI/ASI loop validation.

            B3 hardening:
              - SCT is required; the body's ``auth_context.actor_id`` is ignored.
              - arif_judge must return SEAL for routing to arif_kernel_route to fire.
                HOLD / VOID / SABAR / parse-failure => no execution, no truthy default.
            """
            actor_id, session_id, session_token = _resolve_actor_from_request(
                authorization=authorization,
                x_session_token=x_session_token,
            )

            data = await request.json()
            query = data.get("query", "No query provided")
            mode = data.get("mode", "governed_execution")
            # NOTE: data.get("auth_context", {}).get("actor_id") is deliberately
            # NOT consulted. The verified SCT actor is the only authority.

            # Step 1: Initialize constitutional anchor (use verified actor).
            init_params: dict[str, Any] = {
                "mode": "init",
                "intent": query,
                "actor_id": actor_id,
            }
            if session_token:
                init_params["session_token"] = session_token
            if session_id:
                init_params["session_id"] = session_id

            init_result = await self.task_manager._call_mcp_tool("arif_init", init_params)
            session_id = init_result.get("session_id") or session_id or "global"

            # Step 2: Call arif_judge. Route ONLY on SEAL — no truthy defaults.
            judge_params: dict[str, Any] = {
                "mode": "judge",
                "candidate": f"A2A execute (mode={mode}): {query[:200]}",
                "session_id": session_id,
                "actor_id": actor_id,
            }
            if session_token:
                judge_params["session_token"] = session_token

            judge_result = await self.task_manager._call_mcp_tool("arif_judge", judge_params)
            verdict = _parse_judge_verdict(judge_result)

            if verdict != ARIF_JUDGE_SEAL:
                # No execution on HOLD/VOID/SABAR/parse-failure. 409: verdict
                # did not authorise routing. Body includes the actual verdict
                # for observability.
                raise HTTPException(
                    status_code=409,
                    detail={
                        "code": "JUDGE_NO_SEAL",
                        "verdict": verdict,
                        "message": (
                            "arif_judge did not return SEAL; execution not routed "
                            "(no truthy defaults)."
                        ),
                    },
                )

            # Step 3: SEAL received — route to arif_kernel_route.
            execution_result = await self.task_manager._call_mcp_tool(
                "arif_kernel_route",
                {
                    "mode": "route",
                    "task": query,
                    "session_id": session_id,
                    "context": f"A2A direct-execution probe (actor={actor_id}, mode={mode})",
                },
            )

            return {
                "ok": bool(execution_result.get("ok", False)),
                "verdict": ARIF_JUDGE_SEAL,
                "status": execution_result.get("status", "SUCCESS"),
                "session_id": session_id,
                "creator_actor_id": actor_id,
                "payload": execution_result.get("payload", {}),
                "meta": {
                    "release": f"v{self.build_info['version']}",
                    "protocol": "A2A/Trinity-Probe",
                    "governance": "F1-L13 LOCK",
                },
            }

        # Get Task Status — requires SCT + task ownership (B3).
        @self.app.get("/status/{task_id}")
        async def get_task(
            task_id: str,
            authorization: str | None = Header(default=None),
            x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
        ):
            """Get current status of a task owned by the authenticated actor."""
            actor_id, _session_id, _session_token = _resolve_actor_from_request(
                authorization=authorization,
                x_session_token=x_session_token,
            )
            task = await self.task_manager.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            if task.creator_actor_id and task.creator_actor_id != actor_id:
                raise HTTPException(
                    status_code=403,
                    detail="L11 AUTH: actor does not own this task",
                )
            return GetTaskResponse(task=task).model_dump()

        # Cancel Task — requires SCT + task ownership (B3).
        @self.app.post("/cancel/{task_id}")
        async def cancel_task(
            task_id: str,
            authorization: str | None = Header(default=None),
            x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
        ):
            """Cancel a running or pending task owned by the authenticated actor."""
            actor_id, _session_id, _session_token = _resolve_actor_from_request(
                authorization=authorization,
                x_session_token=x_session_token,
            )
            task = await self.task_manager.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            if task.creator_actor_id and task.creator_actor_id != actor_id:
                raise HTTPException(
                    status_code=403,
                    detail="L11 AUTH: actor does not own this task",
                )
            result = await self.task_manager.cancel_task(task_id)
            return result.model_dump()

        # Subscribe to Task Updates (SSE) — requires SCT + task ownership (B3).
        @self.app.get("/subscribe/{task_id}")
        async def subscribe_task(
            task_id: str,
            request: Request,
            authorization: str | None = Header(default=None),
            x_session_token: str | None = Header(default=None, alias="X-Session-Token"),
        ):
            """
            Subscribe to real-time task updates via Server-Sent Events.

            Stream updates as task progresses through constitutional review.
            Only the verified owner of the task may subscribe.
            """
            actor_id, _session_id, _session_token = _resolve_actor_from_request(
                authorization=authorization,
                x_session_token=x_session_token,
            )
            task = await self.task_manager.get_task(task_id)
            if not task:
                raise HTTPException(status_code=404, detail="Task not found")
            if task.creator_actor_id and task.creator_actor_id != actor_id:
                raise HTTPException(
                    status_code=403,
                    detail="L11 AUTH: actor does not own this task",
                )

            async def event_generator():
                last_state = None

                while True:
                    task = await self.task_manager.get_task(task_id)
                    if not task:
                        yield f"event: error\ndata: {json.dumps({'error': 'Task not found'})}\n\n"
                        break

                    # Send update if state changed
                    if task.state != last_state:
                        last_state = task.state
                        update = TaskStatusUpdate(
                            task_id=task_id,
                            state=task.state,
                            message=f"Task is now {task.state}",
                        )
                        yield f"event: status\ndata: {update.model_dump_json()}\n\n"

                    # End if terminal state
                    if task.state in [
                        TaskState.COMPLETED,
                        TaskState.FAILED,
                        TaskState.CANCELLED,
                    ]:
                        yield (
                            f"event: complete\n"
                            f"data: {json.dumps({'task_id': task_id, 'state': task.state})}\n\n"
                        )
                        break

                    await asyncio.sleep(1)

            return StreamingResponse(
                event_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                },
            )

        # List all tasks (debug/admin)
        @self.app.get("/tasks")
        async def list_tasks():
            """List all tasks (admin/debug endpoint)."""
            tasks = self.task_manager.get_all_tasks()
            return {
                "count": len(tasks),
                "tasks": [t.model_dump() for t in tasks[-10:]],  # Last 10
            }

        # Health check
        @self.app.get("/health")
        async def health():
            """A2A health check."""
            return {
                "status": "healthy",
                "protocol": "A2A",
                "version": self.build_info["version"],
                "constitutional_floors": 13,
                "motto": "Ditempa Bukan Diberi",
            }

        # ── Agent Card v2.0 ────────────────────────────────────────────────────

        @self.app.get("/.well-known/agent-card.json")
        async def agent_card_v2():
            """arifOS Agent Card v2.0 — full 6-axis skill registry."""
            card = get_arifOS_agent_card()
            return card.model_dump()

        @self.app.get("/agent-card")
        async def agent_card_summary():
            """Compact summary for quick discovery."""
            return get_axos_summary()

        @self.app.get("/agent-card/skills")
        async def agent_card_skills():
            """All 23 skills across 6 axes."""
            card = get_arifOS_agent_card()
            return {
                "total": len(card.skills),
                "by_axis": {
                    ax: [s.model_dump() for s in card.skills if s.axis == ax]
                    for ax in ["P", "T", "V", "G", "E", "M"]
                },
                "entry_point": card.routing.entry_point,
            }

        # ── Seal Verification Endpoints ──────────────────────────────────────

        @self.app.post("/seal/verify")
        async def verify_seal(request: SealVerificationRequest):
            """Verify a SEAL verdict is valid and vault-anchored."""
            verifier = get_seal_verifier()
            return verifier.verify_seal(request).model_dump()

        @self.app.get("/seal/verify/{session_id}")
        async def verify_seal_by_session(
            session_id: str, verdict: str = "SEAL", state_hash: str | None = None
        ):
            """Verify SEAL by session ID (GET variant)."""
            verifier = get_seal_verifier()
            result = verifier.verify_seal(
                SealVerificationRequest(
                    session_id=session_id, verdict=verdict, state_hash=state_hash
                )
            )
            return result.model_dump()

        @self.app.get("/meta/omega")
        async def orthogonality_status():
            """Get current Ω_ortho from M01 Correlation Auditor."""
            verifier = get_seal_verifier()
            return verifier.get_orthogonality().model_dump()

        @self.app.get("/meta/omega/violations")
        async def orthogonality_violations():
            """Get detailed Ω_ortho violations."""
            from arifosmcp.runtime.auditor import get_auditor

            auditor = get_auditor()
            report = auditor.compute_orthogonality()
            return {
                "omega_ortho": report.omega_ortho,
                "threshold": auditor.threshold,
                "violations": report.violations,
                "agents_in_scope": report.agents_in_scope,
                "trace": report.trace,
            }

        @self.app.get("/well/state")
        async def well_state():
            """Get current WELL operator state."""
            verifier = get_seal_verifier()
            return verifier.get_well_state().model_dump()


_a2a_server_singleton: A2AServer | None = None


def create_a2a_server(mcp_server: Any) -> A2AServer:
    """Factory function to create A2A server (singleton per process)."""
    global _a2a_server_singleton
    if _a2a_server_singleton is None:
        _a2a_server_singleton = A2AServer(mcp_server)
    return _a2a_server_singleton
