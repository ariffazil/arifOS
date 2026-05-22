"""arifos_wiki_tools.symbols — Language detection and symbol extraction."""

from __future__ import annotations

import ast
import re
from typing import Any

# Maps file suffixes to language names
_LANG_MAP: dict[str, str] = {
    "py": "python",
    "js": "javascript",
    "jsx": "javascript-react",
    "ts": "typescript",
    "tsx": "typescript-react",
    "md": "markdown",
    "mdx": "markdown",
    "json": "json",
    "yaml": "yaml",
    "yml": "yaml",
    "toml": "toml",
    "sh": "shell",
    "sql": "sql",
    "html": "html",
    "css": "css",
    "c": "c",
    "cpp": "cpp",
    "h": "c-header",
    "hpp": "cpp-header",
    "go": "go",
    "rs": "rust",
    "java": "java",
    "kt": "kotlin",
    "txt": "text",
}

# Heading pattern for markdown
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)

# JS/TS symbol extraction regex
# NOTE: [\w$]+ captures full camelCase/PascalCase identifiers.
_JS_SYMBOL_RE = re.compile(
    r"""^\s*
(?:
    (?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(?P<fn>[A-Za-z_$][\w$]+) |
    (?:export\s+)?(?:default\s+)?class\s+(?P<class>[A-Za-z_$][\w$]+) |
    (?:export\s+)?(?:const|let|var)\s+(?P<const>[A-Za-z_$][\w$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*(?:=>|(?:\{))
    |
    (?:export\s+)?(?:const|let|var)\s+(?P<const2>[A-Za-z_$][\w$]+)\s*=\s*async\s+function
)
""",
    re.MULTILINE | re.VERBOSE,
)


def detect_language(rel_path: str) -> str:
    """Infer language from file path suffix."""
    suffix = rel_path.lower().rsplit(".", 1)[-1] if "." in rel_path else ""
    return _LANG_MAP.get(suffix, "text")


def extract_python_symbols(text: str) -> list[dict[str, Any]]:
    """Extract classes, functions, and their docstrings from Python source."""
    symbols: list[dict[str, Any]] = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return symbols

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "class" if isinstance(node, ast.ClassDef) else "function"
            doc = ast.get_docstring(node)
            symbols.append(
                {
                    "kind": kind,
                    "name": node.name,
                    "line": getattr(node, "lineno", None),
                    "doc": (doc.splitlines()[0] if doc else ""),
                }
            )
    return sorted(symbols, key=lambda x: (x.get("line") or 0, x["name"]))


def extract_markdown_symbols(text: str) -> list[dict[str, Any]]:
    """Extract headings from markdown as symbol-like records."""
    out: list[dict[str, Any]] = []
    for idx, line in enumerate(text.splitlines(), 1):
        m = _HEADING_RE.match(line)
        if m:
            out.append(
                {
                    "kind": "heading",
                    "name": m.group(2).strip(),
                    "level": len(m.group(1)),
                    "line": idx,
                }
            )
    return out


def _line_no(text: str, pos: int) -> int:
    """Map a byte offset to a line number (1-indexed)."""
    return text[:pos].count("\n") + 1


def extract_js_symbols(text: str) -> list[dict[str, Any]]:
    """Extract function and class names from JavaScript/TypeScript source."""
    out: list[dict[str, Any]] = []
    for m in _JS_SYMBOL_RE.finditer(text):
        name = m.group("fn") or m.group("class") or m.group("const") or m.group("const2")
        if not name:
            continue
        kind = "class" if m.group("class") else "function"
        out.append(
            {
                "kind": kind,
                "name": name,
                "line": _line_no(text, m.start()),
            }
        )
    return out


def extract_symbols(rel_path: str, text: str) -> list[dict[str, Any]]:
    """
    Extract structured symbols from a source file.

    Returns a list of dicts with keys: kind, name, line, doc (optional).
    """
    lang = detect_language(rel_path)
    if lang == "python":
        return extract_python_symbols(text)
    if lang == "markdown":
        return extract_markdown_symbols(text)
    if lang in {"javascript", "javascript-react", "typescript", "typescript-react"}:
        return extract_js_symbols(text)
    return []
