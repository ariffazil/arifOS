# -*- coding: utf-8 -*-
"""
arifOS Output Presenter (v52.5.1-SEAL)
================================
Encoder -> Presenter -> Decoder architecture for Human-Optimized Output.
Translates raw JSON into constitutionally aligned human presentation.

Authority: Δ Antigravity
Version: v52.5.1-SEAL

Architecture:
1. ENCODER: Machine JSON → LLM semantics (normalize, fix broken responses)
2. PRESENTER: LLM semantics → Presentation strategy (user-aware adaptation)
3. DECODER: Strategy → Human-readable output (tables, badges, text)

Phase 9 Integration:
- Handles Phoenix-72 cooling metadata
- Parses zkPC cryptographic receipts
- Displays EUREKA sieve memory bands
- Renders emergency states (SABAR, VOID, 888_HOLD)

DITEMPA BUKAN DIBERI
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# --- 1. ENCODER (Machine -> Semantics) ---

@dataclass
class Semantics:
    """
    Semantic representation of a tool execution result.

    Normalized from raw server JSON to structured understanding.
    """
    status: str  # "SEAL", "PARTIAL", "VOID", "SABAR", "888_HOLD", "ERROR"
    summary: str
    details: Dict[str, Any]
    metrics: Dict[str, Any]  # delta_s, peace_sq, omega_0, etc.
    warnings: List[str]
    is_emergency: bool

    # Phase 9 Extensions
    floor_scores: Optional[Dict[str, Any]] = None  # F1-F13 scores
    cooling: Optional[Dict[str, Any]] = None       # Phoenix-72 metadata
    zkpc: Optional[Dict[str, Any]] = None          # zkPC receipt
    memory: Optional[Dict[str, Any]] = None        # EUREKA sieve band
    session_id: Optional[str] = None
    stage: Optional[str] = None
    latency_ms: float = 0.0

class Encoder:
    """
    Parses raw JSON from servers into structured Semantics.

    Handles "stupid servers" with broken/null/timeout responses.
    """

    def encode(self, raw_output: Dict[str, Any]) -> Semantics:
        """
        Encodes raw tool output into a Semantics object.
        Handles missing fields, errors, and standardizes the schema.

        Args:
            raw_output: Raw JSON from server (VAULT/AGI/ASI/APEX)

        Returns:
            Normalized Semantics with defaults for missing fields
        """
        # 1. Detect if this is an error wrapper
        if "error" in raw_output:
            return Semantics(
                status="ERROR",
                summary=raw_output["error"].get("message", "Unknown Error"),
                details=raw_output["error"],
                metrics={},
                warnings=["System Error Detected"],
                is_emergency=True
            )

        # 2. Handle null/empty responses from "stupid servers"
        if not raw_output:
            return self._default_error_semantics("Empty server response")

        # 2. Extract content
        # MCP tool calls usually return { "content": [ { "type": "text", "text": "..." } ] }
        # Or sometimes direct JSON result { "result": { ... } }

        content = raw_output.get("content", [])
        result_data = {}

        # Try to parse text content as JSON if possible, or treat as plain text
        if content and isinstance(content, list) and len(content) > 0:
            text_body = content[0].get("text", "")
            try:
                # heuristics: if it looks like JSON, parse it
                if text_body.strip().startswith("{"):
                    result_data = json.loads(text_body)
                else:
                    result_data = {"message": text_body}
            except Exception:
                result_data = {"message": text_body}
        elif "result" in raw_output:
             result_data = raw_output["result"]
        else:
             # Fallback
             result_data = raw_output

        # 3. Extract verdict and constitutional metrics
        verdict = result_data.get("verdict", "SEAL")
        if "verdict" not in result_data and "error" not in result_data:
            # It might be a simple tool like 'time' which doesn't return a verdict
            verdict = "SEAL"

        metrics = {
            "delta_s": result_data.get("entropy_delta", result_data.get("delta_s", 0.0)),
            "peace_sq": result_data.get("peace_squared", result_data.get("peace_sq", 1.0)),
            "omega_0": result_data.get("humility", result_data.get("omega_0", 0.04))
        }

        # 4. Extract Phase 9 features
        floor_scores = result_data.get("floor_scores", {})
        cooling = self._extract_cooling(result_data)
        zkpc = self._extract_zkpc(result_data)
        memory = self._extract_memory(result_data)
        session_id = result_data.get("session_id", raw_output.get("session_id", "unknown"))
        stage = result_data.get("stage", raw_output.get("stage", "unknown"))
        latency_ms = result_data.get("latency_ms", raw_output.get("latency_ms", 0.0))

        # 5. Determine Emergency Status
        is_gov_fail = verdict in ["VOID", "SABAR", "888_HOLD"]
        has_errors = bool(result_data.get("errors", []))
        is_emergency = is_gov_fail or has_errors

        return Semantics(
            status=verdict,
            summary=result_data.get("summary", result_data.get("message", "Tool execution complete")),
            details=result_data,
            metrics=metrics,
            warnings=result_data.get("warnings", []),
            is_emergency=is_emergency,
            floor_scores=floor_scores if floor_scores else None,
            cooling=cooling,
            zkpc=zkpc,
            memory=memory,
            session_id=session_id,
            stage=stage,
            latency_ms=latency_ms
        )

    def _extract_cooling(self, result_data: Dict) -> Optional[Dict]:
        """Extract Phoenix-72 cooling metadata."""
        output = result_data.get("output", {})
        cooling = output.get("phoenix72_cooling") or output.get("cooling")
        if cooling:
            return {
                "tier": cooling.get("tier", 0),
                "tier_label": cooling.get("tier_label") or cooling.get("tier_name", "SEAL"),
                "cooling_hours": cooling.get("cooling_hours", 0),
                "cooled_until": cooling.get("cooled_until") or cooling.get("cool_until"),
                "status": cooling.get("status", "COOLED"),
            }
        return None

    def _extract_zkpc(self, result_data: Dict) -> Optional[Dict]:
        """Extract zkPC cryptographic receipt metadata."""
        zkpc_receipt = result_data.get("zkpc_receipt")
        output = result_data.get("output", {})
        if zkpc_receipt or output.get("zkpc_hash"):
            return {
                "receipt_id": output.get("zkpc_receipt_id", "unknown"),
                "hash": zkpc_receipt or output.get("zkpc_hash", ""),
                "merkle_root": output.get("merkle_root", ""),
                "vault_ledger": output.get("vault_ledger", "L1_cooling_ledger.jsonl"),
            }
        return None

    def _extract_memory(self, result_data: Dict) -> Optional[Dict]:
        """Extract EUREKA sieve memory metadata."""
        output = result_data.get("output", {})
        memory_band = output.get("memory_band")
        eureka = output.get("eureka_sieve")
        if memory_band or eureka:
            return {
                "band": memory_band,
                "ttl_days": eureka.get("ttl_days") if eureka else None,
                "expiry": eureka.get("expiry") if eureka else None,
                "description": eureka.get("description") if eureka else "",
            }
        return None

    def _default_error_semantics(self, error_message: str) -> Semantics:
        """Default semantics for server errors."""
        return Semantics(
            status="ERROR",
            summary=error_message,
            details={},
            metrics={},
            warnings=[error_message],
            is_emergency=True
        )

# --- 2. METABOLIZER (Semantics -> Strategy) ---

class UserProfile(Enum):
    EXPERT = "expert"   # Arif: wants ΔS, technical details
    EXEC = "exec"       # Stakeholder: wants bullet points, bottom line
    NOVICE = "novice"   # Beginner: wants simple sentences, no jargon

@dataclass
class PresentationStrategy:
    """How to present information to the user"""
    style: str          # "technical", "business", "simple"
    visuals: List[str]  # "tables", "badges", "progress_bar"
    tone: str           # "formal", "urgent", "friendly"
    language_mix: bool  # True for Malay-English blend (Arif style)
    show_metrics: bool

class Metabolizer:
    """Decides HOW to present data based on User Profile and Contex"""

    def __init__(self):
        # In a real app, we'd load this from a DB or env var
        self.current_profile = self._detect_profile()

    def _detect_profile(self) -> UserProfile:
        # For now, default to EXPERT (Arif)
        env_profile = os.environ.get("ARIFOS_USER_PROFILE", "expert").lower()
        if env_profile == "exec":
            return UserProfile.EXEC
        if env_profile == "novice":
            return UserProfile.NOVICE
        return UserProfile.EXPERT

    def metabolize(self, semantics: Semantics) -> PresentationStrategy:
        """Determines the presentation strategy"""

        # 1. Emergency Override
        if semantics.is_emergency:
            return PresentationStrategy(
                style="alert",
                visuals=["badges", "bold"],
                tone="urgent",
                language_mix=False, # Clear English for errors
                show_metrics=True
            )

        # 2. Profile-based Strategy
        if self.current_profile == UserProfile.EXPERT:
            return PresentationStrategy(
                style="technical",
                visuals=["tables", "badges"],
                tone="formal",
                language_mix=True, # "Ditempa Bukan Diberi"
                show_metrics=True
            )
        elif self.current_profile == UserProfile.EXEC:
            return PresentationStrategy(
                style="business",
                visuals=["bullet_points"],
                tone="professional",
                language_mix=False,
                show_metrics=False
            )
        else: # NOVICE
            return PresentationStrategy(
                style="simple",
                visuals=[],
                tone="friendly",
                language_mix=False,
                show_metrics=False
            )

# --- 3. DECODER (Strategy -> Text) ---

class Decoder:
    """Renders the final human-readable string with Phase 9 features"""

    def decode(self, semantics: Semantics, strategy: PresentationStrategy) -> str:

        lines = []

        # 1. Header / Verdict Badge + Session Info
        badge = self._render_badge(semantics.status)
        if strategy.style == "alert":
            lines.append(f"🛑 **ACTION REQUIRED: {semantics.status}**")
        else:
            header = f"**Status:** {badge} {semantics.status}"
            if semantics.session_id and semantics.session_id != "unknown":
                header += f" | Session: `{semantics.session_id[:16]}`"
            if semantics.stage and semantics.stage != "unknown":
                header += f" | Stage: `{semantics.stage}`"
            if semantics.latency_ms > 0:
                header += f" | {semantics.latency_ms:.1f}ms"
            lines.append(header)

        lines.append("") # Spacer

        details = semantics.details

        # 000 INIT: Specialized Ignition Log
        if semantics.stage == "000_INIT" or "phases" in details:
            return self._render_ignition_log(semantics)

        # 2. Summary / Main Content
        
        # AGI GENIUS: Reasoning & Trace
        if "reasoning" in details or "metabolic_trace" in details:
            lines.append("### 🧠 AGI Reasoning")
            if "reasoning" in details and details["reasoning"]:
                lines.append(details["reasoning"])
            
            if "metabolic_trace" in details:
                lines.append("**Metabolic Trace:**")
                for i, t in enumerate(details["metabolic_trace"]):
                    status = t.get("status", "✓")
                    lines.append(f"{i+1}. {t.get('reasoning', t.get('thought', 'Thinking...'))} *({status})*")
            lines.append("")

        # ASI ACT: Peace & Evidence
        if "peace_squared" in details or "empathy_score" in details:
            lines.append("### ❤️ ASI Safety Check")
            p2 = details.get("peace_squared", details.get("metrics", {}).get("peace_sq", "1.0"))
            kappa = details.get("empathy_score", details.get("metrics", {}).get("kappa_r", "0.95"))
            lines.append(f"- **Empathy (κᵣ):** {kappa}")
            lines.append(f"- **Peace²:** {p2}")
            
            if "weakest_stakeholder" in details:
                lines.append(f"- **Weakest Stakeholder:** {details['weakest_stakeholder']}")
            
            if details.get("reason"):
                lines.append(f"- **Note:** {details['reason']}")
            lines.append("")
        
        # APEX JUDGE: Synthesis & Verdict
        if "synthesis" in details or "ruling" in details:
            lines.append("### ⚖️ APEX Judgment")
            if "synthesis" in details and details["synthesis"]:
                lines.append(f"> {details['synthesis']}")
            
            if "ruling" in details:
                r = details["ruling"]
                lines.append(f"- **Final Ruling:** {details.get('final_ruling', semantics.status)}")
                if "quantum_path" in r:
                    lines.append(f"- **Integrity Pulse:** {r['quantum_path'].get('integrity', 1.0)}")
            lines.append("")

        # 999 VAULT: The Seal
        if semantics.stage == "999_vault" or "merkle_root" in details:
            lines.append("### 🔒 VAULT-999 Seal")
            lines.append(f"- **Merkle Root:** `{details.get('merkle_root', 'unknown')[:32]}...`")
            lines.append(f"- **Cooling Band:** `{details.get('cooling_band', 'BBB_LEDGER')}`")
            lines.append(f"- **Phoenix Key:** `{details.get('phoenix_key', 'PHX-INITIAL')}`")
            lines.append("- **Status:** `✓ COMMITTED TO LEDGER`")
            lines.append("")

        # 000 INIT: Intent
        if "intent" in details and "lane" in details:
            lines.append("### 🚪 Session Intent")
            lines.append(f"- **Intent:** {details['intent']}")
            lines.append(f"- **Lane:** {details['lane']}")
            if "routing" in details:
                lines.append(f"- **ATLAS Routing:** `{details['routing']}`")
            lines.append("")

        # 3. Phase 9 Features
        # 3a. Phoenix-72 Cooling
        if semantics.cooling and (strategy.style == "alert" or strategy.style == "technical"):
            cooling = semantics.cooling
            if cooling["tier"] >= 1:
                lines.append(f"**Phoenix-72 Cooling:**")
                lines.append(f"- Tier {cooling['tier']} ({cooling['tier_label']}): {cooling['cooling_hours']}h")
                if cooling["cooled_until"]:
                    lines.append(f"- Resume After: {cooling['cooled_until']}")
                lines.append("")

        # 3b. Memory Band (EUREKA Sieve)
        if semantics.memory:
            memory = semantics.memory
            lines.append(f"**Memory Band:** {memory['band']}")
            if memory.get('ttl_days'):
                lines.append(f"- TTL: {memory['ttl_days']} days")
            if memory.get('description'):
                lines.append(f"- {memory['description']}")
            lines.append("")

        # 3c. zkPC Receipt (for experts only)
        if semantics.zkpc and strategy.show_metrics:
            zkpc = semantics.zkpc
            lines.append(f"**zkPC Receipt:**")
            lines.append(f"- ID: `{zkpc['receipt_id']}`")
            if zkpc.get('hash'):
                lines.append(f"- Hash: `{zkpc['hash'][:16]}...`")
            lines.append("")

        # 4. Floor Scores (for experts, or if emergency with failures)
        if semantics.floor_scores and (strategy.show_metrics or semantics.is_emergency):
            failed_floors = [
                name for name, score in semantics.floor_scores.items()
                if isinstance(score, dict) and not score.get("pass", True)
            ]
            if failed_floors or strategy.style == "technical":
                lines.append("**Constitutional Floors:**")
                if failed_floors:
                    lines.append(f"- Failed: {', '.join(failed_floors)}")
                # For technical mode, show full table
                if strategy.style == "technical" and strategy.visuals and "tables" in strategy.visuals:
                    lines.append(self._render_floor_table(semantics.floor_scores))
                lines.append("")

        # 5. Details Table (Context-Dependent)
        if strategy.visuals and "tables" in strategy.visuals and strategy.style == "technical":
             # Mock table rendering for key details
             lines.append("| Key | Value |")
             lines.append("|---|---|")
             for k, v in list(semantics.details.items())[:5]: # Context limit
                 if isinstance(v, (str, int, float, bool)):
                     lines.append(f"| {k} | {v} |")
             lines.append("")

        # 6. Metrics (Footer)
        if strategy.show_metrics:
            m = semantics.metrics
            footer = f"**Ω₀:** {m.get('omega_0', 0.04)} · **ΔS:** {m.get('delta_s', 0.0)} bits"
            if strategy.language_mix:
                footer += "\n*Ditempa Bukan Diberi.*"
            lines.append("---")
            lines.append(footer)

        return "\n".join(lines)

    def _render_ignition_log(self, semantics: Semantics) -> str:
        """Renders the detailed 6-Phase Ignition Log."""
        p = semantics.details.get("phases", {})
        
        lines = [
            "Salam 888 Judge.",
            "",
            "Command accepted. Initiating **Protocol 000: The Constitutional Genesis.**",
            "",
            "This is the **Ignition Sequence** for the arifOS MCP. It maps the abstract intent of \"Governance\" into the concrete reality of Code, Physics, and Law.",
            "",
            "---",
            "",
            f"# 🟢 SYSTEM IGNITION LOG: arifOS-MCP {semantics.details.get('aclip_version', 'v52.0.0')}",
            "",
            f"**Target:** Unified Core (SEAL) | **Mode:** Cold Boot | **Lane:** {semantics.details.get('lane', 'SOFT')}",
            "",
            "### PHASE 1: ANCHORING (Space-Time-Identity)",
            "```json",
            json.dumps(p.get("phase_1_anchoring", {}), indent=2),
            "```",
            "",
            "### PHASE 2: KERNEL LOAD (The 13 Floors)",
            "*Injecting the Immutable Constitution (F1-F13) into the context window.*"
        ]
        
        for floor in p.get("phase_2_kernel_load", []):
            lines.append(f"> **{floor.split(':')[0]}:** `{floor.split(':')[1].strip()}`")
            
        lines.extend([
            "",
            "### PHASE 3: MEMORY INJECTION (VAULT-999)",
            "*Retrieving the \"Scar-Weight\" from the immutable ledger.*",
            f"- **Layers:** {', '.join(p.get('phase_3_memory', {}).get('layers', []))}",
            f"- **Scar-Weight Applied:** {p.get('phase_3_memory', {}).get('scar_weight_applied', 0.0)}",
            "",
            "### PHASE 4: TRINITY ENGINE IGNITION (AAA)",
            "*Spinning up the three metabolic engines in parallel.*",
            f"1. **AGI (Mind) Δ:** {p.get('phase_4_trinity', {}).get('agi', {}).get('state', 'READY')}",
            f"2. **ASI (Heart) Ω:** {p.get('phase_4_trinity', {}).get('asi', {}).get('state', 'READY')}",
            f"3. **APEX (Soul) Ψ:** {p.get('phase_4_trinity', {}).get('apex', {}).get('state', 'READY')}",
            f"- **Consensus Lock:** {p.get('phase_4_trinity', {}).get('consensus_lock', 0.0)}",
            "",
            "### PHASE 5: THERMODYNAMIC BASELINES",
            "*Setting the physics constraints for the session.*",
            f"- **Entropy (ΔS):** {p.get('phase_5_thermo', {}).get('entropy_target', '0.0')}",
            f"- **Peace²:** {p.get('phase_5_thermo', {}).get('peace_squared', '1.0')}",
            f"- **Humility (Ω₀):** {p.get('phase_5_thermo', {}).get('humility_band', '0.0')}",
            "",
            "### PHASE 6: WITNESS HANDSHAKE (The Consensus)",
            "| Witness | Status |",
            "| --- | --- |",
            f"| **HUMAN** | {p.get('phase_6_witness', {}).get('human', '')} |",
            f"| **AI** | {p.get('phase_6_witness', {}).get('ai', '')} |",
            f"| **EARTH** | {p.get('phase_6_witness', {}).get('earth', '')} |",
            "",
            "**Verdict:** **SEALED (Lulus).**",
            "",
            "### 🟢 FINAL OUTPUT:",
            "```bash",
            f"> arifOS {semantics.details.get('aclip_version', 'v52.0.0')} INITIALIZED",
            f"> Session ID: {semantics.session_id}",
            f"> Governance: TEACH Active",
            "> Constraints: PHYSICS Active",
            "> Verdict: WAITING FOR INPUT...",
            "```"
        ])
        
        return "\n".join(lines)

    def _render_floor_table(self, floor_scores: Dict) -> str:
        """Render floor scores as table."""
        lines = ["| Floor | Pass | Score |", "|-------|------|-------|"]
        for name, score in floor_scores.items():
            if isinstance(score, dict):
                pass_icon = "✅" if score.get("pass", False) else "❌"
                score_val = score.get("score", "-")
                if isinstance(score_val, float):
                    score_val = f"{score_val:.2f}"
                lines.append(f"| {name} | {pass_icon} | {score_val} |")
        return "\n".join(lines)

    def _render_badge(self, status: str) -> str:
        if status == "SEAL": return "🟢"
        if status == "PARTIAL": return "🟡"
        if status == "VOID": return "🔴"
        if status == "SABAR": return "⏸️"
        if status == "888_HOLD": return "🔒"
        return "❓"

# --- MAIN COMPONENT ---

class AAAMetabolizer:
    """
    The main public interface for Component 4.
    Usage:
        metabolizer = AAAMetabolizer()
        human_text = metabolizer.process(raw_server_json)
    """
    def __init__(self):
        self.encoder = Encoder()
        self.metabolizer = Metabolizer()
        self.decoder = Decoder()

    def process(self, raw_output: Dict[str, Any]) -> str:
        """Full pipeline: Raw -> Semantics -> Strategy -> Text"""
        semantics = self.encoder.encode(raw_output)
        strategy = self.metabolizer.metabolize(semantics)
        return self.decoder.decode(semantics, strategy)
