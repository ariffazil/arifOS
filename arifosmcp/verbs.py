"""Canonical shell surface for arifOS — a thin client of the kernel.

Every verb maps 1:1 onto a capability the kernel already exposes; nothing is
implemented here that the kernel does not answer. Nothing here reads
/root/scripts, so the same wheel works against any reachable kernel.

Kernel address: ARIFOS_KERNEL_URL (default http://127.0.0.1:8088).
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

VERBS = ("state", "observe", "judge", "seal", "witness")

# verb -> MCP tool. "state" and "witness" read kernel surfaces, not tools.
_TOOL_FOR_VERB = {
    "observe": "arif_observe",
    "judge": "arif_judge",
    "seal": "arif_seal",
}

_STATUS = {
    "state": "Report kernel identity, band and organ health",
    "observe": "Sense reality through the kernel (tool: arif_observe)",
    "judge": "Ask the kernel for a constitutional verdict (tool: arif_judge)",
    "seal": "Append a receipt to the chain via the kernel (tool: arif_seal)",
    "witness": "Read the voucher-chain head (resource: arifos://vault/head)",
}

_DEFAULT_URL = "http://127.0.0.1:8088/mcp"


def kernel_url() -> str:
    """Return the kernel MCP endpoint, honouring ARIFOS_KERNEL_URL."""
    raw = os.getenv("ARIFOS_KERNEL_URL", "http://127.0.0.1:8088").rstrip("/")
    if raw.endswith("/mcp"):
        return raw
    return raw + "/mcp"


def _http(url: str, payload: dict | None = None, timeout: float = 30.0) -> tuple[int, str]:
    data = None
    headers = {"Accept": "application/json, text/event-stream"}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", "replace")


def _decode(body: str) -> dict:
    """Decode a JSON or text/event-stream response body."""
    body = body.strip()
    if not body:
        return {}
    if body.startswith("{"):
        return json.loads(body)
    for line in body.splitlines():
        if line.startswith("data:"):
            chunk = line[5:].strip()
            if chunk.startswith("{"):
                return json.loads(chunk)
    raise ValueError("no JSON found in kernel response")


def _rpc(url: str, method: str, params: dict) -> dict:
    status, body = _http(
        url,
        {"jsonrpc": "2.0", "id": 1, "method": method, "params": params},
    )
    if status >= 400:
        raise RuntimeError(f"kernel answered HTTP {status}: {body[:300]}")
    doc = _decode(body)
    if "error" in doc:
        err = doc["error"]
        raise RuntimeError(f"kernel error {err.get('code')}: {err.get('message')}")
    return doc.get("result", {})


def _parse_argv(argv: list[str]) -> tuple[dict, bool, bool]:
    """Split argv into (tool arguments, json_output, wants_help).

    `--key value` and `--flag` become tool arguments verbatim, so the CLI never
    invents a schema the kernel does not already declare.
    """
    args: dict = {}
    as_json = False
    wants_help = False
    i = 0
    while i < len(argv):
        token = argv[i]
        if token in ("--json",):
            as_json = True
        elif token in ("--help", "-h"):
            wants_help = True
        elif token.startswith("--"):
            key = token[2:].replace("-", "_")
            nxt = argv[i + 1] if i + 1 < len(argv) else None
            if nxt is None or nxt.startswith("--"):
                args[key] = True
            else:
                args[key] = nxt
                i += 1
        else:
            raise ValueError(f"unexpected argument: {token}")
        i += 1
    return args, as_json, wants_help


def _print_verb_help(verb: str) -> int:
    print(f"arifos {verb} — {_STATUS[verb]}")
    print(f"kernel: {kernel_url()}  (override with ARIFOS_KERNEL_URL)")
    print("\nPass tool arguments straight through:")
    print(f"  arifos {verb} --claim 'delete production database' --tier T3 --json")
    print("\nFlags:  --json  machine-readable output   --help  this text")
    return 0


def run_verb(verb: str, argv: list[str]) -> int:
    if verb not in VERBS:
        print(f"arifos: unknown verb {verb!r}; known: {', '.join(VERBS)}", file=sys.stderr)
        return 2
    try:
        args, as_json, wants_help = _parse_argv(argv)
    except ValueError as exc:
        print(f"arifos {verb}: {exc}", file=sys.stderr)
        return 2
    if wants_help:
        return _print_verb_help(verb)

    url = kernel_url()
    try:
        if verb == "state":
            result = _state(url)
        elif verb == "witness":
            result = _witness(url)
        else:
            result = _rpc(url, "tools/call", {"name": _TOOL_FOR_VERB[verb], "arguments": args})
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"arifos {verb}: kernel unreachable at {url} ({exc})", file=sys.stderr)
        print("  start a kernel:  arifos --mode http   (or set ARIFOS_KERNEL_URL)", file=sys.stderr)
        return 1
    except (RuntimeError, ValueError) as exc:
        print(f"arifos {verb}: {exc}", file=sys.stderr)
        return 1

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    else:
        _render(verb, result)
    return 0


def _base(os_url: str) -> str:
    return os_url[: -len("/mcp")]


def _state(url: str) -> dict:
    base = _base(url)
    out: dict = {}
    for route in ("/health", "/version"):
        try:
            status, body = _http(base + route, timeout=10.0)
            out[route.lstrip("/")] = _safe_json(body) if status < 400 else {"http": status}
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            out[route.lstrip("/")] = {"error": str(exc)}
    if all(isinstance(v, dict) and "error" in v for v in out.values()):
        # A CLI that cannot reach the kernel must fail, not print an empty success.
        raise RuntimeError(f"kernel unreachable at {base}")
    return out


def _witness(url: str) -> dict:
    return _rpc(url, "resources/read", {"uri": "arifos://vault/head"})


def _safe_json(body: str):
    try:
        return json.loads(body)
    except ValueError:
        return body[:400]


def _render(verb: str, result: dict) -> None:
    if verb == "state":
        for name, doc in result.items():
            if isinstance(doc, dict):
                bits = " ".join(f"{k}={v}" for k, v in list(doc.items())[:6])
                print(f"{name:8} {bits}")
            else:
                print(f"{name:8} {doc}")
        return
    text = _result_text(result)
    print(text)


def _result_text(result: dict) -> str:
    content = result.get("content")
    if isinstance(content, list):
        parts = [c.get("text", "") for c in content if isinstance(c, dict)]
        joined = "\n".join(p for p in parts if p)
        if joined:
            return joined
    return json.dumps(result, indent=2, ensure_ascii=False, default=str)[:4000]


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(f"usage: arifos <{'|'.join(VERBS)}> [--key value] [--json]", file=sys.stderr)
        return 2
    return run_verb(argv[0], argv[1:])


if __name__ == "__main__":
    raise SystemExit(main())
