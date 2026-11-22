# START HERE — arifOS Plain-Language Guide & Onboarding

> **Canonical model:**
> - **PyPI (`pip install arifos`)** ships the arifOS governance kernel (for self-hosting).
> - **npm (`npm install @arifos/mcp`)** ships the JavaScript/TypeScript cable (thin client, zero governance authority).
> - **MCP** is the communication protocol through the cable.
> - **Hosted endpoint (`https://mcp.arif-fazil.com/mcp`)** is the address of a kernel already running.
> - **GitHub (`ariffazil/arifOS`)** is the source, evidence, and contribution surface.
>
> Installing a package is **not** the same as starting, operating, or verifying a service. Human authority remains above machine capability.

---

## Choose Your Path (No Coding Background Assumed)

### Path A — Try arifOS without installing anything (Recommended first step)
- **Goal:** Connect an AI app (Claude Desktop, Claude Code, Cursor, Windsurf, Cline) to arifOS.
- **What you need beforehand:** An MCP-compatible AI app and internet access. No Python, no Node.js.
- **What gets installed:** Nothing on your computer.
- **What runs locally:** Nothing; only your AI app sends requests.
- **What crosses the network:** The tool call proposals your AI app sends to `https://mcp.arif-fazil.com/mcp` and the verdicts/receipts returned.
- **How to verify success:** Open <https://mcp.arif-fazil.com/health> in a browser (returns JSON status) or ask your AI app to list arifOS tools — you should see **9 live wire tools** (`8` canonical stage verbs `arif_init`..`arif_seal` + `arif_report`).
- **How to stop or remove:** Delete the `"arifos"` entry from your AI app's MCP settings.
- **Common failures:** `HTTP 405 Method Not Allowed` if you open `/mcp` directly in a web browser (normal — `/mcp` speaks JSON-RPC POST, not browser GET; use `/health` in a browser).
- **What not to do:** Do not paste secrets, passwords, or private customer data into public trial prompts.

### Path B — Run your own arifOS kernel (Self-hosting via PyPI)
- **Goal:** Operate your own local or private arifOS governance kernel.
- **What you need beforehand:** Python `3.12`–`3.14` and a terminal.
- **What gets installed:** The `arifos` Python package (`pip install arifos`) and console commands (`arifos-mcp`, `arifos`).
- **What runs locally:** Nothing until you explicitly start it with `PORT=8088 arifos-mcp streamable-http` (or `arifos-mcp` for stdio).
- **What crosses the network:** Only package downloads during `pip install`, plus any external URLs you explicitly ask `arif_observe` to fetch.
- **How to verify success:**
  1. Check installed version: `pip show arifos`
  2. Probe local health: `curl -s http://localhost:8088/health`
  3. Run the safe offline demo: `python examples/enterprise_operations_demo.py`
- **How to stop or remove:** Press `Ctrl+C` in the terminal running the server; uninstall with `pip uninstall arifos`.
- **Common failures:** `command not found: pip` (use `python3 -m pip install arifos`); `Address already in use` (another process uses port `8088` — choose another port, e.g. `PORT=8089`).
- **What not to do:** Do not assume `pip install arifos` starts a background service, and do not expose `localhost:8088` directly to the public internet without authentication and TLS.

### Path C — Integrate from a JavaScript or TypeScript app (`@arifos/mcp`)
- **Goal:** Let a Node.js or TypeScript application request verdicts from a running arifOS kernel.
- **What you need beforehand:** Node.js `>= 18` and a running arifOS kernel (either the hosted endpoint or your own Path B server).
- **What gets installed:** The thin TypeScript client `@arifos/mcp` (`npm install @arifos/mcp`) — zero Python runtime, zero constitutional decision logic.
- **What runs locally:** Only your JavaScript/TypeScript application code.
- **What crosses the network:** MCP requests from your app to the configured kernel endpoint (`https://mcp.arif-fazil.com/mcp` by default, or `http://localhost:8088/mcp`).
- **How to verify success:** Call `await client.listTools()` and confirm it returns the 9 live wire tools from the connected kernel.
- **How to stop or remove:** Close your app (`await client.disconnect()`) and remove with `npm uninstall @arifos/mcp`.
- **Common failures:** Connection refused when pointed at `localhost:8088` without starting the Python kernel first; or using retired package names (`npm install arifos` is **not** published — use `@arifos/mcp`).
- **What not to do:** Never duplicate F1–F13 governance rules in JavaScript; the Python kernel is the sole judge.

### Path D — Review evidence or contribute (GitHub)
- **Goal:** Inspect constitutional floors, live health evidence, security gaps, or submit pull requests.
- **Where to look:**
  - Architecture & what is/isn't proven: [`README.md`](../README.md)
  - Live generated runtime state: [`CURRENT_VERIFIED_STATE.md`](../CURRENT_VERIFIED_STATE.md)
  - Threat model & known gaps: [`SECURITY.md`](../SECURITY.md)
  - 5-minute technical walkthrough: [`docs/QUICKSTART.md`](./QUICKSTART.md)
  - Contribution rules: [`CONTRIBUTING.md`](../CONTRIBUTING.md)

---

## Plain-Language Glossary

| Term | Plain-language meaning |
| :--- | :--- |
| **PyPI** | The public directory where Python software packages (including the `arifos` kernel) are stored and downloaded. |
| **pip** | The Python command-line installer that downloads packages from PyPI (`pip install arifos`). |
| **npm** | The JavaScript/Node.js package directory and installer (`npm install @arifos/mcp`). |
| **Node.js** | The runtime that runs JavaScript/TypeScript programs outside a web browser. |
| **MCP** | Model Context Protocol — the standard message format AI apps use to talk to external tools and governance kernels. |
| **kernel** | The core decision engine (in arifOS, the Python program that evaluates proposals against floors F1–F13 and issues verdicts). |
| **client** | A program (like Claude Desktop, Cursor, or `@arifos/mcp`) that sends requests to a server. |
| **server** | A running program that listens for requests and sends back responses (for example, the running arifOS kernel). |
| **endpoint** | The web address (URL) where a running server can be reached, such as `https://mcp.arif-fazil.com/mcp`. |
| **localhost** | Your own computer's private network address (`127.0.0.1`), reachable only from the same machine. |
| **port** | A numbered doorway on a computer (such as `8088`) so multiple servers can run side by side without colliding. |
| **self-hosting** | Running and operating your own copy of the arifOS kernel on your own computer or server instead of using the hosted endpoint. |

---

## Evidence Hierarchy

Every factual claim in this documentation carries an evidence class:
- **OBS** — Directly observed from a live endpoint, repository file, or command output.
- **DER** — Derived from observed evidence.
- **INT** — Interpretive assessment or recommendation.
- **SPEC** — Design intent not yet proven in production.

**Last updated:** 2026-11-22
**Maintainer:** Muhammad Arif bin Fazil
