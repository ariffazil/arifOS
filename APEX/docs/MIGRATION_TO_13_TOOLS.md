# 🎯 Migration Guide: Consolidated 13 Canonical Tools

## Overview

arifOS has consolidated from a fragmented 17+ tool surface to **exactly 13 canonical
constitutional tools** aligned with the MCP 2025-11-25 specification.

This guide explains the changes and how to migrate your code.

---

## What Changed

### ✅ New Tool: `ingest_evidence`

**Replaces:** `fetch_content` + `inspect_file`

**Why:** Both tools performed the same cognitive act — retrieving and examining an
object from the environment. Merging them into one entry point:
- Reduces conceptual overhead for agents and humans
- Creates a clean "discovery vs. retrieval" split:
  - `search_reality` → **EXPLORE** (find candidates)
  - `ingest_evidence` → **EXAMINE** (open/parse a chosen object)
- Produces cleaner audit trails (one tool name, two input paths)

### ✅ Promoted: `metabolic_loop`

`metabolic_loop` was previously classified as an L5 composite orchestration tool.
It is now a first-class L4 canonical tool, completing the 13-tool surface.

---

## Migration Examples

### From `fetch_content` (URL retrieval)

**Before:**
```python
result = await fetch_content(url="https://example.com", max_chars=500)
```

**After:**
```python
result = await ingest_evidence(
    source_type="url",
    target="https://example.com",
    mode="raw",
    max_chars=500,
)
```

### From `inspect_file` (filesystem inspection)

**Before:**
```python
result = await inspect_file(path="/path/to/file.txt")
# or
result = await inspect_file(path="/path/to/dir", depth=2, max_files=50)
```

**After:**
```python
result = await ingest_evidence(
    source_type="file",
    target="/path/to/dir",
    depth=2,
    max_files=50,
)
```

### Processing Modes

```python
# Raw content (default)
result = await ingest_evidence(source_type="url", target="https://example.com", mode="raw")

# Quick summary (first 500 chars)
result = await ingest_evidence(source_type="url", target="https://example.com", mode="summary")

# Chunked (list of 1000-char segments)
result = await ingest_evidence(source_type="url", target="https://example.com", mode="chunks")
```

---

## SSRF Protection (F12 — Injection Defense)

`ingest_evidence` performs a **server-side HTTP request** when `source_type="url"`. To prevent
Server-Side Request Forgery (SSRF) attacks, the following restrictions are enforced before any
network call is made:

### 1. HTTPS-only scheme

Only `https://` URLs are accepted. Requests using `http://`, `ftp://`, `file://`, or any other
scheme are rejected with `status: "BLOCKED_SSRF"`.

```python
# ✅ Allowed
result = await ingest_evidence(source_type="url", target="https://example.com")

# ❌ Blocked — http scheme
result = await ingest_evidence(source_type="url", target="http://example.com")
# → {"status": "BLOCKED_SSRF", "error": "Only https:// URLs are permitted ..."}
```

### 2. Private and internal address ranges blocked

The target hostname is resolved via DNS before the HTTP call. If **any** returned address falls
within a private, loopback, or link-local range, the request is rejected:

| Range | Description |
|-------|-------------|
| `127.0.0.0/8` | IPv4 loopback |
| `10.0.0.0/8` | Private class A |
| `172.16.0.0/12` | Private class B |
| `192.168.0.0/16` | Private class C |
| `169.254.0.0/16` | Link-local (incl. cloud metadata `169.254.169.254`) |
| `100.64.0.0/10` | CGNAT / shared address space (RFC 6598) |
| `::1/128` | IPv6 loopback |
| `fc00::/7` | IPv6 unique local |
| `fe80::/10` | IPv6 link-local |

```python
# ❌ Blocked — resolves to loopback
result = await ingest_evidence(source_type="url", target="https://localhost/admin")
# → {"status": "BLOCKED_SSRF", "error": "Access to private/internal address '127.0.0.1' ..."}

# ❌ Blocked — AWS instance metadata endpoint
result = await ingest_evidence(source_type="url", target="https://169.254.169.254/latest/meta-data/")
# → {"status": "BLOCKED_SSRF", "error": "Access to private/internal address '169.254.169.254' ..."}
```

### 3. Optional domain allowlist

Set the `INGEST_EVIDENCE_ALLOWED_DOMAINS` environment variable to a comma-separated list of
approved hostnames. When set, requests to any domain not in the list (or not a subdomain of
a listed domain) are rejected.

```bash
# Allow only specific trusted domains
export INGEST_EVIDENCE_ALLOWED_DOMAINS="example.com,trusted.org,docs.mycompany.com"
```

```python
# ✅ Allowed — exact match or subdomain match
result = await ingest_evidence(source_type="url", target="https://docs.example.com/api")

# ❌ Blocked — not in allowlist
result = await ingest_evidence(source_type="url", target="https://untrusted.net/data")
# → {"status": "BLOCKED_SSRF", "error": "Domain 'untrusted.net' is not in the configured allowlist ..."}
```

If `INGEST_EVIDENCE_ALLOWED_DOMAINS` is **not set**, all non-private public URLs are permitted
(the IP-range check still applies).

### BLOCKED_SSRF response envelope

All SSRF violations return the same envelope shape:

```json
{
  "source_type": "url",
  "target": "<the rejected URL>",
  "error": "<human-readable reason>",
  "status": "BLOCKED_SSRF"
}
```

---

## Final 13 Public Tools

### Core Constitutional Spine (8)

| # | Tool | Stage | Floor |
|---|------|-------|-------|
| 1 | `anchor_session` | 000_INIT | F11, F12 |
| 2 | `reason_mind` | 333_REASON | F2, F4, F7 |
| 3 | `recall_memory` | 444_SYNC | F4, F7 |
| 4 | `simulate_heart` | 555_EMPATHY | F5, F6 |
| 5 | `critique_thought` | 666_ALIGN | F4, F7, F8 |
| 6 | `eureka_forge` | 777_FORGE | F5, F6, F9 |
| 7 | `apex_judge` | 888_JUDGE | F1–F13 |
| 8 | `seal_vault` | 999_SEAL | F1, F3 |

### Evidence / Observability (4)

| # | Tool | Purpose |
|---|------|---------|
| 9 | `search_reality` | Discovery — find evidence candidates |
| 10 | `ingest_evidence` | Retrieval — fetch URL or inspect file (**NEW**) |
| 11 | `audit_rules` | Constitutional audit + rule validation |
| 12 | `check_vital` | System health diagnostics |

### Orchestration (1)

| # | Tool | Purpose |
|---|------|---------|
| 13 | `metabolic_loop` | Full 000→999 macro cycle |

---

## Archived Tools

These tools are **no longer available** in the public MCP surface:

| Tool | Status | Replacement |
|------|--------|-------------|
| `fetch_content` | Archived | `ingest_evidence(source_type="url", ...)` |
| `inspect_file` | Archived | `ingest_evidence(source_type="file", ...)` |
| `list_prompts` | Internal | Use MCP `prompts/list` endpoint |
| `get_prompt` | Internal | Use MCP `prompts/get` endpoint |
| `query_openclaw` | Internal | Dev-only (not in public API) |

The internal implementations remain in `aaa_mcp/server.py` as **non-decorated** helper
functions (`_fetch` / `_inspect_file`) and will not appear in `/tools/list`.

See `ARCHIVED_TOOLS/README.md` for full migration reference.

---

## MCP 2025-11-25 Compliance

arifOS now implements the full MCP specification:

### Endpoints

- ✅ `tools/list` - List all 13 public tools
- ✅ `tools/call` - Execute a tool
- ✅ `prompts/list` - List available prompt templates
- ✅ `prompts/get` - Get a specific prompt
- ✅ `resources/list` - List available resources
- ✅ `resources/read` - Read a resource
- ✅ `logging/setLevel` - Set logging level
- ✅ `completion/complete` - Autocomplete support

### Features

- ✅ Pagination support for large lists
- ✅ JSON-RPC 2.0 protocol
- ✅ Proper error handling
- ✅ Input validation (F12: Injection Defense)
- ✅ Health endpoint compliance

---

## Breaking Changes

| Change | Impact | Fix |
|--------|--------|-----|
| `fetch_content` removed from public surface | Calls will fail | Migrate to `ingest_evidence(source_type="url", ...)` |
| `inspect_file` removed from public surface | Calls will fail | Migrate to `ingest_evidence(source_type="file", ...)` |
| `/tools/list` now returns exactly 13 tools | Health checks expecting 15+ will fail | Update count assertions to 13 |
| `_ALLOWED_TOOLS` frozenset updated | Calls to old names denied at F12 layer | Update tool name to `ingest_evidence` |

---

## Migration Checklist

- [ ] Replace all `fetch_content()` calls with `ingest_evidence(source_type="url", ...)`
- [ ] Replace all `inspect_file()` calls with `ingest_evidence(source_type="file", ...)`
- [ ] Remove direct calls to `list_prompts` / `get_prompt` (use MCP endpoints)
- [ ] Update any hardcoded tool lists to use `AAA_CANONICAL_TOOLS`
- [ ] Run tests: `pytest tests/test_13_tools_compliance.py`
- [ ] Verify MCP spec compliance: Check `/tools/list` endpoint
- [ ] Update documentation and examples

---

## Compliance Verification

```bash
# Run 13-tool compliance tests
pytest tests/test_13_tools_compliance.py -v

# Verify canonical count
python -c "from aaa_mcp.protocol.aaa_contract import AAA_CANONICAL_TOOLS; print(len(AAA_CANONICAL_TOOLS))"
# Expected: 13

# Verify no ghost imports
grep -n "fetch_content\|inspect_file" aaa_mcp/server.py | grep "@mcp.tool"
# Expected: (no output)

# Check tools/list returns 13 tools
curl -X POST http://localhost:8080/rpc \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","id":1}' \
  | jq '.result.tools | length'
# Should output: 13
```

---

## Rollback Instructions

If you need to rollback:

1. **Revert the commit:**
   ```bash
   git revert <commit-hash>
   git push
   ```

2. **Restore old tools from ARCHIVED_TOOLS/:**
   ```bash
   cp ARCHIVED_TOOLS/fetch_content.py.archived aaa_mcp/tools/fetch_content.py
   cp ARCHIVED_TOOLS/inspect_file.py.archived aaa_mcp/tools/inspect_file.py
   ```

3. **Update `aaa_contract.py`** to include old tools

---

## FAQ

### Q: Why merge fetch_content and inspect_file?

**A:** They're semantically identical operations:
- Both retrieve and examine a specific object
- Both apply the same floors (F2, F4, F12)
- The only difference is the source type (URL vs file)

Merging them creates a cleaner mental model:
- `search_reality` = find things (exploration)
- `ingest_evidence` = examine things (retrieval)

### Q: What happens if I call fetch_content now?

**A:** The old tools are **no longer registered** on the public MCP surface — they will not
appear in `/tools/list` and any attempt to call them via `tools/call` will be rejected by
the F12 (Injection Defense) gate. The internal implementations still exist as non-decorated
helper functions (`_fetch` / `_inspect_file`) in `aaa_mcp/server.py` for rollback purposes,
but they are not reachable through the public API.

### Q: Are the 13 tools final?

**A:** Yes. This is the **canonical 13-tool surface** for MCP deployment. Any changes require
constitutional review.

### Q: How do I access internal tools like query_openclaw?

**A:** Internal tools are not exposed via MCP `/tools/list`. They're available for dev/ops use
but not part of the public API.

---

## References

- `ARCHIVED_TOOLS/README.md` for full migration reference
- `tests/test_13_tools_compliance.py` for usage examples
- `aaa_mcp/tools/ingest_evidence.py` for implementation details
- MCP spec: https://modelcontextprotocol.io/specification/2025-11-25/

---

*Migration effective: 2026-03-06*  
*Target MCP Spec: 2025-11-25*  
*arifOS Version: v60.0-FORGE*
