"""
arifOS MCP Resources — TREE777 Wiki Skills as MCP Resources
═══════════════════════════════════════════════════════════════════════════════════════

Exposes the TREE777 canonical wiki as MCP Resources.

Rule: The wiki is the canonical TREE777 knowledge tree.
The four MCP servers expose selected branches as Resources,
expose deliberative rituals as Prompts, and retain only existing
gated backend actuators as Tools.

URI scheme:
  tree777://skills/arifos/*       — governance skills
  tree777://skills/geox/*        — geoscience skills
  tree777://skills/well/*        — vitality skills
  tree777://skills/wealth/*      — capital skills
  tree777://skills/federation/*  — federation skills
  tree777://skills/infrastructure/* — infra skills
  tree777://concepts/*          — knowledge concept pages
  tree777://scars/*             — scar/incident records
  tree777://schemas/*           — schema pages
  tree777://registry/tools       — live tool registry (13 sealed + diagnostics)

DITEMPA BUKAN DIBERI — Forged, Not Given
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# ── Wiki Root ─────────────────────────────────────────────────────────────────
# The canonical TREE777 wiki lives at this path.
# All 4 servers' domain skills are stored here.
WIKI_ROOT = Path(os.environ.get("TREE777_WIKI_ROOT", "/root/AAA/wiki"))
SKILLS_DIR = WIKI_ROOT / "skills"
CONCEPTS_DIR = WIKI_ROOT / "concepts"
SCARS_DIR = WIKI_ROOT / "scars"

TOOL_REGISTRY_PATH = Path(
    os.environ.get(
        "TOOL_REGISTRY_PATH",
        "/root/arifOS/core/vault999/layer4_survivability/tool-registry-2026-05-19.json",
    )
)


# ── Skill Index ────────────────────────────────────────────────────────────────


def _list_wiki_skills() -> list[dict[str, str]]:
    """List all skills in the wiki with metadata."""
    skills = []
    if not SKILLS_DIR.exists():
        return skills

    for category_dir in SKILLS_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        for skill_file in category_dir.glob("*.md"):
            skills.append(
                {
                    "category": category,
                    "name": skill_file.stem,
                    "file": str(skill_file),
                    "uri": f"tree777://skills/{category}/{skill_file.stem}",
                }
            )
    return skills


def _list_wiki_concepts() -> list[dict[str, str]]:
    """List all concept pages in the wiki."""
    concepts = []
    if not CONCEPTS_DIR.exists():
        return concepts

    for concept_file in CONCEPTS_DIR.glob("*.md"):
        concepts.append(
            {
                "name": concept_file.stem,
                "file": str(concept_file),
                "uri": f"tree777://concepts/{concept_file.stem}",
            }
        )
    return concepts


def _list_wiki_scars() -> list[dict[str, str]]:
    """List all scar records in the wiki."""
    scars = []
    if not SCARS_DIR.exists():
        return scars

    for scar_file in SCARS_DIR.glob("*.md"):
        scars.append(
            {
                "name": scar_file.stem,
                "file": str(scar_file),
                "uri": f"tree777://scars/{scar_file.stem}",
            }
        )
    return scars


def _within_wiki_root(path: Path) -> bool:
    """Return True only if path resolves strictly inside WIKI_ROOT."""
    try:
        path.resolve().relative_to(WIKI_ROOT.resolve())
        return True
    except ValueError:
        return False


def _read_wiki_file(file_path: str | Path) -> str:
    """Read a wiki file, returning frontmatter-stripped content."""
    path = Path(file_path)
    if not _within_wiki_root(path):
        return f"ERROR: Path outside wiki root: {path}"
    if not path.exists():
        return f"ERROR: File not found: {path}"

    content = path.read_text()

    # Strip YAML frontmatter
    if content.startswith("---"):
        end = content.find("\n---\n", 4)
        if end != -1:
            content = content[end + 5 :]
    return content.strip()


def _get_frontmatter(file_path: str | Path) -> dict[str, Any]:
    """Extract frontmatter from a wiki file."""
    import yaml

    path = Path(file_path)
    if not _within_wiki_root(path) or not path.exists():
        return {}

    text = path.read_text()
    if not text.startswith("---"):
        return {}

    end = text.find("\n---\n", 4)
    if end == -1:
        return {}

    fm_text = text[4:end]
    try:
        return yaml.safe_load(fm_text) or {}
    except Exception:
        return {}


def _build_index() -> dict[str, Any]:
    """Build the TREE777 wiki index for resource listing."""
    skills = _list_wiki_skills()
    concepts = _list_wiki_concepts()
    scars = _list_wiki_scars()

    index = {
        "uri": "tree777://index",
        "wiki_root": str(WIKI_ROOT),
        "total_skills": len(skills),
        "total_concepts": len(concepts),
        "total_scars": len(scars),
        "categories": {},
    }

    for skill in skills:
        cat = skill["category"]
        if cat not in index["categories"]:
            index["categories"][cat] = {"skills": [], "count": 0}
        index["categories"][cat]["skills"].append(skill["name"])
        index["categories"][cat]["count"] += 1

    index["skills"] = skills
    index["concepts"] = concepts
    index["scars"] = scars
    return index


# ── Resource Handlers ─────────────────────────────────────────────────────────


def get_tree777_index_resource() -> dict[str, Any]:
    """MCP resource: tree777://index — full wiki index."""
    return {
        "uri": "tree777://index",
        "mime_type": "application/json",
        "body": _build_index(),
    }


def get_tree777_skill_resource(category: str, name: str) -> dict[str, Any]:
    """MCP resource: tree777://skills/{category}/{name}"""
    # Try direct name first, then skill-{name} variant (for skills whose
    # filenames include a domain prefix like skill-well-governance-ops)
    direct = SKILLS_DIR / category / f"{name}.md"
    with_prefix = SKILLS_DIR / category / f"skill-{name}.md"
    file_path = direct if direct.exists() else with_prefix
    fm = _get_frontmatter(file_path)
    content = _read_wiki_file(file_path)

    return {
        "uri": f"tree777://skills/{category}/{name}",
        "mime_type": "text/markdown",
        "body": content,
        "metadata": {
            "category": category,
            "name": name,
            "file": str(file_path),
            "title": fm.get("title", name),
            "version": fm.get("version", "unknown"),
            "status": fm.get("status", "unknown"),
            "type": fm.get("type", "skill"),
            "floors": fm.get("floors", []),
            "risk_band": fm.get("risk_band", "unknown"),
            "evidence_required": fm.get("evidence_required", False),
        },
    }


def get_tree777_concept_resource(name: str) -> dict[str, Any]:
    """MCP resource: tree777://concepts/{name}"""
    file_path = CONCEPTS_DIR / f"{name}.md"
    fm = _get_frontmatter(file_path)
    content = _read_wiki_file(file_path)

    return {
        "uri": f"tree777://concepts/{name}",
        "mime_type": "text/markdown",
        "body": content,
        "metadata": {
            "name": name,
            "file": str(file_path),
            "title": fm.get("title", name),
            "version": fm.get("version", "unknown"),
            "status": fm.get("status", "unknown"),
            "type": fm.get("type", "concept"),
            "tags": fm.get("tags", []),
        },
    }


def get_tree777_scar_resource(name: str) -> dict[str, Any]:
    """MCP resource: tree777://scars/{name}"""
    file_path = SCARS_DIR / f"{name}.md"
    fm = _get_frontmatter(file_path)
    content = _read_wiki_file(file_path)

    return {
        "uri": f"tree777://scars/{name}",
        "mime_type": "text/markdown",
        "body": content,
        "metadata": {
            "name": name,
            "file": str(file_path),
            "title": fm.get("title", name),
            "version": fm.get("version", "unknown"),
            "status": fm.get("status", "unknown"),
            "type": fm.get("type", "scar"),
            "created": fm.get("created", "unknown"),
        },
    }


def get_tree777_search_resource(query: str = "", type_filter: str = "all") -> dict[str, Any]:
    """MCP resource: tree777://search — search wiki content."""
    results = {"skills": [], "concepts": [], "scars": []}
    query_lower = query.lower()

    if type_filter in ("all", "skills"):
        for skill in _list_wiki_skills():
            content = _read_wiki_file(skill["file"]).lower()
            fm = _get_frontmatter(skill["file"])
            if query_lower in content or query_lower in str(fm).lower():
                results["skills"].append(skill["uri"])

    if type_filter in ("all", "concepts"):
        for concept in _list_wiki_concepts():
            content = _read_wiki_file(concept["file"]).lower()
            fm = _get_frontmatter(concept["file"])
            if query_lower in content or query_lower in str(fm).lower():
                results["concepts"].append(concept["uri"])

    if type_filter in ("all", "scars"):
        for scar in _list_wiki_scars():
            content = _read_wiki_file(scar["file"]).lower()
            fm = _get_frontmatter(scar["file"])
            if query_lower in content or query_lower in str(fm).lower():
                results["scars"].append(scar["uri"])

    return {
        "uri": "tree777://search",
        "mime_type": "application/json",
        "body": {
            "query": query,
            "type_filter": type_filter,
            "total_results": len(results["skills"])
            + len(results["concepts"])
            + len(results["scars"]),
            "results": results,
        },
    }


# ── FastMCP Resource Registration ───────────────────────────────────────────


def register_tree777_resources(mcp: FastMCP) -> list[str]:
    """
    Register TREE777 wiki as MCP Resources.

    Exposes:
      tree777://index                    — full wiki index
      tree777://skills/{category}/{name} — individual skills
      tree777://concepts/{name}         — concept pages
      tree777://scars/{name}            — scar records
      tree777://search                  — search wiki content
    """
    registered: list[str] = []

    # Index resource
    @mcp.resource(
        "tree777://index",
        description=(
            "TREE777 wiki full index. Lists all skills (by category), "
            "concepts, and scars in the canonical wiki. Use this to discover "
            "what resources are available before fetching individual pages."
        ),
    )
    async def get_tree777_index() -> str:
        index = _build_index()
        return json.dumps(index, indent=2)

    registered.append("tree777://index")

    # Search resource
    @mcp.resource(
        "tree777://search",
        description=(
            "TREE777 wiki full-text index for client-side search. Returns all "
            "skill/concept/scar URIs with their names and categories. "
            "To find a specific item, read tree777://index for the full map, "
            "then fetch the specific resource URI."
        ),
    )
    async def search_tree777() -> str:
        index = _build_index()
        search_index = {
            "skills": [
                {"uri": s["uri"], "category": s["category"], "name": s["name"]}
                for s in index["skills"]
            ],
            "concepts": [{"uri": c["uri"], "name": c["name"]} for c in index["concepts"]],
            "scars": [{"uri": sc["uri"], "name": sc["name"]} for sc in index["scars"]],
        }
        return json.dumps(search_index, indent=2)

    registered.append("tree777://search")

    # Dynamic skill resources — registered as template resources
    # tree777://skills/{category}/{name}

    @mcp.resource(
        "tree777://skills/{category}/{name}",
        description=(
            "Individual TREE777 skill page. Returns the full skill content "
            "(markdown, frontmatter-stripped) with metadata including version, "
            "status, floors, risk_band, and evidence_required flag. "
            "Categories: arifos, geox, well, wealth, federation, infrastructure."
        ),
    )
    async def get_tree777_skill(category: str, name: str) -> str:
        result = get_tree777_skill_resource(category, name)
        if "ERROR" in result["body"]:
            return json.dumps({"error": result["body"], "uri": result["uri"]})
        output = {
            "uri": result["uri"],
            "metadata": result["metadata"],
            "content": result["body"],
        }
        return json.dumps(output, indent=2)

    registered.append("tree777://skills/{category}/{name}")

    # Concept resources
    @mcp.resource(
        "tree777://concepts/{name}",
        description=(
            "TREE777 concept page. Returns the full concept content "
            "(markdown, frontmatter-stripped) with metadata. "
            "Concepts include: TREE777, intelligence-tree, concept-tools-and-embodiment, etc."
        ),
    )
    async def get_tree777_concept(name: str) -> str:
        result = get_tree777_concept_resource(name)
        if "ERROR" in result["body"]:
            return json.dumps({"error": result["body"], "uri": result["uri"]})
        output = {
            "uri": result["uri"],
            "metadata": result["metadata"],
            "content": result["body"],
        }
        return json.dumps(output, indent=2)

    registered.append("tree777://concepts/{name}")

    # Scar resources
    @mcp.resource(
        "tree777://scars/{name}",
        description=(
            "TREE777 scar/incident record. Returns the full scar content "
            "(markdown, frontmatter-stripped) with metadata. "
            "Scars document failures and lessons learned. "
            "Example: scar-hermes-fabrication-2026-05-17."
        ),
    )
    async def get_tree777_scar(name: str) -> str:
        result = get_tree777_scar_resource(name)
        if "ERROR" in result["body"]:
            return json.dumps({"error": result["body"], "uri": result["uri"]})
        output = {
            "uri": result["uri"],
            "metadata": result["metadata"],
            "content": result["body"],
        }
        return json.dumps(output, indent=2)

    registered.append("tree777://scars/{name}")

    return registered


# ── Unified resource registry ───────────────────────────────────────────────

RESOURCE_HANDLERS = {
    "tree777://index": lambda: get_tree777_index_resource()["body"],
    "tree777://registry/tools": lambda: get_tree777_registry_resource("tools")["body"],
}


def get_tree777_registry_resource(name: str) -> dict[str, Any]:
    """Return a tool registry resource by name. Currently supports 'tools'."""
    uri = f"tree777://registry/{name}"
    if name != "tools":
        return {"uri": uri, "error": f"Unknown registry resource: {name}. Available: tools"}
    if not TOOL_REGISTRY_PATH.exists():
        return {"uri": uri, "error": "Tool registry not found", "path": str(TOOL_REGISTRY_PATH)}
    try:
        data = json.loads(TOOL_REGISTRY_PATH.read_text())
        return {"uri": uri, "metadata": {"name": "tool-registry", "type": "registry"}, "body": data}
    except Exception as e:
        return {"uri": uri, "error": str(e)}


def handle_resource(uri: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Handle a TREE777 resource request.

    Usage:
        resource = handle_resource("tree777://index")
        resource = handle_resource("tree777://skills/arifos/constitutional-reasoning")
    """
    if uri == "tree777://index":
        return get_tree777_index_resource()

    parts = uri.replace("tree777://", "").split("/")

    if len(parts) == 2 and parts[0] == "search":
        query = (params or {}).get("query", "")
        type_filter = (params or {}).get("type_filter", "all")
        return get_tree777_search_resource(query, type_filter)

    if len(parts) == 3 and parts[0] == "skills":
        category, name = parts[1], parts[2]
        return get_tree777_skill_resource(category, name)

    if len(parts) == 2 and parts[0] == "concepts":
        return get_tree777_concept_resource(parts[1])

    if len(parts) == 2 and parts[0] == "scars":
        return get_tree777_scar_resource(parts[1])

    if len(parts) == 2 and parts[0] == "registry":
        return get_tree777_registry_resource(parts[1])

    return {
        "uri": uri,
        "error": f"Unknown TREE777 resource URI: {uri}",
        "available": [
            "tree777://index",
            "tree777://search",
            "tree777://skills/{category}/{name}",
            "tree777://concepts/{name}",
            "tree777://scars/{name}",
            "tree777://registry/tools",
        ],
    }


__all__ = [
    "register_tree777_resources",
    "get_tree777_index_resource",
    "get_tree777_skill_resource",
    "get_tree777_concept_resource",
    "get_tree777_scar_resource",
    "get_tree777_search_resource",
    "get_tree777_registry_resource",
    "RESOURCE_HANDLERS",
    "handle_resource",
]
