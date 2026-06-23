"""
NATS Event Bus — Inter-Organ Mesh Transport for arifOS Federation
═══════════════════════════════════════════════════════════════════

Upgraded 2026-06-14: from telemetry-only to primary inter-organ mesh.
The NATS event bus is now the nervous system of the federation — carrying
not just telemetry events but request/response, feedback loops, gradient
signals, and governance pipeline verdicts across all organs.

ARCHITECTURE:
  Level 1 (Telemetry — original)  arifOS.verdicts, arifOS.heartbeat, arifOS.alerts
  Level 2 (Governance — upgrade) arifOS.governance.gate.* — pipeline verdicts
  Level 3 (Inter-Organ — new)    arifOS.requests.<organ>, arifOS.responses.<organ>
  Level 4 (Feedback — new)       arifOS.feedback.<signal> — cross-organ loop signals
  Level 5 (Gradient — new)       arifOS.gradient.<dimension> — constitutional cost

JETSTREAM STREAMS (durable, replayable):
  GOVERNANCE   — subjects: arifos.governance.>
  INTER_ORGAN  — subjects: arifos.requests.>, arifos.responses.>
  FEEDBACK     — subjects: arifos.feedback.>
  GRADIENT     — subjects: arifos.gradient.>

F1 AMANAH: NATS is mesh transport, not authority. arifOS kernel remains
the sole constitutional authority. Mesh failure must never block governance.

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

try:
    import nats
    from nats.js import JetStreamContext
    from nats.js.api import (
        AckPolicy,
        ConsumerConfig,
        DeliverPolicy,
        DiscardPolicy,
        ReplayPolicy,
        RetentionPolicy,
        StorageType,
        StreamConfig,
    )

    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False

logger = logging.getLogger("arifosmcp.nats_event_bus")

# ═══════════════════════════════════════════════════════════════════════════════
# SUBJECT HIERARCHY — the federation nervous system
# ═══════════════════════════════════════════════════════════════════════════════

# ── Level 1: Telemetry (original — backward compatible) ──
SUBJECT_VERDICTS = "arifOS.verdicts"
SUBJECT_HEARTBEAT = "arifOS.heartbeat"
SUBJECT_ALERTS = "arifOS.alerts"
SUBJECT_EVIDENCE = "arifOS.evidence"
SUBJECT_FLOORS = "arifOS.floors"

# ── Level 2: Governance Pipeline ──
SUBJECT_GOVERNANCE_PREFIX = "arifos.governance.gate"
SUBJECT_GOVERNANCE_PASS = "arifos.governance.gate.8.pass"
SUBJECT_GOVERNANCE_HOLD = "arifos.governance.gate.*.hold"
SUBJECT_GOVERNANCE_ALL = "arifos.governance.>"

# ── Level 3: Inter-Organ Request/Response ──
SUBJECT_REQUESTS_PREFIX = "arifos.requests"  # arifos.requests.<organ>
SUBJECT_RESPONSES_PREFIX = "arifos.responses"  # arifos.responses.<organ>
SUBJECT_BROADCAST = "arifos.broadcast"  # all organs

# ── Level 4: Feedback Loop Signals ──
SUBJECT_FEEDBACK_PREFIX = "arifos.feedback"  # arifos.feedback.<signal>
SUBJECT_FEEDBACK_PROCEED = "arifos.feedback.PROCEED"
SUBJECT_FEEDBACK_REVISE_LOCAL = "arifos.feedback.REVISE_LOCAL"
SUBJECT_FEEDBACK_REVISE_GLOBAL = "arifos.feedback.REVISE_GLOBAL"
SUBJECT_FEEDBACK_BRANCH = "arifos.feedback.BRANCH"
SUBJECT_FEEDBACK_BACKTRACK = "arifos.feedback.BACKTRACK"
SUBJECT_FEEDBACK_HOLD = "arifos.feedback.HOLD"
SUBJECT_FEEDBACK_ALL = "arifos.feedback.>"

# ── Level 5: Gradient Descent Signals (Constitutional Cost Function) ──
SUBJECT_GRADIENT_PREFIX = "arifos.gradient"
SUBJECT_GRADIENT_CONSTITUTION = "arifos.gradient.constitution"  # α term
SUBJECT_GRADIENT_PHYSICS = "arifos.gradient.physics"  # β term
SUBJECT_GRADIENT_CAPITAL = "arifos.gradient.capital"  # γ term
SUBJECT_GRADIENT_SUBSTRATE = "arifos.gradient.substrate"  # δ term
SUBJECT_GRADIENT_CONTINUITY = "arifos.gradient.continuity"  # ε term
SUBJECT_GRADIENT_DIGNITY = "arifos.gradient.dignity"  # ζ term
SUBJECT_GRADIENT_ALL = "arifos.gradient.>"

# ── E7 Principal Paradox subjects ──
SUBJECT_E7_AUTONOMY = "arifos.e7.autonomy"  # autonomy ceiling changes
SUBJECT_E7_OVERRIDE = "arifos.e7.override"  # principal override events
SUBJECT_E7_ATTESTATION = "arifos.e7.attestation"  # attestation receipts

# ── /000 + /999 Public Surface subjects ──
SUBJECT_PUBLIC_000 = "arifos.public.000"  # authority boundary surface
SUBJECT_PUBLIC_999 = "arifos.public.999"  # execution proof surface

# ── Level 6: Intelligence Diffusion (new — kernel state broadcast to all organs) ──
SUBJECT_INTELLIGENCE_FLOORS = "arifos.intelligence.floors"  # F1-F13 state snapshot
SUBJECT_INTELLIGENCE_ENTROPY = "arifos.intelligence.entropy"  # pipeline ΔS
SUBJECT_INTELLIGENCE_VERDICT = "arifos.intelligence.verdict"  # 888 verdict broadcast
SUBJECT_INTELLIGENCE_LEASE = "arifos.intelligence.lease"  # active lease changes
SUBJECT_INTELLIGENCE_ALL = "arifos.intelligence.>"


# ═══════════════════════════════════════════════════════════════════════════════
# ALL SUBJECTS — for stream configuration
# ═══════════════════════════════════════════════════════════════════════════════

ALL_GOVERNANCE_SUBJECTS = [
    "arifos.governance.>",
]

ALL_INTER_ORGAN_SUBJECTS = [
    "arifos.requests.>",
    "arifos.responses.>",
    "arifos.broadcast",
]

ALL_FEEDBACK_SUBJECTS = [
    "arifos.feedback.>",
]

ALL_GRADIENT_SUBJECTS = [
    "arifos.gradient.>",
]

ALL_E7_SUBJECTS = [
    "arifos.e7.>",
]


# ═══════════════════════════════════════════════════════════════════════════════
# JETSTREAM STREAM CONFIGURATIONS (durable, replayable)
# ═══════════════════════════════════════════════════════════════════════════════

STREAM_CONFIGS: dict[str, dict[str, Any]] = {
    "GOVERNANCE": {
        "subjects": ALL_GOVERNANCE_SUBJECTS,
        "retention": "limits",
        "max_msgs": 10_000,
        "max_bytes": 256 * 1024 * 1024,  # 256 MB
        "discard": "old",
        "storage": "file",
        "description": "Governance pipeline verdicts — every gate crossing",
    },
    "INTER_ORGAN": {
        "subjects": ALL_INTER_ORGAN_SUBJECTS,
        "retention": "limits",
        "max_msgs": 50_000,
        "max_bytes": 512 * 1024 * 1024,  # 512 MB
        "discard": "old",
        "storage": "file",
        "description": "Inter-organ request/response mesh — federation nervous system",
    },
    "FEEDBACK": {
        "subjects": ALL_FEEDBACK_SUBJECTS,
        "retention": "limits",
        "max_msgs": 5_000,
        "max_bytes": 64 * 1024 * 1024,  # 64 MB
        "discard": "old",
        "storage": "file",
        "description": "Cross-organ feedback loop signals — plan→act→observe→evaluate",
    },
    "GRADIENT": {
        "subjects": ALL_GRADIENT_SUBJECTS,
        "retention": "limits",
        "max_msgs": 5_000,
        "max_bytes": 64 * 1024 * 1024,  # 64 MB
        "discard": "old",
        "storage": "file",
        "description": "Constitutional cost function gradient signals — 6 dimensions",
    },
    "E7_AUTONOMY": {
        "subjects": ALL_E7_SUBJECTS,
        "retention": "limits",
        "max_msgs": 10_000,
        "max_bytes": 128 * 1024 * 1024,  # 128 MB
        "discard": "old",
        "storage": "file",
        "description": "E7 Principal Paradox — autonomy ceiling, overrides, attestations",
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# FEDERATION ORGAN REGISTRY
# ═══════════════════════════════════════════════════════════════════════════════

FEDERATION_ORGANS = ["arifOS", "GEOX", "WEALTH", "WELL", "MIND", "MEMORY", "AAA"]


def organ_subject(organ: str, suffix: str = "") -> str:
    """Build a canonical organ subject: arifos.requests.GEOX, etc."""
    organ_norm = organ.upper().replace("-", "_")
    return f"arifos.{suffix}.{organ_norm}" if suffix else f"arifos.{organ_norm}"


# ═══════════════════════════════════════════════════════════════════════════════
# NATS EVENT BUS — upgraded to inter-organ mesh
# ═══════════════════════════════════════════════════════════════════════════════


class NATSEventBus:
    """
    arifOS event publisher and inter-organ mesh transport.

    Level 1 (Telemetry):  publish_verdict, publish_heartbeat, publish_alert
    Level 2 (Governance): publish_gate_verdict, publish_pipeline_result
    Level 3 (Inter-Organ): request_organ, respond_to, broadcast_to_federation
    Level 4 (Feedback):    publish_feedback_signal, subscribe_feedback
    Level 5 (Gradient):    publish_gradient, subscribe_gradient
    """

    _instance: NATSEventBus | None = None
    _nc: Any | None = None
    _js: Any | None = None  # JetStream context
    _streams_initialized: bool = False
    _subscriptions: dict[str, Any] = {}  # subject → subscription handle

    def __new__(cls) -> NATSEventBus:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def connected(self) -> bool:
        return self._nc is not None and self._nc.is_connected

    @property
    def jetstream_available(self) -> bool:
        return self._js is not None

    # ═══════════════════════════════════════════════════════════════════════
    # CONNECTION LIFECYCLE
    # ═══════════════════════════════════════════════════════════════════════

    async def connect(
        self,
        nats_url: str = "nats://127.0.0.1:4222",
        init_jetstream: bool = True,
    ) -> bool:
        """Connect to NATS server and initialize JetStream streams."""
        if not NATS_AVAILABLE:
            logger.warning("nats-py not installed, event bus disabled")
            return False

        try:
            self._nc = await nats.connect(
                nats_url,
                name="arifOS-kernel",
                connect_timeout=10,
                ping_interval=30,
                max_reconnect_attempts=-1,  # infinite reconnect
            )
            logger.info(f"NATS connected to {nats_url} as arifOS-kernel")

            if init_jetstream:
                await self._init_jetstream()

            return True
        except Exception as e:
            logger.error(f"NATS connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from NATS, draining subscriptions."""
        if self._nc:
            # Drain all subscriptions
            for subj, sub in list(self._subscriptions.items()):
                try:
                    await sub.unsubscribe()
                except Exception:
                    pass
            self._subscriptions.clear()

            await self._nc.drain()
            await self._nc.close()
            self._nc = None
            self._js = None
            self._streams_initialized = False
            logger.info("NATS disconnected")

    async def _init_jetstream(self) -> bool:
        """Initialize JetStream context and create durable streams."""
        if not self._nc:
            return False

        try:
            self._js = self._nc.jetstream()
            logger.info("JetStream context acquired")

            # Create/verify all streams
            for stream_name, config in STREAM_CONFIGS.items():
                try:
                    await self._js.add_stream(
                        StreamConfig(
                            name=stream_name,
                            subjects=config["subjects"],
                            retention=RetentionPolicy.LIMITS,
                            max_msgs=config["max_msgs"],
                            max_bytes=config["max_bytes"],
                            discard=DiscardPolicy.OLD,
                            storage=StorageType.FILE,
                            description=config.get("description", ""),
                        )
                    )
                    logger.info(f"JetStream stream '{stream_name}' ready")
                except Exception:
                    # Stream may already exist — try to update
                    try:
                        await self._js.update_stream(
                            StreamConfig(
                                name=stream_name,
                                subjects=config["subjects"],
                                retention=RetentionPolicy.LIMITS,
                                max_msgs=config["max_msgs"],
                                max_bytes=config["max_bytes"],
                                discard=DiscardPolicy.OLD,
                                storage=StorageType.FILE,
                                description=config.get("description", ""),
                            )
                        )
                        logger.info(f"JetStream stream '{stream_name}' updated")
                    except Exception as e2:
                        logger.warning(f"JetStream stream '{stream_name}' init error: {e2}")

            self._streams_initialized = True
            return True
        except Exception as e:
            logger.warning(f"JetStream init failed (non-fatal): {e}")
            self._js = None
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # LEVEL 1: TELEMETRY (original API — fully backward compatible)
    # ═══════════════════════════════════════════════════════════════════════

    async def publish_verdict(
        self,
        session_id: str,
        verdict: str,  # SEAL, SABAR, HOLD, VOID
        stage: str,
        evidence_count: int = 0,
        source: str = "arifOS",
    ):
        """Publish a constitutional verdict event."""
        if not self._nc:
            logger.warning("NATS not connected, skipping verdict publish")
            return

        event = {
            "event": "VERDICT_ISSUED",
            "session_id": session_id,
            "verdict": verdict,
            "stage": stage,
            "evidence_count": evidence_count,
            "source": source,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_VERDICTS, json.dumps(event).encode())
            await self._nc.flush()
            logger.info(f"Published verdict: {verdict} for session {session_id}")
        except Exception as e:
            logger.error(f"Failed to publish verdict: {e}")

    async def publish_heartbeat(self, organ: str, status: str = "alive"):
        """Publish a heartbeat event from an organ."""
        if not self._nc:
            return

        event = {
            "event": "HEARTBEAT",
            "organ": organ,
            "status": status,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_HEARTBEAT, json.dumps(event).encode())
            await self._nc.flush()
        except Exception as e:
            logger.error(f"Failed to publish heartbeat: {e}")

    async def publish_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "warn",  # info, warn, critical
        source: str = "arifOS",
    ):
        """Publish an alert event."""
        if not self._nc:
            return

        event = {
            "event": "ALERT",
            "alert_type": alert_type,
            "message": message,
            "severity": severity,
            "source": source,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_ALERTS, json.dumps(event).encode())
            await self._nc.flush()
        except Exception as e:
            logger.error(f"Failed to publish alert: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # LEVEL 2: GOVERNANCE PIPELINE
    # ═══════════════════════════════════════════════════════════════════════

    async def publish_gate_verdict(
        self,
        gate: str,  # e.g. "GATE_1.5_PRINCIPAL_PARADOX"
        verdict: str,  # PASS, HOLD, SABAR, PROCEED
        session_id: str,
        tool_name: str,
        action_class: str = "OBSERVE",
        autonomy_tier: str = "",
        reasons: list[str] | None = None,
        violated_laws: list[str] | None = None,
    ):
        """Publish a governance gate verdict to the governance stream."""
        if not self._nc:
            return

        gate_num = gate.split("_")[1] if "_" in gate else "unknown"
        subject = (
            f"{SUBJECT_GOVERNANCE_PREFIX}.{gate_num}.pass"
            if verdict in ("PASS", "PROCEED")
            else f"{SUBJECT_GOVERNANCE_PREFIX}.{gate_num}.hold"
        )

        event = {
            "event": "GATE_VERDICT",
            "gate": gate,
            "verdict": verdict,
            "session_id": session_id,
            "tool_name": tool_name,
            "action_class": action_class,
            "autonomy_tier": autonomy_tier,
            "reasons": reasons or [],
            "violated_laws": violated_laws or [],
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(subject, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish gate verdict: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # LEVEL 3: INTER-ORGAN REQUEST/RESPONSE (NATS mesh)
    # ═══════════════════════════════════════════════════════════════════════

    async def request_organ(
        self,
        organ: str,
        method: str,
        params: dict[str, Any] | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any] | None:
        """Send a request to a federation organ via NATS and await response.

        Uses NATS request-reply pattern. Each organ subscribes to
        arifos.requests.<ORGAN> and replies on the inbox subject.

        Args:
            organ: Target organ name (GEOX, WEALTH, WELL, MIND, MEMORY, AAA)
            method: Tool name or method to call
            params: Arguments dict
            timeout: Seconds to wait for response

        Returns:
            Response dict or None on timeout/error.
        """
        if not self._nc:
            logger.warning("NATS not connected — cannot request organ via mesh")
            return None

        subject = organ_subject(organ, "requests")
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {},
            "caller": "arifOS",
            "timestamp": datetime.now(UTC).isoformat(),
        }

        try:
            msg = await self._nc.request(
                subject,
                json.dumps(payload).encode(),
                timeout=timeout,
            )
            data = json.loads(msg.data.decode())
            if data.get("error"):
                logger.warning(f"NATS request to {organ} returned error: {data['error']}")
            return data.get("result", data)
        except TimeoutError:
            logger.warning(f"NATS request to {organ} timed out after {timeout}s")
            return None
        except Exception as e:
            logger.error(f"NATS request to {organ} failed: {e}")
            return None

    async def respond_to(
        self,
        reply_subject: str,
        result: dict[str, Any],
        error: dict[str, Any] | None = None,
    ):
        """Respond to an incoming NATS request on the given reply subject."""
        if not self._nc or not reply_subject:
            return

        response = {
            "jsonrpc": "2.0",
            "id": 1,
            "result": result,
        }
        if error:
            response["error"] = error

        try:
            await self._nc.publish(reply_subject, json.dumps(response).encode())
        except Exception as e:
            logger.error(f"Failed to respond on {reply_subject}: {e}")

    async def broadcast_to_federation(
        self,
        event_type: str,
        payload: dict[str, Any],
        exclude: str | None = None,
    ):
        """Broadcast a message to all federation organs.

        Args:
            event_type: Event type identifier
            payload: Event data
            exclude: Optional organ name to exclude from broadcast
        """
        if not self._nc:
            return

        event = {
            "event": event_type,
            "source": "arifOS",
            "payload": payload,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        try:
            await self._nc.publish(SUBJECT_BROADCAST, json.dumps(event).encode())
            logger.info(f"Broadcast: {event_type} to federation")
        except Exception as e:
            logger.error(f"Failed to broadcast: {e}")

    async def subscribe_to_requests(
        self,
        organ: str,
        handler: Callable[[dict[str, Any]], Any],
    ) -> bool:
        """Subscribe to incoming NATS requests for a specific organ.

        The handler receives the parsed payload dict and must return a
        result dict. Errors are caught and returned as JSON-RPC errors.

        Args:
            organ: This organ's name (e.g. "arifOS")
            handler: async callable(payload) → result_dict

        Returns:
            True if subscription succeeded.
        """
        if not self._nc:
            return False

        subject = organ_subject(organ, "requests")

        async def _handler(msg):
            try:
                data = json.loads(msg.data.decode())
                result = await handler(data)
                if msg.reply:
                    await self.respond_to(msg.reply, result)
            except Exception as e:
                logger.error(f"Request handler error for {organ}: {e}")
                if msg.reply:
                    await self.respond_to(msg.reply, {}, {"code": -1, "message": str(e)})

        try:
            sub = await self._nc.subscribe(subject, cb=_handler)
            self._subscriptions[f"requests:{organ}"] = sub
            logger.info(f"Subscribed to {subject} for {organ}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to {subject}: {e}")
            return False

    async def subscribe_to_broadcast(
        self,
        handler: Callable[[dict[str, Any]], Any],
    ) -> bool:
        """Subscribe to federation-wide broadcast messages."""
        if not self._nc:
            return False

        async def _handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await handler(data)
            except Exception as e:
                logger.error(f"Broadcast handler error: {e}")

        try:
            sub = await self._nc.subscribe(SUBJECT_BROADCAST, cb=_handler)
            self._subscriptions["broadcast"] = sub
            logger.info(f"Subscribed to {SUBJECT_BROADCAST}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to broadcast: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # LEVEL 4: FEEDBACK LOOP SIGNALS
    # ═══════════════════════════════════════════════════════════════════════

    async def publish_feedback_signal(
        self,
        signal: str,  # PROCEED, REVISE_LOCAL, REVISE_GLOBAL, BRANCH, BACKTRACK, HOLD
        session_id: str,
        step_number: int = 0,
        source_organ: str = "arifOS",
        target_organ: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        """Publish a cross-organ feedback loop signal.

        This enables the plan→act→observe→evaluate→update_graph→re-plan
        cycle to span multiple organs. An arifOS reasoning step can trigger
        a GEOX computation, and GEOX's result feeds back into the loop.
        """
        if not self._nc:
            return

        subject = f"{SUBJECT_FEEDBACK_PREFIX}.{signal}"
        event = {
            "event": "FEEDBACK_SIGNAL",
            "signal": signal,
            "session_id": session_id,
            "step_number": step_number,
            "source_organ": source_organ,
            "target_organ": target_organ,
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(subject, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish feedback signal: {e}")

    async def subscribe_feedback(
        self,
        handler: Callable[[dict[str, Any]], Any],
        signal_filter: str | None = None,  # e.g. "HOLD" to only get HOLD signals
    ) -> bool:
        """Subscribe to cross-organ feedback loop signals."""
        if not self._nc:
            return False

        subject = (
            f"{SUBJECT_FEEDBACK_PREFIX}.{signal_filter}" if signal_filter else SUBJECT_FEEDBACK_ALL
        )

        async def _handler(msg):
            try:
                data = json.loads(msg.data.decode())
                await handler(data)
            except Exception as e:
                logger.error(f"Feedback handler error: {e}")

        try:
            sub = await self._nc.subscribe(subject, cb=_handler)
            key = f"feedback:{signal_filter or 'all'}"
            self._subscriptions[key] = sub
            logger.info(f"Subscribed to {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to feedback: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # LEVEL 5: GRADIENT DESCENT SIGNALS (Constitutional Cost Function)
    # ═══════════════════════════════════════════════════════════════════════

    async def publish_gradient(
        self,
        dimension: str,  # constitution, physics, capital, substrate, continuity, dignity
        delta: float,
        session_id: str,
        source_organ: str = "arifOS",
        metadata: dict[str, Any] | None = None,
    ):
        """Publish a gradient signal for one dimension of the constitutional cost function.

        C = α·C_constitution + β·C_physics + γ·C_capital + δ·C_substrate
            + ε·C_continuity + ζ·C_dignity

        Each organ publishes its dimension's gradient. The kernel integrates
        all dimensions to compute the total constitutional cost.
        """
        if not self._nc:
            return

        subject = f"{SUBJECT_GRADIENT_PREFIX}.{dimension}"
        event = {
            "event": "GRADIENT_SIGNAL",
            "dimension": dimension,
            "delta": delta,
            "session_id": session_id,
            "source_organ": source_organ,
            "metadata": metadata or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(subject, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish gradient: {e}")

    async def subscribe_gradient(
        self,
        dimension: str | None = None,
        handler: Callable[[dict[str, Any]], Any] | None = None,
    ) -> bool:
        """Subscribe to gradient signals for constitutional cost integration."""
        if not self._nc:
            return False

        subject = f"{SUBJECT_GRADIENT_PREFIX}.{dimension}" if dimension else SUBJECT_GRADIENT_ALL

        async def _handler(msg):
            try:
                data = json.loads(msg.data.decode())
                if handler:
                    await handler(data)
            except Exception as e:
                logger.error(f"Gradient handler error: {e}")

        try:
            sub = await self._nc.subscribe(subject, cb=_handler)
            key = f"gradient:{dimension or 'all'}"
            self._subscriptions[key] = sub
            logger.info(f"Subscribed to {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to subscribe to gradient: {e}")
            return False

    # ═══════════════════════════════════════════════════════════════════════
    # LEVEL 6: E7 PRINCIPAL PARADOX
    # ═══════════════════════════════════════════════════════════════════════

    async def publish_e7_autonomy_change(
        self,
        session_id: str,
        action_class: str,
        autonomy_tier: str,
        risk_tier: str,
        blast_radius: str,
        gate_verdict: str,
    ):
        """Publish E7 autonomy ceiling change to mesh."""
        if not self._nc:
            return

        event = {
            "event": "E7_AUTONOMY_CHANGE",
            "session_id": session_id,
            "action_class": action_class,
            "autonomy_tier": autonomy_tier,
            "risk_tier": risk_tier,
            "blast_radius": blast_radius,
            "gate_verdict": gate_verdict,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_E7_AUTONOMY, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish E7 autonomy change: {e}")

    async def publish_e7_override(
        self,
        session_id: str,
        reason: str,
        override_count: int,
        surge_active: bool,
    ):
        """Publish E7 principal override event to mesh."""
        if not self._nc:
            return

        event = {
            "event": "E7_OVERRIDE",
            "session_id": session_id,
            "reason": reason,
            "override_count": override_count,
            "surge_active": surge_active,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_E7_OVERRIDE, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish E7 override: {e}")

    async def publish_e7_attestation(
        self,
        receipt_hash: str,
        autonomy_tier: str,
        approving_authority: str,
        principal_override_occurred: bool,
    ):
        """Publish E7 attestation receipt to mesh."""
        if not self._nc:
            return

        event = {
            "event": "E7_ATTESTATION",
            "receipt_hash": receipt_hash,
            "autonomy_tier": autonomy_tier,
            "approving_authority": approving_authority,
            "principal_override_occurred": principal_override_occurred,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_E7_ATTESTATION, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish E7 attestation: {e}")

    # ═══════════════════════════════════════════════════════════════════════
    # /000 + /999 PUBLIC SURFACE
    # ═══════════════════════════════════════════════════════════════════════

    async def publish_000_surface(self, surface: dict[str, Any]):
        """Publish the /000 authority boundary surface to mesh."""
        if not self._nc:
            return

        event = {
            "event": "SURFACE_000",
            "surface": surface,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_PUBLIC_000, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish /000 surface: {e}")

    async def publish_999_surface(self, surface: dict[str, Any]):
        """Publish the /999 execution proof surface to mesh."""
        if not self._nc:
            return

        event = {
            "event": "SURFACE_999",
            "surface": surface,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        try:
            await self._nc.publish(SUBJECT_PUBLIC_999, json.dumps(event).encode())
        except Exception as e:
            logger.error(f"Failed to publish /999 surface: {e}")

    # ── Level 6: Intelligence Diffusion ────────────────────────────────────

    async def publish_intelligence_broadcast(
        self,
        floors_snapshot: dict[str, Any] | None = None,
        entropy_delta: float | None = None,
        verdict_summary: dict[str, Any] | None = None,
        lease_summary: dict[str, Any] | None = None,
        organ_heartbeats: dict[str, str] | None = None,
    ) -> None:
        """
        Broadcast current kernel intelligence state to all federation organs.

        This is the dynamic intelligence flow that organs need to operate
        with awareness of the kernel's constitutional state. Called after
        every 888_JUDGE verdict or on timer for continuous diffusion.

        Organs subscribe to 'arifos.intelligence.>' to receive these updates.
        """
        if not self.connected:
            return

        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "source": "arifOS-kernel",
        }

        # Floor snapshot
        if floors_snapshot:
            event["floors"] = floors_snapshot
            try:
                await self._nc.publish(
                    SUBJECT_INTELLIGENCE_FLOORS,
                    json.dumps(event).encode(),
                )
            except Exception as e:
                logger.error(f"Failed to publish intelligence floors: {e}")

        # Entropy delta
        if entropy_delta is not None:
            event["entropy_delta"] = entropy_delta
            try:
                await self._nc.publish(
                    SUBJECT_INTELLIGENCE_ENTROPY,
                    json.dumps(event).encode(),
                )
            except Exception as e:
                logger.error(f"Failed to publish intelligence entropy: {e}")

        # Verdict summary
        if verdict_summary:
            event["verdict"] = verdict_summary
            try:
                await self._nc.publish(
                    SUBJECT_INTELLIGENCE_VERDICT,
                    json.dumps(event).encode(),
                )
            except Exception as e:
                logger.error(f"Failed to publish intelligence verdict: {e}")

        # Lease summary
        if lease_summary:
            event["leases"] = lease_summary
            try:
                await self._nc.publish(
                    SUBJECT_INTELLIGENCE_LEASE,
                    json.dumps(event).encode(),
                )
            except Exception as e:
                logger.error(f"Failed to publish intelligence lease: {e}")

        # Organ heartbeats (broadcast so every organ knows every other organ)
        if organ_heartbeats:
            event["heartbeats"] = organ_heartbeats
            try:
                await self._nc.publish(
                    SUBJECT_BROADCAST,
                    json.dumps(event).encode(),
                )
            except Exception as e:
                logger.error(f"Failed to publish broadcast: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════════════

event_bus = NATSEventBus()


# ═══════════════════════════════════════════════════════════════════════════════
# CONVENIENCE FUNCTIONS (backward compatible)
# ═══════════════════════════════════════════════════════════════════════════════


async def publish_arifOS_heartbeat():
    """Publish arifOS heartbeat to NATS."""
    await event_bus.publish_heartbeat("arifOS", "alive")


async def init_nats_event_bus(nats_url: str = "nats://127.0.0.1:4222") -> bool:
    """Initialize the NATS event bus connection and JetStream streams."""
    return await event_bus.connect(nats_url)


async def shutdown_nats_event_bus():
    """Shutdown the NATS event bus gracefully."""
    await event_bus.disconnect()


# ═══════════════════════════════════════════════════════════════════════════════
# CROSS-ORGAN FEEDBACK LOOP BRIDGE
# ═══════════════════════════════════════════════════════════════════════════════


async def wire_cross_organ_feedback(
    session_id: str,
    source_organ: str,
    target_organ: str,
    signal: str,
    step_number: int = 0,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Wire a feedback signal from one organ to another via NATS.

    This is the cross-organ extension of feedback_loop.py. Instead of
    the feedback loop running only within a single arif_think call,
    it now spans organs: arifOS reason → GEOX compute → WEALTH evaluate →
    feedback signal → arifOS re-plan.

    Args:
        session_id: Active session
        source_organ: Organ emitting the signal
        target_organ: Organ that should receive it
        signal: FeedbackSignal value (PROCEED, REVISE_LOCAL, etc.)
        step_number: Current reasoning step
        metadata: Additional context for the receiving organ
    """
    await event_bus.publish_feedback_signal(
        signal=signal,
        session_id=session_id,
        step_number=step_number,
        source_organ=source_organ,
        target_organ=target_organ,
        metadata=metadata,
    )


async def publish_constitutional_gradient(
    session_id: str,
    constitution_delta: float = 0.0,
    physics_delta: float = 0.0,
    capital_delta: float = 0.0,
    substrate_delta: float = 0.0,
    continuity_delta: float = 0.0,
    dignity_delta: float = 0.0,
) -> None:
    """Publish all six dimensions of the constitutional cost gradient.

    C = α·C_constitution + β·C_physics + γ·C_capital
        + δ·C_substrate + ε·C_continuity + ζ·C_dignity
    """
    dims = [
        ("constitution", constitution_delta),
        ("physics", physics_delta),
        ("capital", capital_delta),
        ("substrate", substrate_delta),
        ("continuity", continuity_delta),
        ("dignity", dignity_delta),
    ]
    for dim, delta in dims:
        if delta != 0.0:
            await event_bus.publish_gradient(
                dimension=dim,
                delta=delta,
                session_id=session_id,
            )


__all__ = [
    # Singleton
    "event_bus",
    # Lifecycle
    "init_nats_event_bus",
    "shutdown_nats_event_bus",
    "publish_arifOS_heartbeat",
    # Subject constants
    "SUBJECT_VERDICTS",
    "SUBJECT_HEARTBEAT",
    "SUBJECT_ALERTS",
    "SUBJECT_EVIDENCE",
    "SUBJECT_FLOORS",
    "SUBJECT_GOVERNANCE_PREFIX",
    "SUBJECT_GOVERNANCE_PASS",
    "SUBJECT_GOVERNANCE_HOLD",
    "SUBJECT_GOVERNANCE_ALL",
    "SUBJECT_REQUESTS_PREFIX",
    "SUBJECT_RESPONSES_PREFIX",
    "SUBJECT_BROADCAST",
    "SUBJECT_FEEDBACK_PREFIX",
    "SUBJECT_FEEDBACK_PROCEED",
    "SUBJECT_FEEDBACK_REVISE_LOCAL",
    "SUBJECT_FEEDBACK_REVISE_GLOBAL",
    "SUBJECT_FEEDBACK_BRANCH",
    "SUBJECT_FEEDBACK_BACKTRACK",
    "SUBJECT_FEEDBACK_HOLD",
    "SUBJECT_FEEDBACK_ALL",
    "SUBJECT_GRADIENT_PREFIX",
    "SUBJECT_GRADIENT_CONSTITUTION",
    "SUBJECT_GRADIENT_PHYSICS",
    "SUBJECT_GRADIENT_CAPITAL",
    "SUBJECT_GRADIENT_SUBSTRATE",
    "SUBJECT_GRADIENT_CONTINUITY",
    "SUBJECT_GRADIENT_DIGNITY",
    "SUBJECT_GRADIENT_ALL",
    "SUBJECT_E7_AUTONOMY",
    "SUBJECT_E7_OVERRIDE",
    "SUBJECT_E7_ATTESTATION",
    "SUBJECT_PUBLIC_000",
    "SUBJECT_PUBLIC_999",
    # Intelligence Diffusion (Level 6)
    "SUBJECT_INTELLIGENCE_FLOORS",
    "SUBJECT_INTELLIGENCE_ENTROPY",
    "SUBJECT_INTELLIGENCE_VERDICT",
    "SUBJECT_INTELLIGENCE_LEASE",
    "SUBJECT_INTELLIGENCE_ALL",
    # Federation
    "FEDERATION_ORGANS",
    "organ_subject",
    # Cross-organ bridges
    "wire_cross_organ_feedback",
    "publish_constitutional_gradient",
]
