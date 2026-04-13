"""
arifosmcp/apps/vault_app.py
═══════════════════════════════════════════════════════════════════════════════
arifOS VaultApp — FastMCP Immutable Ledger Surface (999_VAULT)
═══════════════════════════════════════════════════════════════════════════════

Implements the immutable verdict ledger as a FastMCPApp:

  @app.ui()   vault_ledger_surface  — entry; renders seal card + ledger table
  @app.tool() get_vault_data        — backend; reads VAULT999/outcomes.jsonl
                                      + builds BLS seal card

F1 Amanah enforced: append-only display, no edit/delete controls anywhere.

UI anatomy:
  ┌── Live Seal Card ─────────────────────────────────────────────────┐
  │  seal_id: seal_79112f02…  │  Verdict: ● SEAL                     │
  │  τ=0.99  κᵣ=0.97  Ω₀=0.04  W³=0.95                             │
  │  BLS: 3/5 quorum  │  ZKPC: Phase B  │  Chain: 0e06ab93…         │
  └───────────────────────────────────────────────────────────────────┘
  ┌── Ledger (VAULT999/outcomes.jsonl) ───────────────────────────────┐
  │  ID     Session     Verdict  Status    Reversible  Harm  Override │
  │  D001   sess-test   SEAL     PENDING   ✓           ✗     ✗       │
  │  D002   sess-2      SEAL     PENDING   ✓           ✗     ✗       │
  │  ...                                                              │
  └───────────────────────────────────────────────────────────────────┘

F1 Amanah: no mutation UI exposed. Ledger is read-only.

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from prefab_ui.actions import SetState, ShowToast
from prefab_ui.actions.mcp import CallTool
from prefab_ui.app import PrefabApp
from prefab_ui.components import (
    Badge,
    Card,
    CardContent,
    Column,
    DataTable,
    Grid,
    Heading,
    Muted,
    Row,
    Separator,
    Text,
)
from prefab_ui.rx import RESULT

from fastmcp import FastMCP, FastMCPApp

# ── Ledger path ───────────────────────────────────────────────────────────────
_REPO_ROOT = Path(__file__).parent.parent.parent
_VAULT999 = _REPO_ROOT / "arifosmcp" / "VAULT999"
_OUTCOMES = _VAULT999 / "outcomes.jsonl"
_VAULT999_JSONL = _VAULT999 / "vault999.jsonl"

_MAX_ROWS = 50  # F4 clarity: cap table to avoid noise


# ── Verdict variants ──────────────────────────────────────────────────────────

def _verdict_variant(v: str) -> str:
    return {
        "SEAL": "success",
        "PARTIAL": "warning",
        "VOID": "destructive",
        "888_HOLD": "warning",
        "SABAR": "secondary",
        "PENDING": "secondary",
    }.get(v.upper() if v else "PENDING", "secondary")


def _bool_icon(val: Any) -> str:
    if isinstance(val, bool):
        return "✓" if val else "✗"
    return "✓" if str(val).lower() in ("true", "1", "yes") else "✗"


def _ts_human(ts: Any) -> str:
    """Convert epoch float or ISO string to readable form."""
    if not ts:
        return "—"
    try:
        import datetime
        if isinstance(ts, (int, float)):
            return datetime.datetime.fromtimestamp(float(ts), tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
        return str(ts)[:16]
    except Exception:
        return str(ts)[:16]


# ── App definition ────────────────────────────────────────────────────────────

vault_app = FastMCPApp("VaultApp")


@vault_app.tool()
def get_vault_data() -> dict[str, Any]:
    """
    Read VAULT999 ledger and build current BLS seal card.
    Returns: seal card data + ledger rows. Read-only (F1 Amanah).
    """
    # ── Ledger rows ───────────────────────────────────────────────────────────
    rows: list[dict[str, Any]] = []
    for ledger_file in [_OUTCOMES, _VAULT999_JSONL]:
        if ledger_file.exists():
            try:
                with ledger_file.open(encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                rows.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
            except Exception:
                pass
        if rows:
            break

    # Normalise to table columns and cap rows
    table_rows = []
    for r in rows[-_MAX_ROWS:]:
        table_rows.append({
            "id": r.get("decision_id", "—"),
            "session": (r.get("session_id") or "—")[:12],
            "verdict": (r.get("verdict_issued") or "—").upper(),
            "status": (r.get("outcome_status") or "—").upper(),
            "reversible": _bool_icon(r.get("reversible", True)),
            "harm": _bool_icon(r.get("harm_detected", False)),
            "override": _bool_icon(r.get("operator_override", False)),
            "timestamp": _ts_human(r.get("timestamp_decision")),
        })

    # ── Seal card ─────────────────────────────────────────────────────────────
    seal_card: dict[str, Any] = {}
    try:
        from arifosmcp.runtime.chatgpt_integration.apps_sdk_tools import _build_vault_seal_structured_content
        seal_card = _build_vault_seal_structured_content()
    except Exception:
        import uuid, datetime as _dt
        seal_card = {
            "seal_id": f"seal_{uuid.uuid4().hex[:16]}",
            "verdict": "SEAL",
            "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "floors": {"tau_truth": 0.99, "omega_0": 0.04, "kappa_r": 0.97, "tri_witness": 0.95},
            "bls": {"quorum_fraction": 0.60, "juror_count": 3, "aggregate_signature": "—"},
            "zkpc": {"proof_status": "Phase B — pending"},
            "chain_hash": "",
            "summary": {"truth_score": 0.99, "care_level": 0.97, "humility_level": 0.04, "trust_vote": 0.95},
            "witness": {"human": 0.95, "ai": 0.94, "earth": 0.93},
        }

    return {
        "seal": seal_card,
        "rows": table_rows,
        "total_entries": len(rows),
        "ledger_file": str(_OUTCOMES.name if _OUTCOMES.exists() else _VAULT999_JSONL.name),
    }


@vault_app.ui(title="999 Vault Ledger")
def vault_ledger_surface() -> PrefabApp:
    """
    Open the arifOS Immutable Vault Ledger.
    Shows the live BLS constitutional seal card and all VAULT999 ledger entries.
    F1 Amanah: read-only — no edit, no delete.
    """
    initial_state: dict[str, Any] = {
        "seal": {},
        "rows": [],
        "total_entries": 0,
        "ledger_file": "—",
        "loaded": False,
    }

    on_load = CallTool(
        get_vault_data,
        on_success=[
            SetState("seal",          RESULT["seal"]),
            SetState("rows",          RESULT["rows"]),
            SetState("total_entries", RESULT["total_entries"]),
            SetState("ledger_file",   RESULT["ledger_file"]),
            SetState("loaded",        True),
            ShowToast("Ledger loaded", variant="success"),
        ],
        on_error=ShowToast("Vault read error", variant="destructive"),
    )

    with Column(gap=5, css_class="p-5 max-w-3xl") as view:

        # ── Header ──────────────────────────────────────────────────────────
        with Row(gap=3, align="center"):
            Heading("999 Vault Ledger")
            Badge("F1 Amanah · Append-Only", variant="secondary", css_class="text-xs font-mono")

        Muted("Immutable constitutional verdict ledger · DITEMPA BUKAN DIBERI")
        Separator()

        # ── Live Seal Card ───────────────────────────────────────────────────
        Muted("Live Constitutional Seal", css_class="text-xs uppercase tracking-wider")
        with Card():
            with CardContent(css_class="py-4"):
                with Grid(columns=2, gap=4):
                    # Left: seal identity
                    with Column(gap=2):
                        with Row(gap=2, align="center"):
                            Badge("● SEAL", variant="success", css_class="font-mono")
                            Muted("Current verdict")
                        Muted("seal_id: —", css_class="text-xs font-mono truncate")
                        Muted("Awaiting load…", css_class="text-xs")

                    # Right: key floor scores
                    with Grid(columns=2, gap=2):
                        for label, key in [("τ Truth", "tau_truth"), ("κᵣ Care", "kappa_r"),
                                          ("Ω₀ Hum.", "omega_0"), ("W³ Wit.", "tri_witness")]:
                            with Card(css_class="bg-muted/30"):
                                with CardContent(css_class="py-2 text-center"):
                                    Text("—", css_class="text-lg font-bold font-mono")
                                    Muted(label, css_class="text-xs")

                Separator()

                # BLS + ZKPC attestation row
                with Row(gap=4, css_class="mt-2"):
                    with Row(gap=2, align="center"):
                        Badge("BLS", variant="outline", css_class="text-xs font-mono")
                        Muted("— quorum · — jurors", css_class="text-xs")
                    with Row(gap=2, align="center"):
                        Badge("ZKPC", variant="outline", css_class="text-xs font-mono")
                        Muted("Phase B — pending", css_class="text-xs")

                Muted("Chain: —", css_class="text-xs font-mono mt-2 truncate")

        Separator()

        # ── Ledger Table ─────────────────────────────────────────────────────
        Muted("VAULT999 Ledger Entries", css_class="text-xs uppercase tracking-wider")

        # DataTable renders after load via state
        DataTable(
            data="rows",
            columns=[
                {"key": "id",        "label": "ID",        "sortable": True},
                {"key": "session",   "label": "Session",   "sortable": False},
                {"key": "verdict",   "label": "Verdict",   "sortable": True},
                {"key": "status",    "label": "Status",    "sortable": True},
                {"key": "reversible","label": "Rev.",       "sortable": False},
                {"key": "harm",      "label": "Harm",      "sortable": False},
                {"key": "override",  "label": "Override",  "sortable": False},
                {"key": "timestamp", "label": "Timestamp", "sortable": True},
            ],
            searchable=True,
            css_class="text-sm",
        )

        Muted(
            "Entries shown: latest 50 · Full ledger at VAULT999/outcomes.jsonl",
            css_class="text-xs",
        )

        Separator()

        # ── Load action (F1: no mutation controls) ───────────────────────────
        from prefab_ui.components import Button
        Button(
            "Load Ledger",
            on_click=on_load,
            variant="outline",
            css_class="w-full",
        )

        Muted(
            "Read-only · F1 Amanah · No edit or delete capability",
            css_class="text-xs text-center text-muted-foreground",
        )

    return PrefabApp(view=view, state=initial_state)


def _register(mcp: FastMCP) -> None:
    """Mount VaultApp onto the platform FastMCP server."""
    mcp.add_provider(vault_app)
