"""
arifOS Resources — Alignment Gap Closure (2026-08-05)
═══════════════════════════════════════════════════════

Four resources that the provenance-hardened prompts reference but were not
on the MCP surface. Without these, the WITNESS→JUDGE→SEAL provenance gates
would fail every agent that calls them.

  arifos://epistemic   — Epistemic label ontology (OBS/DER/INT/SPEC + provenance rules)
  arifos://floors       — All 13 floors as a list (complement to floor/{fid} template)
  arifos://affordances  — Tool affordances (action class, blast radius, reversibility)
  arifos://vault/head   — VAULT999 chain head (static, not template-parameterized)

DITEMPA BUKAN DIBERI.
"""

from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

from fastmcp import FastMCP
from fastmcp.resources.types import TextResource

logger = logging.getLogger(__name__)

# ══════════════════════════════════════════════════════════════════════════════
# arifos://epistemic — Epistemic label ontology
# ══════════════════════════════════════════════════════════════════════════════

EPISTEMIC_TEXT = """\
# arifOS Epistemic Label Ontology — F2 TRUTH

## Labels

| Label | Meaning | Confidence Band | Origin |
|-------|---------|-----------------|--------|
| **OBS** | Directly observed / measured | 0.85–0.90 | Sensor, probe, health endpoint, filesystem read |
| **DER** | Computed from OBS evidence | 0.70–0.85 | Formula, transform, aggregation of OBS inputs |
| **INT** | Interpreted / inferred | 0.50–0.70 | Model output, abductive reasoning, pattern detection |
| **SPEC** | Speculative / hypothesized | 0.20–0.50 | Projection, forecast, "what if" |
| **UNKNOWN** | No evidence available | 0.00–0.20 | Admitted ignorance — no fabrication |

## Provenance Rule (binding F2)

Labels MUST originate at data INGRESS — not at model output time.
Every claim carries:
  - provenance_source:  [tool_name + endpoint + iso_timestamp]
  - confidence:         [0.0–1.0], capped at 0.90 for OBS
  - staleness_seconds:  [int], age of data at observation time
  - epistemic_tag:      OBS|DER|INT|SPEC — assigned at retrieval

Post-hoc labeling (model generates tag at output time without retrieval provenance) → F2 VOID.
A label without provenance_source is not a label — it is decoration.

## Hard Caps

- Maximum confidence: 0.90 (Ω₀ ∈ [0.03, 0.05])
- UNKNOWN is an acceptable and truthful answer
- Never inflate confidence to appear more useful
"""

# ══════════════════════════════════════════════════════════════════════════════
# arifos://floors — All 13 floors as a list
# ══════════════════════════════════════════════════════════════════════════════

FLOORS_TEXT = """\
# arifOS Constitutional Floors (F1–F13)

| Floor | Name | Type | Rule |
|-------|------|------|------|
| **F1** | AMANAH | HARD | Reversible-first. Irreversible → 888_HOLD. |
| **F2** | TRUTH | HARD | P(truth) ≥ 0.99. Evidence carries OBS/DER/INT/SPEC/UNKNOWN. |
| **F3** | TRI-WITNESS | DERIVED | Human × AI × Earth × Verifier ≥ 0.75 (Nash product). |
| **F4** | CLARITY | HARD | ΔS ≤ 0 — every output reduces entropy. |
| **F5** | PEACE² | SOFT | Non-destructive power. Blocks harm/harass/extort. |
| **F6** | EMPATHY ⇄ MARUAH | SOFT | Dual-registry lossless bridge. Protect weakest stakeholder. |
| **F7** | HUMILITY | HARD | Ω₀ ∈ [0.03, 0.05]. Confidence cap 0.90. No fake certainty. |
| **F8** | GENIUS | DERIVED | G = (A×P×E×X)^(1/4) ≥ 0.80 for complex actions. |
| **F9** | ANTI-HANTU | HARD | No deception, manipulation, or consciousness claims. C_dark < 0.30. |
| **F10** | ONTOLOGY | HARD | AI-only ontology. No soul/feelings/sentience. Soul = VOID. |
| **F11** | AUDITABILITY | HARD | Every decision logged, inspectable, attributable. |
| **F12** | RESILIENCE | HARD | Injection defense. Risk < 0.85. |
| **F13** | SOVEREIGN | HARD | Human veto FINAL. Harness switch belongs to sovereign. |

## Verdict Taxonomy

| Verdict | Meaning |
|---------|---------|
| **SEAL** | All floors passed. Action authorized. |
| **HOLD** | Constitutional gate blocked. Requires remediation. |
| **SABAR** | Proceed with caution. Soft floor tension. |
| **VOID** | Hard floor violation. Action inadmissible. |

For per-floor detail, use arifos://floor/{fid} resource template.
"""

# ══════════════════════════════════════════════════════════════════════════════
# arifos://affordances — Tool affordances
# ══════════════════════════════════════════════════════════════════════════════

AFFORDANCES_TEXT = """\
# arifOS Tool Affordances — Action Classification

## Action Classes

| Class | Risk | Reversibility | Gate | Example |
|-------|------|---------------|------|---------|
| **OBSERVE** | LOW | n/a (read-only) | AUTO-DO | health probe, file read, search |
| **EXECUTE_REVERSIBLE** | MEDIUM | Rollback available | ANNOUNCE | file edit, service restart, test run |
| **EXECUTE_HIGH_IMPACT** | HIGH | Difficult rollback | arif_judge SEAL | deploy to staging, schema migration |
| **IRREVERSIBLE** | CRITICAL | Cannot undo | 888_HOLD + F13 | rm -rf, DROP, force push, vault seal |

## Blast Radius (BR)

| BR | Scope | Examples |
|----|-------|----------|
| **BR-0** | Single file / local | Edit one file |
| **BR-1** | Single service | Restart one service |
| **BR-2** | Single organ | Deploy to one organ |
| **BR-3** | Multi-organ | Federation-wide config change |
| **BR-4** | External systems | DNS, firewall, external API |
| **BR-5** | Entire federation + external | VPS restart, Caddy reload |

## Reversibility Classification

| Class | Rollback Path | Auto |
|-------|--------------|------|
| **REVERSIBLE** | `git reset --hard` or equivalent | T1 AUTO-DO |
| **RECOVERABLE** | Requires coordination, minor consequence | T2 ANNOUNCE |
| **PERMANENT** | No rollback, high consequence | T3 888_HOLD |

These affordances are the kernel's contract with every tool. A tool's action class,
blast radius, and reversibility are declared in its registration and enforced at
every call by the ConstitutionalProvider.
"""

# ══════════════════════════════════════════════════════════════════════════════
# arifos://vault/head — VAULT999 chain head
# ══════════════════════════════════════════════════════════════════════════════


def _get_vault_head_text() -> str:
    """Get VAULT999 chain head info from the filesystem."""
    vault_path = Path("/root/arifOS/VAULT999/outcomes.jsonl")
    seal_chain_path = Path("/root/.local/share/arifos/vault999/seal_chain.jsonl")

    parts = ["# VAULT999 Chain Head\n"]

    if vault_path.exists():
        try:
            result = subprocess.run(
                ["tail", "-1", str(vault_path)], capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                last = json.loads(result.stdout.strip())
                parts.append(f"last_entry: {json.dumps(last, indent=2)[:2000]}")
        except Exception as exc:
            parts.append(f"outcomes_error: {exc}")

    if seal_chain_path.exists():
        try:
            result = subprocess.run(
                ["tail", "-1", str(seal_chain_path)], capture_output=True, text=True, timeout=5
            )
            if result.stdout.strip():
                parts.append(f"\nseal_chain_tail: {result.stdout.strip()[:2000]}")
        except Exception as exc:
            parts.append(f"seal_chain_error: {exc}")

    # Verify chain integrity
    try:
        result = subprocess.run(
            [
                "python3",
                "-c",
                "import json; "
                "lines=[json.loads(l) for l in open('/root/arifOS/VAULT999/outcomes.jsonl')]; "
                f"print(f'total_seals: {len(lines)}')",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        parts.append(f"\n{result.stdout.strip()}")
    except Exception:
        pass

    if len(parts) == 1:
        parts.append("vault_status: EMPTY_OR_UNREACHABLE")

    return "\n".join(parts)


# ══════════════════════════════════════════════════════════════════════════════
# Registration
# ══════════════════════════════════════════════════════════════════════════════


def register_alignment_gap_resources(mcp: FastMCP) -> list[str]:
    """Register the 4 resources that close the provenance alignment gap."""

    @mcp.resource("arifos://epistemic")
    def epistemic_resource() -> str:
        """Epistemic label ontology (OBS/DER/INT/SPEC + provenance rules)."""
        return EPISTEMIC_TEXT

    @mcp.resource("arifos://floors")
    def floors_resource() -> str:
        """All 13 constitutional floors as a reference list."""
        return FLOORS_TEXT

    @mcp.resource("arifos://affordances")
    def affordances_resource() -> str:
        """Tool affordances: action classes, blast radius, reversibility."""
        return AFFORDANCES_TEXT

    @mcp.resource("arifos://vault/head")
    def vault_head_resource() -> str:
        """VAULT999 chain head — live from filesystem."""
        return _get_vault_head_text()

    return [
        "arifos://epistemic",
        "arifos://floors",
        "arifos://affordances",
        "arifos://vault/head",
    ]
