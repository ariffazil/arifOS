from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "00_legacy_materials",
    "archive",
    "memory",
}
ALLOWED_FILE_NAMES = {
    "fastmcp.json",
    "server.json",
    "agent.json",
    "ai-plugin.json",
    "manifesto.html",
}
ALLOWED_PATH_SNIPPETS = {
    "/.well-known/",
    "agent-manifest/v1",
    "mcp manifest",
    "forge manifest",
    "webmcp manifest",
    "signed execution manifests",
    "actions_without_manifest",
    "manifest_id",
    "forgemanifest",
    "executionmanifest",
    "manifest creation",
    "manifest describing the operation",
    "historical memory",
}
TEXT_EXTS = {".py", ".md", ".json", ".yaml", ".yml", ".html", ".sh", ".toml"}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def audit_names() -> list[str]:
    issues: list[str] = []
    for path in ROOT.rglob("*"):
        if should_skip(path):
            continue
        if (
            path.is_file()
            and "manifest" in path.name.lower()
            and path.name not in ALLOWED_FILE_NAMES
        ):
            issues.append(f"file-name: {path.relative_to(ROOT)}")
        if path.is_dir() and path.name.lower() == "manifest":
            issues.append(f"directory-name: {path.relative_to(ROOT)}")
    return issues


def audit_text() -> list[str]:
    issues: list[str] = []
    for path in ROOT.rglob("*"):
        if should_skip(path) or not path.is_file() or path.suffix not in TEXT_EXTS:
            continue
        try:
            text = path.read_text()
        except Exception:
            continue
        lowered = text.lower()
        if "manifest" not in lowered:
            continue
        rel = str(path.relative_to(ROOT))
        if rel in {"MEMORY.md", "docs/deployment/VPS_CHARTER_MIGRATION.md"}:
            continue
        for line_no, line in enumerate(text.splitlines(), start=1):
            ll = line.lower()
            if "manifest" not in ll:
                continue
            if any(snippet in ll for snippet in ALLOWED_PATH_SNIPPETS):
                continue
            if "protocol discovery" in ll or "package manifest" in ll:
                continue
            if "forge_execute" in ll and "manifest" in ll:
                continue
            if "executionmanifest" in ll or "forgemanifest" in ll:
                continue
            if "manifeststatus" in ll or "manifest_id" in ll:
                continue
            if "actions_without_manifest" in ll:
                continue
            if "schema" in ll and "manifest" in ll:
                continue
            if "webmcp_manifest" in ll:
                continue
            issues.append(f"text: {rel}:{line_no}: {line.strip()}")
    return issues


def main() -> int:
    issues = audit_names() + audit_text()
    if issues:
        print("CHARTER AUDIT FAIL")
        for issue in issues:
            print(issue)
        return 1
    print("CHARTER AUDIT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
