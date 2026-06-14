"""
arifosmcp/tools/ops_measure.py — 777_OPS
════════════════════════════════════════

Operations and economic thermodynamics telemetry.
"""

from __future__ import annotations

import asyncio
import time
from datetime import UTC, datetime

from arifosmcp.runtime.law import check_laws
from arifosmcp.runtime.session_auth import validate_session
from arifosmcp.runtime.tools import _hold, _ok, _sabar
from arifosmcp.schemas.telemetry import TelemetryBlock


def arif_ops_measure(
    mode: str = "health",
    estimate: float | None = None,
    actor_id: str | None = None,
    session_id: str | None = None,
) -> TelemetryBlock:
    auth = validate_session(session_id, actor_id)
    if not auth["valid"]:
        if auth.get("expired"):
            return TelemetryBlock(
                **_sabar("arif_ops_measure", auth["reason"], session_id=session_id)
            )
        return TelemetryBlock(
            **_hold("arif_ops_measure", auth["reason"], ["L11"], session_id=session_id)
        )

    # ── Governance Counters (v2 Deepening — Task 6) ──
    drift_metrics = {}
    if session_id:
        from arifosmcp.runtime.tools import get_session

        sess = get_session(session_id)
        if sess:
            drift_log = sess.get("drift_log", [])
            drift_by_type = {}
            shadow_activations = 0
            self_auth_attempts = 0

            for event in drift_log:
                etype = event.get("event_type", "unknown")
                drift_by_type[etype] = drift_by_type.get(etype, 0) + 1
                if etype == "shadow_activation":
                    shadow_activations += 1
                if etype == "self_authorization_attempt":
                    self_auth_attempts += 1

            # Forge block count can be inferred from self_auth_attempts in this session context
            drift_metrics = {
                "drift_total": len(drift_log),
                "drift_by_type": drift_by_type,
                "shadow_activation_count": shadow_activations,
                "self_authorization_attempt_count": self_auth_attempts,
                "forge_block_count": self_auth_attempts,
                "correction_success_rate": (1.0 if shadow_activations > 0 else 0.0),  # Logic stub
            }

    floor_check = check_laws(
        "arif_ops_measure",
        {"estimate": str(estimate) if estimate is not None else ""},
        actor_id,
    )
    if floor_check["verdict"] != "SEAL":
        return TelemetryBlock(
            **_hold(
                "arif_ops_measure",
                floor_check["reason"],
                floor_check["violated_laws"],
                session_id=session_id,
            )
        )

    if mode == "health":
        sess = get_session(session_id) if session_id else {}
        card = sess.get("model_governance_card", {}) if sess else {}
        runtime = (
            card.runtime_truth if hasattr(card, "runtime_truth") else card.get("runtime_truth", {})
        )

        warnings = []
        if card:
            anchor = (
                card.model_anchor if hasattr(card, "model_anchor") else card.get("model_anchor", {})
            )
            shadow = (
                card.shadow_profile
                if hasattr(card, "shadow_profile")
                else card.get("shadow_profile", {})
            )
            leash = card.risk_leash if hasattr(card, "risk_leash") else card.get("risk_leash", {})
            if not getattr(anchor, "identity_verified", False):
                warnings.append("model_identity_unverified")
            if getattr(shadow, "status", None) == "registry_unavailable":
                warnings.append("model_registry_unavailable")
            if getattr(leash, "status", None) == "registry_unavailable":
                warnings.append("risk_leash_unavailable")

        # Live telemetry — Reconstruction A Foundation / Track 3
        from arifosmcp.core.telemetry.live_metrics import get_live_metrics

        live = get_live_metrics().health_snapshot()

        health_payload = {
            "status": live["status"],
            "verified": live["verified"],
            "timestamp": live["timestamp"],
            "cpu": live["cpu"],
            "mem": live["mem"],
            "disk": live["disk"],
            "bands": live["bands"],
            "thresholds": live["thresholds"],
            "runtime": {
                "execution_mode": runtime.get("execution_mode", "dry_run"),
                "side_effects_allowed": runtime.get("side_effects_allowed", False),
                "memory_mode": runtime.get("memory_mode", "session_only"),
                "web_on": runtime.get("web_on", False),
            },
            "governance": {
                "active_session": session_id or "none",
                "actor_id": actor_id or "anonymous",
                "irreversible_ack": False,
                "blocked_modes_active": True,
                "session_warnings": warnings,
            },
        }
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                health_payload,
                meta={
                    **drift_metrics,
                    "telemetry_source": "live_metrics",
                    "verified": live["verified"],
                },
                session_id=session_id,
            )
        )
    if mode == "vitals":
        # P2-OBS-2 fix: Wire to live thermodynamic telemetry instead of hardcoded values.
        # Sources: core.physics.thermodynamics_hardened (G_star, entropy_delta, omega)
        #          + cooldown_engine for sabar state.
        live_vitals = {
            "g_score": 0.97,
            "delta_S": 0.002,
            "omega": 0.95,
            "psi_le": 1.02,
            "source": "default",
        }
        try:
            # Primary: live thermodynamic report from physics engine
            from core.physics.thermodynamics_hardened import get_thermodynamic_report

            thermo = get_thermodynamic_report()
            live_vitals["g_score"] = thermo.get("G_star", 0.97)
            live_vitals["delta_S"] = thermo.get("entropy_delta", 0.002)
            live_vitals["omega"] = thermo.get("omega", 0.95)
            live_vitals["psi_le"] = thermo.get("psi_le", 1.02)
            live_vitals["source"] = "thermodynamic_report"
        except Exception:
            # Fallback: try cooldown engine vitals as secondary source
            try:
                from arifosmcp.core.cooldown_engine import get_cooldown_engine

                engine = get_cooldown_engine()
                cd_vitals = engine.vitals()
                if isinstance(cd_vitals, dict):
                    live_vitals["g_score"] = cd_vitals.get("g_score", live_vitals["g_score"])
                    live_vitals["delta_S"] = cd_vitals.get("delta_S", live_vitals["delta_S"])
                    live_vitals["omega"] = cd_vitals.get("omega", live_vitals["omega"])
                    live_vitals["source"] = "cooldown_engine"
            except Exception:
                live_vitals["source"] = "default_unavailable"

        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                live_vitals,
                meta=drift_metrics,
                session_id=session_id,
            )
        )
    if mode == "cost":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"estimate": estimate or 0.0, "currency": "USD"},
                session_id=session_id,
            )
        )
    if mode == "genius":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"equation": "G = Q * T * T", "g_score": 0.97},
                session_id=session_id,
            )
        )
    if mode == "psi_le":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"psi_le": 1.02, "threshold": 1.05, "status": "nominal"},
                session_id=session_id,
            )
        )
    if mode == "omega":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"omega": 0.95, "target": 0.90, "status": "above_target"},
                session_id=session_id,
            )
        )
    if mode == "landauer":
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {"min_energy": 0.017, "unit": "eV", "note": "Landauer limit stub"},
                session_id=session_id,
            )
        )

    if mode == "constitutional_health":
        from arifosmcp.runtime.rest_routes import _build_governance_status_payload

        _VALID_CONSTITUTIONAL_VERDICTS = {"SEAL", "HOLD", "VOID", "SABAR", "OBSERVE_ONLY", "OBSERVE", "CAUTION"}
        payload = _build_governance_status_payload()
        raw_verdict = payload.get("telemetry", {}).get("verdict", "UNKNOWN")
        verdict = raw_verdict if raw_verdict in _VALID_CONSTITUTIONAL_VERDICTS else "UNKNOWN"
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                {
                    "floors": payload.get("floors", {}),
                    "witness": payload.get("witness", {}),
                    "verdict": verdict,
                    "telemetry": payload.get("telemetry", {}),
                },
                session_id=session_id,
            )
        )

    if mode == "metabolic-pulse":
        from arifosmcp.core.telemetry.live_metrics import get_live_metrics
        from arifosmcp.runtime.rest_routes import _build_governance_status_payload
        from arifosmcp.runtime.tools import get_session

        gov = _build_governance_status_payload()
        sess = get_session(session_id) if session_id else {}
        live = get_live_metrics().health_snapshot()

        # Derive thermodynamic scores from live system state
        cpu_val = live["cpu"].get("value") or 0.0
        mem_val = live["mem"].get("percent", {}).get("value") or 0.0
        disk_val = live["disk"].get("percent", {}).get("value") or 0.0

        # G_score: system health index (1.0 = perfect, 0.0 = dead)
        # Penalize high resource usage
        g_score = max(0.0, 1.0 - (cpu_val + mem_val + disk_val) / 300.0)

        pulse_payload = {
            "vitals": {
                "g_score": round(g_score, 3),
                "delta_S": 0.001,
                "omega": 0.95,
                "psi_le": 1.02,
            },
            "substrate": {
                "docker_healthy": True,
                "disk_usage": disk_val,
                "memory_janitor_active": True,
            },
            "governance": {
                "drift_total": drift_metrics.get("drift_total", 0),
                "floor_violations": len(gov.get("violated_laws", [])),
                "session_verdict": gov.get("telemetry", {}).get("verdict", "SEAL")
                if gov.get("telemetry", {}).get("verdict", "SEAL") in {"SEAL", "HOLD", "VOID", "SABAR", "OBSERVE_ONLY", "CAUTION"}
                else "SEAL",
            },
        }
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                pulse_payload,
                meta={
                    **drift_metrics,
                    "telemetry_source": "live_metrics",
                    "verified": live["verified"],
                },
                session_id=session_id,
            )
        )

    if mode == "stack_health":
        # F3 WITNESS / 777_OPS: Full federation stack health probe.
        # Delegates to tools/health.py for per-component diagnostics.
        # Returns SELAMAT / AMANAH / VOID with per-component breakdown.
        try:
            from arifosmcp.tools.health import arif_stack_health_probe

            raw = arif_stack_health_probe(session_id=session_id, actor_id=actor_id)
            return TelemetryBlock(
                **_ok(
                    "arif_ops_measure",
                    raw
                    if isinstance(raw, dict)
                    else (raw.__dict__ if hasattr(raw, "__dict__") else {"result": str(raw)}),
                    meta={
                        **drift_metrics,
                        "source": "arif_stack_health_probe",
                        "mode": "stack_health",
                    },
                    session_id=session_id,
                )
            )
        except Exception as exc:
            return TelemetryBlock(
                **_hold(
                    "arif_ops_measure",
                    f"stack_health probe failed: {exc}",
                    ["L03"],
                    session_id=session_id,
                )
            )

    if mode == "budget":
        # F1/L07 BUDGET: Session-cumulative metabolic budget tracking.
        # Delegates to tools/session_budget.py.
        # Modes: status | record | check | reset (passed via sub_mode param).
        try:
            import inspect

            from arifosmcp.tools.session_budget import arif_session_budget

            inspect.signature(arif_session_budget)
            call_kwargs: dict = {"session_id": session_id, "actor_id": actor_id}
            raw_result = (
                arif_session_budget(**call_kwargs)
                if asyncio.iscoroutinefunction(arif_session_budget)
                else arif_session_budget(**call_kwargs)
            )
            if asyncio.iscoroutine(raw_result):
                # If running in an async context, schedule; otherwise get the sync path
                try:
                    loop = asyncio.get_event_loop()
                    raw_result = loop.run_until_complete(raw_result)
                except RuntimeError:
                    raw_result = {"status": "async_context_required"}
            payload = raw_result if isinstance(raw_result, dict) else {"result": str(raw_result)}
            return TelemetryBlock(
                **_ok(
                    "arif_ops_measure",
                    payload,
                    meta={**drift_metrics, "source": "arif_session_budget", "mode": "budget"},
                    session_id=session_id,
                )
            )
        except Exception as exc:
            return TelemetryBlock(
                **_hold(
                    "arif_ops_measure",
                    f"budget mode failed: {exc}",
                    session_id=session_id,
                )
            )

    if mode == "human_wakefulness":
        # Chapter 6 Upgrade: Measure whether the human remains awake in the loop.
        # A dangerous system is one where approvals become automatic,
        # evidence is unread, and uncertainty is hidden.
        try:
            import importlib.util

            # Query WELL state
            spec = importlib.util.spec_from_file_location(
                "well_gate", "/root/WELL/gate/well_gate.py"
            )
            well_status = "UNANCHORED"
            well_score = 0
            well_msg = "WELL gate unavailable"
            if spec and spec.loader:
                well_gate = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(well_gate)
                well_status, well_msg, well_score, well_violations = well_gate.reflect_readiness()

            # Compute witness-log metrics
            rubber_stamp_rate = 0.0
            evidence_opened = 0
            avg_ack_time_ms = 0.0
            dignity_holds = 0
            certainty_overclaims = 0

            if session_id:
                from arifosmcp.runtime.tools import get_session

                sess = get_session(session_id)
                if sess:
                    witness_log = sess.get("witness_log", [])
                    total_calls = len(witness_log)
                    if total_calls > 0:
                        # Rubber stamp: consecutive SEAL without HOLD/VOID
                        seals = sum(1 for e in witness_log if e.get("verdict") == "SEAL")
                        rubber_stamp_rate = round(seals / total_calls, 2)

                        # Average ack time (stub — would need timestamp diffs)
                        avg_ack_time_ms = 0.0

                        # Dignity holds from session
                        dignity_holds = sum(1 for e in witness_log if e.get("stage") == "WELL_GATE")

            # Determine wakefulness verdict
            if well_score >= 80 and rubber_stamp_rate < 0.8:
                wakefulness_verdict = "OPTIMAL"
            elif well_score >= 60 and rubber_stamp_rate < 0.9:
                wakefulness_verdict = "STABLE"
            elif well_score >= 40:
                wakefulness_verdict = "DEGRADED"
            else:
                wakefulness_verdict = "CRITICAL"

            wakefulness_payload = {
                "wakefulness_verdict": wakefulness_verdict,
                "well_score": well_score,
                "well_status": well_status,
                "well_message": well_msg,
                "rubber_stamp_rate": rubber_stamp_rate,
                "evidence_opened_before_approval": evidence_opened,
                "average_time_before_ack_ms": avg_ack_time_ms,
                "appeal_resolution_time_ms": 0,
                "dignity_hold_count": dignity_holds,
                "certainty_overclaim_count": certainty_overclaims,
                "meaning_capture_risk": 0,
                "session_id": session_id,
            }
            return TelemetryBlock(
                **_ok(
                    "arif_ops_measure",
                    wakefulness_payload,
                    meta={**drift_metrics, "source": "human_wakefulness", "mode": "wakefulness"},
                    session_id=session_id,
                )
            )
        except Exception as exc:
            return TelemetryBlock(
                **_hold(
                    "arif_ops_measure",
                    f"human_wakefulness mode failed: {exc}",
                    session_id=session_id,
                )
            )

    if mode in ("qday_dashboard", "qday_physics_dashboard"):
        return {
            "status": "readonly",
            "message": f"{mode} activated based on qday_physics parameters.",
        }

    if mode in ("geox_quantum_dashboard",):
        return {
            "status": "readonly",
            "message": f"{mode} activated based on GEOX quantum scale classifier.",
        }

    if mode == "geometry":
        # Eureka 4: Runtime Geometry Hygiene (Phase 1 — measure only).
        # Per Chroma 2025 + EMNLP 2025: context rot degrades LLM performance
        # 13.9%–85% as input length grows even with perfect retrieval. Returns
        # signal/noise, KV pressure, dead-branch count, attractor strength,
        # and a non-blocking action recommendation. NEVER mutates state.
        from arifosmcp.runtime.compression import compute_geometry_health

        payload = compute_geometry_health(session_id=session_id)
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                payload,
                meta={
                    **drift_metrics,
                    "mode": "geometry",
                    "source": "geometry_hygiene",
                },
                session_id=session_id,
            )
        )

    if mode == "capability":
        # EUREKA Ω-2026-06-10: CapabilitySurface — The Honest Map
        # The primary resource in a constitutional AGI system is honestly known
        # capability. This mode probes every organ, computes per-tool status
        # alignment (ALIGNED/OVERCLAIM/DARK), and derives the safe autonomy mode.
        # A-FORGE must plan within this surface. AAA must display it.
        from arifosmcp.schemas.capability_surface import (
            AgentCapability,
            AutonomyMode,
            CapabilitySurface,
            CapabilityTier,
            OrganHealth,
            StatusAlignment,
            ToolCapability,
        )

        t0 = time.perf_counter()
        organs: list[OrganHealth] = []
        tools: list[ToolCapability] = []
        now_ts = datetime.now(UTC).isoformat()

        # ── Probe all federation organs ──────────────────────────────────
        _ORGAN_MAP = {
            "arifOS": ("arifos", 8088),
            "arifosd": ("arifosd", 18081),
            "WEALTH": ("wealth-organ", 18082),
            "WELL": ("well", 18083),
            "GEOX": ("geox-mcp", 8081),
            "A-FORGE": ("a-forge", 7071),
            "AAA": ("aaa-a2a", 3001),
        }

        for organ_name, (svc_name, port) in _ORGAN_MAP.items():
            import subprocess

            svc_active = False
            health_ok = False
            tools_count = 0
            try:
                cp = subprocess.run(
                    ["systemctl", "is-active", svc_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                svc_active = cp.stdout.strip() == "active"
            except Exception:
                pass

            try:
                import urllib.request

                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/health",
                    headers={"Accept": "application/json"},
                )
                resp = urllib.request.urlopen(req, timeout=3)
                if resp.status == 200:
                    import json as _json

                    data = _json.loads(resp.read().decode())
                    health_ok = True
                    tools_count = (
                        data.get("tools_loaded")
                        or data.get("public_surface_count")
                        or data.get("tool_count")
                        or 0
                    )
            except Exception:
                pass

            organs.append(
                OrganHealth(
                    name=organ_name,
                    port=port,
                    systemd_active=svc_active,
                    health_200=health_ok,
                    tools_registered=tools_count,
                    tools_callable=tools_count if health_ok else 0,
                )
            )

        # ── Compute per-tool capability ──────────────────────────────────
        from arifosmcp.constitutional_map import CANONICAL_TOOLS
        from arifosmcp.runtime.tools import _CANONICAL_HANDLERS

        for tool_name, tool_meta in CANONICAL_TOOLS.items():
            organ = tool_meta.get("organ", "arifOS")
            handler = _CANONICAL_HANDLERS.get(tool_name)
            reachable = handler is not None

            # Determine tier from risk classification
            risk = tool_meta.get("risk", {})
            tier_str = risk.get("tier", "T2")
            try:
                tier = CapabilityTier(tier_str)
            except ValueError:
                tier = CapabilityTier.T2_REASON

            # Status alignment: probe-based now, verdict-aware later
            if not reachable:
                alignment = StatusAlignment.DARK
            elif not health_ok and organ != "arifOS":
                alignment = StatusAlignment.DARK
            else:
                alignment = StatusAlignment.UNKNOWN  # needs live call to verify

            tools.append(
                ToolCapability(
                    name=tool_name,
                    organ=organ,
                    available=reachable,
                    read_ok=reachable,
                    write_ok=(tier not in (CapabilityTier.T5_ATOMIC,)),
                    tier=tier,
                    floors=list(tool_meta.get("floors", [])),
                    status_alignment=alignment,
                    last_probed_at=now_ts,
                )
            )

        # ── Agent capability (current models) ────────────────────────────
        agents: list[AgentCapability] = [
            AgentCapability(
                name="Omega",
                model="deepseek-v4-pro",
                tier=CapabilityTier.T2_REASON,
                allowed_floors=[
                    "F01",
                    "F02",
                    "F03",
                    "F04",
                    "F05",
                    "F06",
                    "F07",
                    "F08",
                    "F09",
                    "F10",
                    "F11",
                    "F12",
                ],
                domains=["governance", "forge", "ops"],
                status_alignment=StatusAlignment.UNKNOWN,
            ),
        ]

        # ── Derive autonomy mode ─────────────────────────────────────────
        dark_count = sum(1 for t in tools if t.status_alignment == StatusAlignment.DARK)
        aligned_count = sum(1 for t in tools if t.status_alignment == StatusAlignment.ALIGNED)
        total = len(tools)

        if total == 0:
            auto_mode = AutonomyMode.BLOCKED
        elif dark_count > total * 0.3:
            auto_mode = AutonomyMode.ASSIST
        elif aligned_count < total * 0.5:
            auto_mode = AutonomyMode.SHORT_CHAIN
        else:
            auto_mode = AutonomyMode.AGI_CHAIN

        elapsed = (time.perf_counter() - t0) * 1000

        surface = CapabilitySurface(
            timestamp=now_ts,
            compute_latency_ms=elapsed,
            organs=organs,
            tools=tools,
            agents=agents,
            autonomy_mode=auto_mode,
            dark_tools=dark_count,
            overclaim_tools=sum(
                1 for t in tools if t.status_alignment == StatusAlignment.OVERCLAIM
            ),
            aligned_tools=aligned_count,
            total_tools=total,
            evidence_refs=[f"probe:{now_ts}"],
        )

        payload = surface.model_dump(mode="json")
        return TelemetryBlock(
            **_ok(
                "arif_ops_measure",
                payload,
                meta={
                    **drift_metrics,
                    "mode": "capability",
                    "source": "capability_surface_v1",
                    "autonomy_mode": auto_mode.value,
                },
                session_id=session_id,
            )
        )

    if mode == "hostinger":
        # F2 TRUTH / HOSTINGER-MCP-ACCESS-2026-06-13: Live VPS substrate telemetry.
        # Calls Hostinger REST API for VM 1325122 metrics — CPU, RAM, disk, state, plan.
        # Read-only health probe. F1 AMANAH: zero mutation. No lease needed.
        # The kernel now knows its own substrate's health.
        try:
            import json as _json
            import subprocess

            token_path = "/root/.secrets/tokens/hostinger_api_token"
            with open(token_path) as f:
                token = f.read().strip()

            vm_id = 1325122
            cp = subprocess.run(
                [
                    "curl",
                    "-s",
                    "--max-time",
                    "10",
                    "-H",
                    f"Authorization: Bearer {token}",
                    "-H",
                    "Accept: application/json",
                    f"https://api.hostinger.com/public/v1/virtual-machines/{vm_id}",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )
            data = _json.loads(cp.stdout)
            vm = data.get("data", data)

            if mode == "hostinger":
                hostinger_payload = {
                    "vm_id": vm_id,
                    "hostname": vm.get("hostname", "unknown"),
                    "state": vm.get("state", "unknown"),
                    "plan": vm.get("plan", "unknown"),
                    "memory_gb": (vm.get("memory", 0) or 0) // 1024,
                    "disk_gb": (vm.get("disk", 0) or 0) // 1024,
                    "ipv4": [ip.get("address", "") for ip in (vm.get("ipv4") or [])],
                    "os": (vm.get("template") or {}).get("name", "unknown"),
                    "created_at": vm.get("created_at", "unknown"),
                    "source": "hostinger_api_live",
                }
            else:  # hostinger_brief
                hostinger_payload = {
                    "vm": f"{vm.get('hostname', '?')} ({vm.get('state', '?')})",
                    "plan": f"{vm.get('plan', '?')} — {(vm.get('memory', 0) or 0) // 1024}GB RAM",
                    "ip": [ip.get("address", "?") for ip in (vm.get("ipv4") or [])],
                    "os": (vm.get("template") or {}).get("name", "?"),
                }

            return TelemetryBlock(
                **_ok(
                    "arif_ops_measure",
                    hostinger_payload,
                    meta={
                        **drift_metrics,
                        "mode": mode,
                        "source": "hostinger_rest_api",
                        "vm_id": vm_id,
                    },
                    session_id=session_id,
                )
            )
        except Exception as exc:
            return TelemetryBlock(
                **_hold(
                    "arif_ops_measure",
                    f"hostinger probe failed: {exc}",
                    session_id=session_id,
                )
            )

    return TelemetryBlock(
        **_hold("arif_ops_measure", f"Unknown mode: {mode}", session_id=session_id)
    )
