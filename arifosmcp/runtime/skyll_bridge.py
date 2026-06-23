"""
arifosmcp/runtime/skyll_bridge.py — Skyll Skill Discovery Bridge for arifOS

Skyll (assafelovic/skyll) is a REST + MCP server that aggregates SKILL.md
files from skills.sh + community registry. The hosted MCP is at:
    https://api.skyll.app/mcp

This bridge exposes two arifOS sense_observe modes:
    - skill_discover  — search skills by natural language
    - skill_learn    — fetch + install a skill (888_HOLD territory, mutates
                       /root/.agents/skills/)

Unlike gptr (SSE long-lived), Skyll uses simple per-request POSTs to
the /mcp endpoint, returning SSE-formatted responses. This makes the
bridge much simpler.

F2 epistemic tag: skill content is INTERPRETATION (community-curated
documentation, not ground truth).

DITEMPA BUKAN DIBERI — Forged, Not Given.
"""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any

import httpx

logger = logging.getLogger(__name__)

_SKYLL_URL = os.getenv("SKYLL_MCP_URL", "https://api.skyll.app/mcp")
_SKYLL_TIMEOUT = float(os.getenv("SKYLL_TIMEOUT", "60.0"))
_DEFAULT_SKILLS_DIR = Path("/root/.agents/skills")


class SkyllBridge:
    """Async MCP client for the Skyll hosted MCP server."""

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=_SKYLL_TIMEOUT)
        return self._client

    async def _post_sse(self, payload: dict[str, Any]) -> dict[str, Any]:
        """
        POST to Skyll's /mcp endpoint. The response is SSE-formatted
        (event: message\\ndata: {...}\\n\\n). Parse all data events,
        return the LAST non-notification JSON-RPC response.
        """
        client = self._get_client()
        try:
            resp = await client.post(
                _SKYLL_URL,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json, text/event-stream",
                },
                json=payload,
            )
            resp.raise_for_status()
        except Exception as exc:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": str(exc),
                "bridge": "skyll",
            }

        # Parse SSE: extract ALL data: lines from the full text.
        # Skyll's response is one big block with multiple events; the
        # data: lines are not always separated by blank lines.
        text = resp.text
        events: list[dict[str, Any]] = []
        for line in text.split("\n"):
            if line.startswith("data:"):
                data_line = line[5:].strip()
                if data_line:
                    try:
                        events.append(json.loads(data_line))
                    except json.JSONDecodeError:
                        pass

        # Find the LAST json-rpc response (skip notifications)
        for event in reversed(events):
            if "id" in event and "result" in event:
                return event
            if "error" in event:
                return event

        # Fallback: return the last event
        if events:
            return events[-1]

        return {
            "status": "error",
            "verdict": "SABAR",
            "error": "no JSON-RPC response in SSE stream",
            "bridge": "skyll",
        }

    # ── High-level skill methods ──────────────────────────────────────

    async def search_skills(
        self,
        query: str,
        limit: int = 5,
        include_references: bool = False,
    ) -> dict[str, Any]:
        """
        Search skills by natural language query.
        Returns ranked list with full SKILL.md content.
        F2 epistemic tag: INTERPRETATION.

        Each skill is augmented with a `safety_recommendation` based on
        install_count (per F12 INJECTION + F1 AMANAH discipline):
          - "trusted"             — install_count >= 1000
          - "well_tested"         — install_count >= 100 (default threshold)
          - "review_before_install" — install_count >= 10
          - "low_trust"           — install_count < 10

        The LLM/agent uses these to warn the user, not to block them.
        install_count is a soft signal, not a security boundary.
        """
        resp = await self._post_sse(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "search_skills",
                    "arguments": {
                        "query": query,
                        "limit": min(max(limit, 1), 20),
                        "include_references": include_references,
                    },
                },
            }
        )

        if "error" in resp:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": resp["error"].get("message", str(resp["error"])),
                "bridge": "skyll_search",
            }

        content = resp.get("result", {}).get("content", [])
        if not content:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "empty content from Skyll",
                "bridge": "skyll_search",
            }

        text = content[0].get("text", "")
        try:
            inner = json.loads(text)
        except json.JSONDecodeError as exc:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": f"invalid JSON from Skyll: {exc}",
                "raw": text[:200],
                "bridge": "skyll_search",
            }

        skills = inner.get("skills", [])
        # Augment each skill with safety_recommendation (F12 soft signal)
        for skill in skills:
            installs = int(skill.get("install_count", 0) or 0)
            if installs >= 1000:
                skill["safety_recommendation"] = "trusted"
            elif installs >= 100:
                skill["safety_recommendation"] = "well_tested"
            elif installs >= 10:
                skill["safety_recommendation"] = "review_before_install"
            else:
                skill["safety_recommendation"] = "low_trust"

        return {
            "status": "success",
            "verdict": "SEAL" if skills else "SABAR",
            "epistemic_tag": "INTERPRETATION",  # F2: community-curated
            "bridge": "skyll_search",
            "query": inner.get("query", query),
            "count": inner.get("count", len(skills)),
            "skills": skills,
            "skill_count": len(skills),
            "safety_floor_install_count": 100,  # default install_count threshold
            "safety_floor_rationale": (
                "F12 INJECTION + F1 AMANAH: skills with install_count >= 100 "
                "are considered 'well_tested' by community signal. Below 100, "
                "the LLM/agent is encouraged to surface this to the user "
                "via the safety_recommendation field. Not a hard block — "
                "user retains agency via force=True on install_skill."
            ),
        }

    async def get_skill(
        self,
        skill_id: str,
    ) -> dict[str, Any]:
        """
        Get a specific skill by name (like `npx skills add`).
        Returns full SKILL.md content.
        F2 epistemic tag: INTERPRETATION.
        """
        resp = await self._post_sse(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "add_skill",
                    "arguments": {"name": skill_id},
                },
            }
        )

        if "error" in resp:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": resp["error"].get("message", str(resp["error"])),
                "bridge": "skyll_get_skill",
            }

        content = resp.get("result", {}).get("content", [])
        if not content:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": f"skill '{skill_id}' not found",
                "bridge": "skyll_get_skill",
            }

        text = content[0].get("text", "")
        try:
            inner = json.loads(text)
        except json.JSONDecodeError:
            # Maybe raw text
            inner = {"content": text}

        return {
            "status": "success",
            "verdict": "SEAL",
            "epistemic_tag": "INTERPRETATION",
            "bridge": "skyll_get_skill",
            "skill_id": skill_id,
            "content": inner.get("content", text),
            "metadata": {k: v for k, v in inner.items() if k != "content"},
        }

    async def install_skill(
        self,
        skill_id: str,
        skills_dir: str | Path | None = None,
        overwrite: bool = False,
        install_count: int | None = None,
        force: bool = False,
    ) -> dict[str, Any]:
        """
        Fetch a skill from Skyll and install it to /root/.agents/skills/<id>/SKILL.md.

        ⚠️  888_HOLD TERRITORY — this mutates the arifOS skill directory.
        Callers (LLM/agent) must confirm with the user before invoking.

        Args:
          skill_id: Skill identifier (e.g., "react-performance", "vercel-labs/agent-skills/react-best-practices")
          skills_dir: Target directory (default /root/.agents/skills)
          overwrite: Allow replacing an existing skill (default False → fail-closed)
          install_count: Optional — install_count from a prior search_skills
            result. Used to apply the safety floor (>= 100 = "well_tested").
          force: Bypass the install_count safety floor (user has confirmed).
            Does NOT bypass the overwrite gate — that's a separate check.

        Safety floor (F12 INJECTION + F1 AMANAH):
          - install_count >= 100  → install allowed by default
          - install_count < 100   → requires force=True
          - install_count is None → requires force=True (unknown trust)
        """
        target_dir = Path(skills_dir) if skills_dir else _DEFAULT_SKILLS_DIR

        # F1 AMANAH gate: refuse to overwrite without explicit flag
        safe_id = re.sub(r"[^A-Za-z0-9_\-/.]", "_", skill_id)
        skill_path = target_dir / safe_id / "SKILL.md"
        if skill_path.exists() and not overwrite:
            return {
                "status": "error",
                "verdict": "888_HOLD",
                "error": f"skill already installed at {skill_path}; pass overwrite=True to replace",
                "bridge": "skyll_install",
                "existing_path": str(skill_path),
                "skill_id": skill_id,
            }

        # F1 AMANAH + F12 INJECTION: install_count safety floor
        _SAFETY_FLOOR = 100
        if not force and install_count is not None and install_count < _SAFETY_FLOOR:
            return {
                "status": "error",
                "verdict": "888_HOLD",
                "error": (
                    f"install_count={install_count} is below the safety floor "
                    f"({_SAFETY_FLOOR}). This skill is not well-tested by "
                    f"community signal. Pass force=True to install anyway, "
                    f"after confirming with the user."
                ),
                "bridge": "skyll_install",
                "skill_id": skill_id,
                "install_count": install_count,
                "safety_floor": _SAFETY_FLOOR,
                "recommendation": "low_trust" if install_count < 10 else "review_before_install",
            }
        if not force and install_count is None:
            # Unknown install_count — require explicit force
            return {
                "status": "error",
                "verdict": "888_HOLD",
                "error": (
                    "install_count was not provided. To install a skill without "
                    "a known community trust signal, pass force=True after "
                    "confirming with the user. Or call search_skills first to "
                    "retrieve the install_count."
                ),
                "bridge": "skyll_install",
                "skill_id": skill_id,
                "recommendation": "low_trust",
            }

        # Fetch from Skyll
        skill = await self.get_skill(skill_id)
        if skill.get("status") != "success":
            return {
                "status": "error",
                "verdict": skill.get("verdict", "SABAR"),
                "error": skill.get("error", "fetch failed"),
                "bridge": "skyll_install",
                "skill_id": skill_id,
            }

        content = skill.get("content", "")
        if not content:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": "no content returned by Skyll",
                "bridge": "skyll_install",
                "skill_id": skill_id,
            }

        # F12 INJECTION: validate the skill content — must look like markdown
        if "<think>" in content and len(content) < 200:
            return {
                "status": "error",
                "verdict": "VOID",
                "error": "content looks like an LLM artifact, not a real SKILL.md",
                "bridge": "skyll_install",
                "skill_id": skill_id,
            }

        # Write the skill file
        try:
            skill_path.parent.mkdir(parents=True, exist_ok=True)
            skill_path.write_text(content, encoding="utf-8")
        except Exception as exc:
            return {
                "status": "error",
                "verdict": "SABAR",
                "error": f"failed to write {skill_path}: {exc}",
                "bridge": "skyll_install",
                "skill_id": skill_id,
            }

        return {
            "status": "success",
            "verdict": "SEAL",
            "bridge": "skyll_install",
            "skill_id": skill_id,
            "installed_path": str(skill_path),
            "content_length_chars": len(content),
            "epistemic_tag": "INTERPRETATION",  # F2: community-curated
            "install_count": install_count,
            "force_used": force,
        }


skyll_bridge = SkyllBridge()
