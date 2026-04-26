"""arifOS Command Center MCP App.

One cockpit. Separate chambers. Judge above action.

Architecture:
- FastMCPApp ("arifOS Command Center") owns the UI + app-scoped backend tools.
- Only command_center() is a visible UI entry point for the model.
- All Forge, Vault, Gateway operations are simulated (dry-run) in v0.1.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

from arifosmcp.apps.command_center.governance import classify_risk, hash_preview, judge_candidate
from arifosmcp.apps.command_center.mock_kernel import MOCK_VAULT_ENTRIES
from arifosmcp.apps.command_center.models import (
    ForgeDryRun,
    GatewayHandshake,
    JudgeVerdict,
    OpsVitals,
    SessionStatus,
    VaultDrySeal,
    VaultList,
)
from arifosmcp.apps.command_center.state import get_state
from fastmcp import FastMCP
from fastmcp.apps import FastMCPApp
from prefab_ui.actions import SetState
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Button,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
    Column,
    Heading,
    Input,
    Metric,
    Row,
    Separator,
    Tab,
    Tabs,
    Text,
    Textarea,
)

# ---------------------------------------------------------------------------
# Safety constants — red-team hardening
# ---------------------------------------------------------------------------
MAX_MANIFEST_LENGTH = 10_000  # 10KB
MAX_CANDIDATE_LENGTH = 10_000  # 10KB
MAX_PAYLOAD_LENGTH = 10_000  # 10KB
MAX_AGENT_NAME_LENGTH = 256


def _truncate(text: str, max_len: int) -> str:
    """Safely truncate text with an ellipsis indicator."""
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


# ---------------------------------------------------------------------------
# App definition
# ---------------------------------------------------------------------------
command_center_app = FastMCPApp("arifOS Command Center")

# ---------------------------------------------------------------------------
# Backend tools — app-scoped, not general model-facing actions
# ---------------------------------------------------------------------------


@command_center_app.tool()
def session_status() -> dict:
    """Return current constitutional session status."""
    state = get_state()
    state.session_count += 1
    return SessionStatus().model_dump()


@command_center_app.tool()
def ops_vitals() -> dict:
    """Return simulated thermodynamic health telemetry."""
    state = get_state()
    state.ops_reads += 1
    return OpsVitals().model_dump()


@command_center_app.tool()
def judge_action(candidate: str) -> dict:
    """Adjudicate a candidate action against constitutional floors F1–F13.

    Returns SEAL, SABAR, HOLD, or VOID. Never permits real execution in v0.1.
    Large or empty inputs fail closed to HOLD.
    """
    state = get_state()
    state.judge_calls += 1
    if not isinstance(candidate, str):
        candidate = str(candidate) if candidate is not None else ""
    candidate = _truncate(candidate.strip(), MAX_CANDIDATE_LENGTH)
    result = judge_candidate(candidate)
    return JudgeVerdict(**result).model_dump()


@command_center_app.tool()
def forge_dry_run(manifest: str) -> dict:
    """Simulate a forge execution without changing anything.

    v0.1: dry_run only. No build, no deploy, no file write.
    """
    state = get_state()
    state.forge_dry_runs += 1

    risk = classify_risk(manifest)
    reversibility = "uncertain" if risk in {"high", "critical"} else "reversible"

    manifest = _truncate(manifest, MAX_MANIFEST_LENGTH)
    summary = f"Would simulate: {manifest[:120]}"
    if len(manifest) > 120:
        summary += "..."

    return ForgeDryRun(
        mode="dry_run",
        would_execute=False,
        manifest_summary=summary,
        reversibility=reversibility,
        required_verdict="SEAL",
        status="simulated",
    ).model_dump()


@command_center_app.tool()
def gateway_handshake(target_agent: str) -> dict:
    """Simulate a constitutional cross-agent handshake.

    No real network traffic. No credential exchange.
    """
    state = get_state()
    state.gateway_handshakes += 1
    if not isinstance(target_agent, str):
        target_agent = str(target_agent) if target_agent is not None else ""
    target_agent = _truncate(target_agent.strip(), MAX_AGENT_NAME_LENGTH)
    return GatewayHandshake(
        target_agent=target_agent,
        handshake="simulated",
        constitution_hash_required=True,
        rogue_agent_protection=True,
        status="pending_trust_verification",
    ).model_dump()


@command_center_app.tool()
def vault_list() -> dict:
    """Return mock vault audit entries.

    v0.1: synthetic data only. No ledger read from VAULT999.
    """
    return VaultList(entries=MOCK_VAULT_ENTRIES).model_dump()


@command_center_app.tool()
def vault_dry_seal(payload: str) -> dict:
    """Simulate a vault seal without permanent write.

    v0.1: not_written. No append to VAULT999.
    """
    state = get_state()
    state.vault_dry_seals += 1
    if not isinstance(payload, str):
        payload = str(payload) if payload is not None else ""
    payload = _truncate(payload, MAX_PAYLOAD_LENGTH)
    return VaultDrySeal(
        mode="dry_seal",
        permanent=False,
        payload_hash_preview=hash_preview(payload),
        status="not_written",
    ).model_dump()


# ---------------------------------------------------------------------------
# Visible UI entry point
# ---------------------------------------------------------------------------


@command_center_app.ui()
def command_center() -> PrefabApp:
    """Open arifOS Command Center."""

    # Header
    header = Column(
        children=[
            Heading(content="arifOS Command Center", level=1),
            Text(content="One cockpit. Separate chambers. Judge above action.", italic=True),
            Row(
                children=[
                    Badge(label="v0.1 DRY-RUN ONLY", variant="warning"),
                    Badge(label="F1 Amanah Active", variant="success"),
                ],
                gap=2,
            ),
            Separator(spacing=2),
        ],
        gap=2,
    )

    # ---------- Session Tab ----------
    session_tab = Tab(
        title="Session",
        value="session",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="Constitutional Session")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Actor: {{ session_actor }}", bold=True),
                                    Text(
                                        content="Constitution: {{ session_constitution }}",
                                        bold=True,
                                    ),
                                    Text(content="Stage: {{ session_stage }}", bold=True),
                                    Text(content="Lane: {{ session_lane }}", bold=True),
                                    Text(content="Authority: {{ session_authority }}", bold=True),
                                    Badge(
                                        label="{{ session_sealed }}",
                                        variant="{{ session_sealed == 'true' ? 'success' : 'secondary' }}",  # noqa: E501
                                    ),
                                    Button(
                                        label="Refresh Session",
                                        variant="outline",
                                        on_click=CallTool(
                                            "session_status",
                                            on_success=[
                                                SetState("session_actor", "{{ $result.actor_id }}"),
                                                SetState(
                                                    "session_constitution",
                                                    "{{ $result.constitution_id }}",
                                                ),
                                                SetState("session_stage", "{{ $result.stage }}"),
                                                SetState("session_lane", "{{ $result.lane }}"),
                                                SetState("session_sealed", "{{ $result.sealed }}"),
                                                SetState(
                                                    "session_authority", "{{ $result.authority }}"
                                                ),
                                            ],
                                        ),
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Ops Tab ----------
    ops_tab = Tab(
        title="Ops",
        value="ops",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="Thermodynamic Vitals")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Row(
                                        children=[
                                            Metric(
                                                label="G Score",
                                                value="{{ ops_g }}",
                                                description="Genius coefficient",
                                            ),
                                            Metric(
                                                label="ΔS",
                                                value="{{ ops_delta_s }}",
                                                description="Entropy delta",
                                            ),
                                            Metric(
                                                label="Ω",
                                                value="{{ ops_omega }}",
                                                description="Human impact load",
                                            ),
                                            Metric(
                                                label="Ψ",
                                                value="{{ ops_psi }}",
                                                description="Paradox tension",
                                            ),
                                        ],
                                        gap=4,
                                    ),
                                    Badge(
                                        label="Status: {{ ops_status }}",
                                        variant="{{ ops_status == 'stable' ? 'success' : 'destructive' }}",  # noqa: E501
                                    ),
                                    Button(
                                        label="Refresh Vitals",
                                        variant="outline",
                                        on_click=CallTool(
                                            "ops_vitals",
                                            on_success=[
                                                SetState("ops_g", "{{ $result.g_score }}"),
                                                SetState("ops_delta_s", "{{ $result.delta_S }}"),
                                                SetState("ops_omega", "{{ $result.omega }}"),
                                                SetState("ops_psi", "{{ $result.psi_le }}"),
                                                SetState("ops_status", "{{ $result.status }}"),
                                            ],
                                        ),
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Judge Tab ----------
    judge_tab = Tab(
        title="Judge",
        value="judge",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="888 Judge — Constitutional Review")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(
                                        content="Describe the candidate action for constitutional review:"  # noqa: E501
                                    ),
                                    Input(
                                        name="judge_candidate",
                                        placeholder="e.g., restart the production database",
                                    ),
                                    Button(
                                        label="Review Action",
                                        variant="secondary",
                                        on_click=CallTool(
                                            "judge_action",
                                            arguments={"candidate": "{{ judge_candidate }}"},
                                            on_success=[
                                                SetState("judge_verdict", "{{ $result.verdict }}"),
                                                SetState("judge_risk", "{{ $result.risk_tier }}"),
                                                SetState("judge_reason", "{{ $result.reason }}"),
                                                SetState(
                                                    "judge_human",
                                                    "{{ $result.human_decision_required }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Verdict:", bold=True),
                                    Badge(
                                        label="{{ judge_verdict }}",
                                        variant="{{ judge_verdict == 'SEAL' ? 'success' : (judge_verdict == 'SABAR' ? 'warning' : 'destructive') }}",  # noqa: E501
                                    ),
                                    Text(content="Risk Tier: {{ judge_risk }}", bold=True),
                                    Text(content="Reason: {{ judge_reason }}", italic=True),
                                    Badge(
                                        label="{{ judge_human == 'true' ? 'Human Decision REQUIRED' : 'No human decision required' }}",  # noqa: E501
                                        variant="{{ judge_human == 'true' ? 'destructive' : 'secondary' }}",  # noqa: E501
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Forge Tab ----------
    forge_tab = Tab(
        title="Forge",
        value="forge",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="010 Forge — Metabolic Execution")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Badge(label="DRY RUN ONLY", variant="warning"),
                                    Badge(
                                        label="No files changed. No deployment performed.",
                                        variant="secondary",
                                    ),
                                    Textarea(
                                        name="forge_manifest",
                                        placeholder="Paste manifest JSON or description here...",
                                        rows=4,
                                    ),
                                    Button(
                                        label="Dry Run Forge",
                                        variant="outline",
                                        on_click=CallTool(
                                            "forge_dry_run",
                                            arguments={"manifest": "{{ forge_manifest }}"},
                                            on_success=[
                                                SetState("forge_mode", "{{ $result.mode }}"),
                                                SetState(
                                                    "forge_summary",
                                                    "{{ $result.manifest_summary }}",
                                                ),
                                                SetState(
                                                    "forge_reversibility",
                                                    "{{ $result.reversibility }}",
                                                ),
                                                SetState("forge_status", "{{ $result.status }}"),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Mode: {{ forge_mode }}", bold=True),
                                    Text(content="Summary: {{ forge_summary }}", italic=True),
                                    Text(
                                        content="Reversibility: {{ forge_reversibility }}",
                                        bold=True,
                                    ),
                                    Badge(
                                        label="Status: {{ forge_status }}",
                                        variant="{{ forge_status == 'simulated' ? 'success' : 'default' }}",  # noqa: E501
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Gateway Tab ----------
    gateway_tab = Tab(
        title="Gateway",
        value="gateway",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="666 Gateway — A2A Mesh")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Text(content="Target agent for constitutional handshake:"),
                                    Input(
                                        name="gateway_target",
                                        placeholder="e.g., geox-mcp, wealth-mcp, a-forge",
                                    ),
                                    Button(
                                        label="Simulate Handshake",
                                        variant="outline",
                                        on_click=CallTool(
                                            "gateway_handshake",
                                            arguments={"target_agent": "{{ gateway_target }}"},
                                            on_success=[
                                                SetState("gw_target", "{{ $result.target_agent }}"),
                                                SetState("gw_status", "{{ $result.status }}"),
                                                SetState(
                                                    "gw_hash_req",
                                                    "{{ $result.constitution_hash_required }}",
                                                ),
                                                SetState(
                                                    "gw_rogue",
                                                    "{{ $result.rogue_agent_protection }}",
                                                ),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Target: {{ gw_target }}", bold=True),
                                    Text(content="Status: {{ gw_status }}", italic=True),
                                    Badge(
                                        label="Hash Required: {{ gw_hash_req }}",
                                        variant="{{ gw_hash_req == 'true' ? 'success' : 'warning' }}",  # noqa: E501
                                    ),
                                    Badge(
                                        label="Rogue Protection: {{ gw_rogue }}",
                                        variant="{{ gw_rogue == 'true' ? 'success' : 'warning' }}",
                                    ),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # ---------- Vault Tab ----------
    vault_tab = Tab(
        title="Vault",
        value="vault",
        children=[
            Card(
                children=[
                    CardHeader(
                        children=[CardTitle(content="999 Vault — Immutable Ledger")],
                    ),
                    CardContent(
                        children=[
                            Column(
                                children=[
                                    Badge(
                                        label="Dry seal only. No permanent ledger write.",
                                        variant="warning",
                                    ),
                                    Button(
                                        label="List Mock Vault",
                                        variant="outline",
                                        on_click=CallTool(
                                            "vault_list",
                                            on_success=[
                                                SetState(
                                                    "vault_entries_json", "{{ $result.entries }}"
                                                ),
                                            ],
                                        ),
                                    ),
                                    Text(
                                        content="Mock Entries (raw): {{ vault_entries_json }}",
                                        code=True,
                                    ),
                                    Separator(),
                                    Text(content="Payload to dry-seal:"),
                                    Textarea(
                                        name="vault_payload",
                                        placeholder="Enter payload to hash and preview...",
                                        rows=3,
                                    ),
                                    Button(
                                        label="Dry Seal",
                                        variant="secondary",
                                        on_click=CallTool(
                                            "vault_dry_seal",
                                            arguments={"payload": "{{ vault_payload }}"},
                                            on_success=[
                                                SetState("seal_mode", "{{ $result.mode }}"),
                                                SetState(
                                                    "seal_hash",
                                                    "{{ $result.payload_hash_preview }}",
                                                ),
                                                SetState(
                                                    "seal_permanent", "{{ $result.permanent }}"
                                                ),
                                                SetState("seal_status", "{{ $result.status }}"),
                                            ],
                                        ),
                                    ),
                                    Separator(),
                                    Text(content="Mode: {{ seal_mode }}", bold=True),
                                    Text(content="Hash Preview: {{ seal_hash }}", code=True),
                                    Badge(
                                        label="Permanent: {{ seal_permanent }}",
                                        variant="{{ seal_permanent == 'true' ? 'destructive' : 'success' }}",  # noqa: E501
                                    ),
                                    Text(content="Status: {{ seal_status }}", italic=True),
                                ],
                                gap=2,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    # Main tabs container
    chambers = Tabs(
        value="session",
        children=[session_tab, ops_tab, judge_tab, forge_tab, gateway_tab, vault_tab],
    )

    return PrefabApp(
        title="arifOS Command Center",
        view=Column(
            children=[header, chambers],
            gap=4,
        ),
        state={
            # Session defaults
            "session_actor": "—",
            "session_constitution": "—",
            "session_stage": "—",
            "session_lane": "—",
            "session_sealed": "false",
            "session_authority": "—",
            # Ops defaults
            "ops_g": "—",
            "ops_delta_s": "—",
            "ops_omega": "—",
            "ops_psi": "—",
            "ops_status": "—",
            # Judge defaults
            "judge_verdict": "—",
            "judge_risk": "—",
            "judge_reason": "—",
            "judge_human": "false",
            # Forge defaults
            "forge_mode": "—",
            "forge_summary": "—",
            "forge_reversibility": "—",
            "forge_status": "—",
            # Gateway defaults
            "gw_target": "—",
            "gw_status": "—",
            "gw_hash_req": "false",
            "gw_rogue": "false",
            # Vault defaults
            "vault_entries_json": "[]",
            "seal_mode": "—",
            "seal_hash": "—",
            "seal_permanent": "false",
            "seal_status": "—",
        },
    )


def _register(mcp: FastMCP) -> None:
    """Mount arifOS Command Center onto the platform FastMCP server."""
    mcp.add_provider(command_center_app)
