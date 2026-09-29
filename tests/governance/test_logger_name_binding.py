#!/usr/bin/env python3
"""Governance hygiene: every logger name used for logging must resolve to a binding.

Origin: commit 11d4f0e21 ("convert 171 bare except/pass -> logger.exception()")
inserted `_log.exception(...)` into modules whose module-level logger is named
`logger`. `_log` was never bound, so each of those exception handlers raises
NameError instead of logging — destroying the original traceback and, in
arifosmcp/server.py, aborting inside the composer's fail-closed handler.

This test is the mechanical prevention for that failure class: a blanket
exception-handler rewrite that no analyzer ever checked.

Implementation note: a crude "is `_log` assigned anywhere in the file" test is
INSUFFICIENT and would pass arifosmcp/runtime/tools.py, which binds `_log`
inside two functions while calling it from ~56 other scopes. Real scope
resolution is required, so this walks the AST with a scope chain.
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

PKG_ROOT = Path(__file__).resolve().parents[2] / "arifosmcp"

# A name is treated as a logger when it is the base of one of these attribute calls.
LOG_METHODS = {"exception", "error", "warning", "warn", "info", "debug", "critical", "log"}
# Only names that look like loggers are audited, to keep the invariant tight and
# avoid asserting on every legitimate free variable in the package.
LOGGERISH = {"log", "_log", "logger", "_logger", "logging_logger"}


class _Scope:
    __slots__ = ("bindings", "decls", "parent")

    def __init__(self, parent: "_Scope | None" = None) -> None:
        self.bindings: set[str] = set()
        self.decls: set[tuple[str, str]] = set()  # (name, "global"|"nonlocal")
        self.parent = parent


def _collect_bindings(scope: _Scope, node: ast.AST, stop_at_scope: bool = True) -> None:
    """Record names bound directly in `scope`, recursing into non-scope children."""
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Lambda)):
            name = getattr(child, "name", None)
            if name:
                scope.bindings.add(name)
            continue  # its body is a child scope, handled separately
        if isinstance(child, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
            for gen in child.generators:
                _record_target(scope, gen.target)
            continue
        if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
            scope.bindings.add(child.id)
        elif isinstance(child, (ast.Tuple, ast.List)):
            _record_target(scope, child)
        elif isinstance(child, (ast.Import, ast.ImportFrom)):
            for alias in child.names:
                scope.bindings.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(child, ast.ExceptHandler) and child.name:
            scope.bindings.add(child.name)
        elif isinstance(child, (ast.Global, ast.Nonlocal)):
            for name in child.names:
                scope.decls.add((name, "global" if isinstance(child, ast.Global) else "nonlocal"))
        elif isinstance(child, ast.arg):
            scope.bindings.add(child.arg)
        elif isinstance(child, (ast.withitem,)):
            if child.optional_vars:
                _record_target(scope, child.optional_vars)
        else:
            _collect_bindings(scope, child)


def _record_target(scope: _Scope, target: ast.AST) -> None:
    if isinstance(target, ast.Name):
        scope.bindings.add(target.id)
    elif isinstance(target, (ast.Tuple, ast.List)):
        for elt in target.elts:
            _record_target(scope, elt)


def _resolve(name: str, scope: _Scope) -> bool:
    if any(n == name for n, kind in scope.decls if kind == "global"):
        return True  # explicitly delegated to module scope; module scope is checked too
    cur: _Scope | None = scope
    depth = 0
    while cur is not None and depth < 200:
        if name in cur.bindings:
            return True
        cur = cur.parent
        depth += 1
    return False


def _walk(node: ast.AST, scope: _Scope, module_scope: _Scope, path: Path, hits: list[str]) -> None:
    _collect_bindings(scope, node)
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            child_scope = _Scope(scope)
            for a in getattr(child.args, "args", []) if isinstance(child, ast.Lambda) else []:
                child_scope.bindings.add(a.arg)
            if not isinstance(child, ast.Lambda):
                for a in (child.args.posonlyargs + child.args.args + child.args.kwonlyargs):
                    child_scope.bindings.add(a.arg)
                if child.args.vararg:
                    child_scope.bindings.add(child.args.vararg.arg)
                if child.args.kwarg:
                    child_scope.bindings.add(child.args.kwarg.arg)
                _walk(child, child_scope, module_scope, path, hits)
                continue
            _walk(child, child_scope, module_scope, path, hits)
            continue
        if isinstance(child, ast.ClassDef):
            child_scope = _Scope(scope)
            _walk(child, child_scope, module_scope, path, hits)
            continue
        if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name):
            base = child.value.id
            if base in LOGGERISH and child.attr in LOG_METHODS:
                # a logging call on a loggerish name that resolves nowhere is a NameError
                if not _resolve(base, scope) and base not in _BUILTINS:
                    hits.append(f"{path}:{child.lineno}: {base}.{child.attr}() — `{base}` unbound in this scope")
        _walk(child, scope, module_scope, path, hits)


import builtins  # noqa: E402

_BUILTINS = set(dir(builtins))


def _audit(path: Path) -> list[str]:
    src = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError:
        return []
    module_scope = _Scope()
    hits: list[str] = []
    _walk(tree, module_scope, module_scope, path.relative_to(PKG_ROOT.parent), hits)
    return hits


def _package_py_files() -> list[Path]:
    return sorted(p for p in PKG_ROOT.rglob("*.py") if "__pycache__" not in p.parts)


def test_logger_names_resolve_across_the_package():
    """No module may call a logging method on a logger name it never binds."""
    offenders: list[str] = []
    for py in _package_py_files():
        offenders.extend(_audit(py))
    assert not offenders, (
        f"{len(offenders)} unbound logger call site(s) — each raises NameError inside an "
        f"exception handler, hiding the real error:\n" + "\n".join(sorted(set(offenders))[:60])
    )


def test_the_five_mass_converted_files_are_clean():
    """Regression anchor for commit 11d4f0e21 specifically."""
    files = [
        "runtime/rest_routes/rest_routes.py",
        "runtime/tools.py",
        "server.py",
        "tools/judge.py",
        "tools/session.py",
    ]
    for rel in files:
        p = PKG_ROOT / rel
        assert p.exists(), f"expected file moved: {rel}"
        hits = _audit(p)
        assert not hits, f"{rel} still has unbound logger calls:\n" + "\n".join(hits[:20])


if __name__ == "__main__":
    bad: list[str] = []
    for f in _package_py_files():
        bad.extend(_audit(f))
    print(f"{len(bad)} unbound logger call sites")
    for line in sorted(set(bad)):
        print("  " + line)
