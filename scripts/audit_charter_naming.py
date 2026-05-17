from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".venv",
    ".mypy_cache",
    "__pycache__",
    "00_legacy_materials",
    "archive",
    "memory",
    "wiki",
}
TEXT_EXTS = {".py", ".md", ".json", ".yaml", ".yml", ".html", ".sh", ".toml"}
ALLOWED_FILE_NAMES = {
    "fastmcp.json",
    "server.json",
    "agent.json",
    "ai-plugin.json",
    "manifesto.html",
    "arifOS_13tool_manifest_v1.md",
}
BANNED_PATH_TOKENS = {
    "stack.manifest.json",
    "federation_manifest.json",
    "federation-manifest.json",
    "SovereigntyManifest.json",
    "config/manifest/",
    "tools/manifests/",
    "tool_manifest.json",
    "tool_manifest.py",
    "capability-manifest.yaml",
    "apps/manifests/",
    "runtime/manifest.py",
    "core/shared/manifest_loader.py",
}
ALLOWED_TEXT_FILES = {
    "MEMORY.md",
    "docs/deployment/VPS_CHARTER_MIGRATION.md",
    "scripts/audit_charter_naming.py",
}
ALLOWED_RELATIVE_PATHS = {
    "arifosmcp/runtime/.archive/manifest_v2_original.py",
}


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def audit_names() -> list[str]:
    issues: list[str] = []
    for path in ROOT.rglob("*"):
        if should_skip(path):
            continue
        rel = str(path.relative_to(ROOT))
        if rel in ALLOWED_RELATIVE_PATHS:
            continue
        if path.is_file() and "manifest" in path.name and path.name not in ALLOWED_FILE_NAMES:
            issues.append(f"file-name: {rel}")
        if path.is_dir() and path.name == "manifest":
            issues.append(f"directory-name: {rel}")
    return issues


def audit_paths_in_text() -> list[str]:
    issues: list[str] = []
    for path in ROOT.rglob("*"):
        if should_skip(path) or not path.is_file() or path.suffix not in TEXT_EXTS:
            continue
        rel = str(path.relative_to(ROOT))
        if rel in ALLOWED_RELATIVE_PATHS or rel in ALLOWED_TEXT_FILES:
            continue
        try:
            text = path.read_text()
        except Exception:
            continue
        for token in BANNED_PATH_TOKENS:
            if token in text:
                issues.append(f"stale-path: {rel}: contains {token}")
    return issues


def main() -> int:
    issues = audit_names() + audit_paths_in_text()
    if issues:
        print("CHARTER AUDIT FAIL")
        for issue in issues:
            print(issue)
        return 1
    print("CHARTER AUDIT PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
