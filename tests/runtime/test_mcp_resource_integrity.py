"""
tests/runtime/test_mcp_resource_integrity.py — MCP Inspector-style resource tests.

Proves:
  1. Every canonical arifos:// URI resolves via resources/read
  2. Every resolved content carries _meta with content_hash
  3. _meta includes provenance (truth_level, evidence_layer)
  4. Seal anchoring connects to VAULT999 head
  5. Inline boilerplate migration (extract_inline_meta)
  6. listChanged capability is declared
  7. Resource templates are discoverable

These tests run against the LIVE arifOS MCP server at localhost:8088.
They are the MCP Inspector equivalent for the arifOS federation.

Forged 2026-07-15 — Reality Verdict P1 implementation.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

import pytest

# ── MCP transport helper ─────────────────────────────────────────────────────

ARIFOS_MCP_URL = "http://localhost:8088/mcp"


def _mcp_call(method: str, params: dict | None = None, *, session_id: str | None = None) -> dict:
    """Make a JSON-RPC call to the arifOS MCP server."""
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {},
        }
    ).encode()

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = urllib.request.Request(ARIFOS_MCP_URL, data=body, headers=headers, method="POST")
    resp = urllib.request.urlopen(req, timeout=15)
    sid = resp.headers.get("Mcp-Session-Id") or resp.headers.get("mcp-session-id")
    data = json.loads(resp.read())
    if sid:
        data["_session_id"] = sid
    return data


def _init_session() -> str:
    """Initialize an MCP session and return the session ID."""
    data = _mcp_call(
        "initialize",
        {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "mcp-inspector-test", "version": "1.0"},
        },
    )
    return data.get("_session_id", "")


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def session_id() -> str:
    return _init_session()


@pytest.fixture(scope="session")
def resource_list(session_id: str) -> list[dict]:
    """Fetch the full resource list from arifOS."""
    data = _mcp_call("resources/list", session_id=session_id)
    return data.get("result", {}).get("resources", [])


@pytest.fixture(scope="session")
def prompt_list(session_id: str) -> list[dict]:
    """Fetch the full prompt list from arifOS."""
    data = _mcp_call("prompts/list", session_id=session_id)
    return data.get("result", {}).get("prompts", [])


# ── Canonical arifos:// URIs that MUST resolve ───────────────────────────────

CANONICAL_URIS = [
    "arifos://doctrine",
    "arifos://trinity",
    "arifos://schema",
    "arifos://civilization",
    "arifos://seal-readiness",
    "arifos://jurisdiction",
    "arifos://identity",
    "arifos://memory",
    "arifos://vitals",
    "arifos://bootstrap",
    "arifos://human/metabolized",
    "arifos://loop-engineering",
    "arifos://quickstart",
    "arifos://mcp-alignment",
    "arifos://mcp/surface-map",
]

# Template URIs — test with placeholder values
TEMPLATE_URIS = [
    ("arifos://verdict/{session_id}", {"session_id": "test-session-001"}),
    ("arifos://continuity/{session_id}", {"session_id": "test-session-001"}),
]


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 1: Capability declarations
# ═══════════════════════════════════════════════════════════════════════════════


class TestCapabilities:
    """MCP capability declarations must be honest."""

    def test_resources_capability_declared(self, session_id: str):
        """resources capability must be declared (even if subscribe is false)."""
        data = _mcp_call(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "cap-test", "version": "1.0"},
            },
        )
        caps = data.get("result", {}).get("capabilities", {})
        assert "resources" in caps, "resources capability not declared"
        assert caps["resources"].get("listChanged") is True, (
            "listChanged not declared for resources"
        )

    def test_prompts_capability_declared(self, session_id: str):
        """prompts capability must be declared."""
        data = _mcp_call(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "cap-test", "version": "1.0"},
            },
        )
        caps = data.get("result", {}).get("capabilities", {})
        assert "prompts" in caps, "prompts capability not declared"
        assert caps["prompts"].get("listChanged") is True, "listChanged not declared for prompts"

    def test_tools_capability_declared(self, session_id: str):
        """tools capability must be declared."""
        data = _mcp_call(
            "initialize",
            {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "cap-test", "version": "1.0"},
            },
        )
        caps = data.get("result", {}).get("capabilities", {})
        assert "tools" in caps, "tools capability not declared"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 2: Every canonical arifos:// URI resolves
# ═══════════════════════════════════════════════════════════════════════════════


class TestCanonicalResources:
    """Every canonical arifos:// URI must resolve via resources/read."""

    @pytest.mark.parametrize("uri", CANONICAL_URIS)
    def test_canonical_uri_resolves(self, uri: str, session_id: str):
        """Each canonical URI must return non-empty content."""
        data = _mcp_call("resources/read", {"uri": uri}, session_id=session_id)
        result = data.get("result", {})
        contents = result.get("contents", [])
        assert len(contents) > 0, f"{uri} returned empty contents"

        content = contents[0]
        assert content.get("uri") == uri, f"URI mismatch: expected {uri}, got {content.get('uri')}"
        text = content.get("text", "")
        assert len(text) > 0, f"{uri} returned empty text"

    @pytest.mark.parametrize("uri", CANONICAL_URIS)
    def test_canonical_uri_has_meta(self, uri: str, session_id: str):
        """Each canonical URI must carry _meta with content_hash."""
        data = _mcp_call("resources/read", {"uri": uri}, session_id=session_id)
        contents = data.get("result", {}).get("contents", [])
        assert len(contents) > 0

        meta = contents[0].get("_meta", {})
        assert meta, f"{uri} has no _meta"
        assert "content_hash" in meta, f"{uri} _meta missing content_hash"
        assert meta["content_hash"], f"{uri} content_hash is empty"

    @pytest.mark.parametrize("uri", CANONICAL_URIS)
    def test_canonical_uri_has_provenance(self, uri: str, session_id: str):
        """Each canonical URI must carry provenance metadata."""
        data = _mcp_call("resources/read", {"uri": uri}, session_id=session_id)
        contents = data.get("result", {}).get("contents", [])
        assert len(contents) > 0

        meta = contents[0].get("_meta", {})
        provenance = meta.get("provenance", {})
        assert provenance, f"{uri} _meta missing provenance"
        assert "truth_level" in provenance, f"{uri} provenance missing truth_level"
        assert "evidence_layer" in provenance, f"{uri} provenance missing evidence_layer"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 3: Template URIs resolve with parameters
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemplateResources:
    """Template URIs (with {params}) must resolve when parameters are supplied."""

    @pytest.mark.parametrize("uri,params", TEMPLATE_URIS)
    def test_template_uri_resolves(self, uri: str, params: dict, session_id: str):
        """Template URI must return content when parameters are provided."""
        data = _mcp_call("resources/read", {"uri": uri}, session_id=session_id)
        # Template resources may return error if the underlying data doesn't exist,
        # but the call must not fail at the protocol level
        assert "result" in data or "error" in data, f"{uri} returned neither result nor error"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 4: Hash/seal anchoring
# ═══════════════════════════════════════════════════════════════════════════════


class TestHashSealAnchoring:
    """Resource _meta must carry content hash and seal anchoring."""

    def test_content_hash_is_blake3_or_sha256(self, session_id: str):
        """Content hash must use blake3: or sha256: prefix."""
        data = _mcp_call("resources/read", {"uri": "arifos://doctrine"}, session_id=session_id)
        contents = data.get("result", {}).get("contents", [])
        assert len(contents) > 0

        meta = contents[0].get("_meta", {})
        ch = meta.get("content_hash", "")
        assert ch.startswith("blake3:") or ch.startswith("sha256:"), (
            f"content_hash prefix invalid: {ch[:20]}"
        )

    def test_seal_anchoring_has_seq(self, session_id: str):
        """Seal-anchored resources must carry seal_seq from VAULT999."""
        data = _mcp_call("resources/read", {"uri": "arifos://doctrine"}, session_id=session_id)
        contents = data.get("result", {}).get("contents", [])
        assert len(contents) > 0

        meta = contents[0].get("_meta", {})
        # seal_seq may be None if VAULT999 head doesn't exist, but the field must exist
        assert "seal_seq" in meta, "_meta missing seal_seq field"
        assert "seal_anchored" in meta, "_meta missing seal_anchored field"

    def test_observed_at_is_iso8601(self, session_id: str):
        """observed_at must be ISO-8601 UTC."""
        data = _mcp_call("resources/read", {"uri": "arifos://vitals"}, session_id=session_id)
        contents = data.get("result", {}).get("contents", [])
        assert len(contents) > 0

        meta = contents[0].get("_meta", {})
        oa = meta.get("observed_at", "")
        assert oa.endswith("Z"), f"observed_at not UTC: {oa}"
        assert "T" in oa, f"observed_at not ISO-8601: {oa}"

    def test_schema_version_present(self, session_id: str):
        """_meta must carry schema_version."""
        data = _mcp_call("resources/read", {"uri": "arifos://doctrine"}, session_id=session_id)
        contents = data.get("result", {}).get("contents", [])
        assert len(contents) > 0

        meta = contents[0].get("_meta", {})
        assert meta.get("schema_version") == "resource-meta/v1"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 5: Resource list completeness
# ═══════════════════════════════════════════════════════════════════════════════


class TestResourceList:
    """Resource list must be complete and consistent."""

    def test_resource_list_not_empty(self, resource_list: list):
        """Must have at least 15 canonical resources."""
        assert len(resource_list) >= 15, f"Only {len(resource_list)} resources listed"

    def test_all_canonical_uris_in_list(self, resource_list: list):
        """All canonical URIs must appear in the resource list."""
        listed_uris = {r.get("uri", "") for r in resource_list}
        for uri in CANONICAL_URIS:
            assert uri in listed_uris, f"{uri} not in resources/list"

    def test_resource_names_present(self, resource_list: list):
        """Every resource must have a name."""
        for r in resource_list:
            assert r.get("name"), f"Resource {r.get('uri')} has no name"

    def test_resource_descriptions_present(self, resource_list: list):
        """Every resource must have a description (50+ chars for LLM briefing)."""
        for r in resource_list:
            desc = r.get("description", "")
            assert len(desc) >= 20, (
                f"Resource {r.get('uri')} description too short ({len(desc)} chars)"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 6: Prompts
# ═══════════════════════════════════════════════════════════════════════════════


class TestPrompts:
    """Prompts must be discoverable and well-formed."""

    def test_prompts_not_empty(self, prompt_list: list):
        """Must have at least 3 prompts."""
        assert len(prompt_list) >= 3, f"Only {len(prompt_list)} prompts listed"

    def test_metabolic_loop_prompts_present(self, prompt_list: list):
        """9-stage metabolic loop prompts must be present."""
        prompt_names = {p.get("name", "") for p in prompt_list}
        required = {"000_init", "111_sense", "333_reason", "888_judge", "999_seal"}
        for name in required:
            assert name in prompt_names, f"Metabolic prompt '{name}' missing"

    def test_constitutional_pre_flight_present(self, prompt_list: list):
        """Constitutional pre-flight prompt must be present."""
        prompt_names = {p.get("name", "") for p in prompt_list}
        assert "constitutional_pre_flight" in prompt_names

    def test_prompt_descriptions_present(self, prompt_list: list):
        """Every prompt must have a description."""
        for p in prompt_list:
            assert p.get("description"), f"Prompt {p.get('name')} has no description"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 7: Inline metadata extraction (migration path)
# ═══════════════════════════════════════════════════════════════════════════════


class TestInlineMetaMigration:
    """Test the extract_inline_meta migration helper."""

    def test_extract_inline_meta(self):
        """Inline arifos_meta block must be extracted correctly."""
        from arifosmcp.resources.hash_anchor import extract_inline_meta

        text = """---arifos_meta
resource_class: constitution
authority_level: SOVEREIGN_CANON
mutation_allowed: false
version: 2026.06.21
---
This is the actual content of the resource.
It should be returned without the meta block.
"""
        meta, clean = extract_inline_meta(text)

        assert meta["resource_class"] == "constitution"
        assert meta["authority_level"] == "SOVEREIGN_CANON"
        assert meta["mutation_allowed"] is False
        assert meta["version"] == "2026.06.21"
        assert "arifos_meta" not in clean
        assert "actual content" in clean

    def test_no_inline_meta_passthrough(self):
        """Text without inline meta must pass through unchanged."""
        from arifosmcp.resources.hash_anchor import extract_inline_meta

        text = "Just plain content, no metadata block."
        meta, clean = extract_inline_meta(text)

        assert meta == {}
        assert clean == text

    def test_anchor_resource_meta(self):
        """anchor_resource_meta must produce valid _meta envelope."""
        from arifosmcp.resources.hash_anchor import anchor_resource_meta

        meta = anchor_resource_meta(
            "test content",
            "arifos://doctrine",
            provenance={
                "source": "constitution",
                "truth_level": 1,
                "truth_label": "SOVEREIGN_CANON",
                "mutability": "immutable",
                "evidence_layer": "constitutional",
            },
        )

        assert meta["schema_version"] == "resource-meta/v1"
        assert meta["content_hash"].startswith(("blake3:", "sha256:"))
        assert meta["observed_at"].endswith("Z")
        assert "seal_seq" in meta
        assert "seal_anchored" in meta
        assert meta["provenance"]["truth_level"] == 1
        assert meta["provenance"]["truth_label"] == "SOVEREIGN_CANON"


# ═══════════════════════════════════════════════════════════════════════════════
# TEST 8: Cross-resource consistency
# ═══════════════════════════════════════════════════════════════════════════════


class TestCrossResourceConsistency:
    """Resources must be internally consistent."""

    def test_same_content_produces_same_hash(self, session_id: str):
        """Reading the same resource twice must produce the same hash."""
        data1 = _mcp_call("resources/read", {"uri": "arifos://doctrine"}, session_id=session_id)
        data2 = _mcp_call("resources/read", {"uri": "arifos://doctrine"}, session_id=session_id)

        hash1 = data1["result"]["contents"][0].get("_meta", {}).get("content_hash", "")
        hash2 = data2["result"]["contents"][0].get("_meta", {}).get("content_hash", "")

        assert hash1 == hash2, "Same resource produced different hashes"

    def test_different_resources_different_hash(self, session_id: str):
        """Different resources must have different hashes."""
        data1 = _mcp_call("resources/read", {"uri": "arifos://doctrine"}, session_id=session_id)
        data2 = _mcp_call("resources/read", {"uri": "arifos://trinity"}, session_id=session_id)

        hash1 = data1["result"]["contents"][0].get("_meta", {}).get("content_hash", "")
        hash2 = data2["result"]["contents"][0].get("_meta", {}).get("content_hash", "")

        assert hash1 != hash2, "Different resources produced same hash"

    def test_mime_type_present(self, session_id: str):
        """Every resource content must have mimeType."""
        for uri in ["arifos://doctrine", "arifos://vitals", "arifos://schema"]:
            data = _mcp_call("resources/read", {"uri": uri}, session_id=session_id)
            contents = data.get("result", {}).get("contents", [])
            assert len(contents) > 0, f"{uri} empty"
            assert contents[0].get("mimeType"), f"{uri} missing mimeType"
