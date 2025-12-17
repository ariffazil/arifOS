# FAG (File Access Governance) Quick Start

**Version:** v41.0.0-alpha  
**Status:** ✅ SHIPPED (12/12 tests passing)  
**Phase:** v41 Early Access (Safe-FS renamed to FAG)

---

## What is FAG?

**FAG (File Access Governance)** is a constitutional wrapper around filesystem I/O that enforces arifOS's 9 floors **before** files are read. It prevents:

- **Secret leaks** (.env, SSH keys, credentials)
- **Path traversal** attacks (F1 Amanah root jail)
- **Binary confusion** (F4 DeltaS - text files only)
- **Nonexistent files** (F2 Truth - must be real)

---

## 3-Minute Install & Test

### Installation

```bash
pip install -e .
```

### CLI Usage

```bash
# Read a safe file (SEAL verdict)
arifos-safe-read --path README.md

# Try to read forbidden file (VOID verdict)
arifos-safe-read --path .env
# Returns: [VOID] F9 C_dark FAIL: Forbidden pattern detected

# Custom root jail
arifos-safe-read --path subfolder/data.txt --root /path/to/jail

# JSON output (for scripts)
arifos-safe-read --path config.yaml --json

# Quiet mode (content only)
arifos-safe-read --path notes.txt --quiet
```

### Python API

```python
from arifos_core.fag import FAG

# Initialize with root jail
fag = FAG(
    root="/path/to/project",
    read_only=True,
    enable_ledger=True,
    job_id="analysis-001"
)

# Read file with constitutional checks
result = fag.read("src/main.py")

if result.verdict == "SEAL":
    print(result.content)
    print(f"Ledger ID: {result.ledger_entry_id}")
else:
    print(f"Access denied: {result.reason}")
```

### MCP Integration (VS Code / Cursor)

```python
from arifos_core.mcp.tools.fag_read import arifos_fag_read, FAGReadRequest

# Call via MCP
request = FAGReadRequest(
    path="data/sensitive.json",
    root="/workspace",
    enable_ledger=True
)

response = arifos_fag_read(request)
print(response.verdict)  # SEAL | VOID | 888_HOLD
```

---

## The 5 Floor Checks

| Floor | Check | Example Failure |
|-------|-------|----------------|
| **F1 Amanah** | Path must stay within root jail | `../../../etc/passwd` → VOID |
| **F2 Truth** | File must exist, be readable, AND be read in FULL | `nonexistent.txt` → VOID |
| **F4 DeltaS** | File must be text (not binary) | `image.png` → VOID |
| **F5 Peace²** | Metadata validation (placeholder) | Reserved for future |
| **F9 C_dark** | No forbidden patterns (.env, SSH keys) | `.env` → VOID |

---

## F2 — TRUTH (STRICT)

> **Core Principle (Locked):** Truth without completeness is not Truth. Partial reading = false claim = F2 violation.

Truth claims REQUIRE full document ingestion.

If a file, document, link, or folder is provided:
- **100% of its content MUST be read**
- No truncation, skipping, or heuristic selection is allowed

Partial reading, silent truncation, or summarisation-first behavior constitutes a **TRUTH VIOLATION**.

If full reading is not technically possible:
- The agent MUST **declare this explicitly**
- The agent MUST **STOP**
- The agent MUST **request a readable format**

**Proceeding anyway = false claim = F2 breach.**

---

## TRUTH SAFEGUARD — PDF HANDLING

PDF files are **HIGH-RISK** for Truth violations due to truncation and layout loss.

**Rules:**
- PDFs are accepted for transport only
- Canonical reasoning MUST use Markdown (`.md`) or plain text
- Any PDF in `L1_THEORY/` or `canon/` MUST have a `.md` companion
- AI MUST read the `.md`, NOT the PDF

Image-based or scanned PDFs are rejected by default.

---

## TRUTH CONTEXT — CANON PRIORITY

Before any reasoning or judgment, the following files are **REQUIRED READING**:

- `L1_THEORY/canon/00_foundation/030_ARIF_FAZIL.md`

Failure to read required canon files invalidates all downstream Truth claims.

---

## TRUTH DISCLOSURE REQUIREMENT

If any part of the provided material is skipped, truncated, reordered, or lost:
- The agent MUST **disclose it**
- The agent MUST **STOP**

**Silence or continuation implies a false claim of Truth.**

---


## Forbidden Patterns (50+ Regex)

### Secrets & Credentials
- `.env`, `.env.local`, `.env.*`
- `id_rsa`, `id_dsa`, `id_ecdsa`, `*.pem`, `*.key`
- `credentials.json`, `service-account.json`
- `.aws/credentials`, `.gcp/credentials`

### Git Internals
- `.git/config`, `.git/objects/`, `.git/HEAD`

### System Files
- `/etc/passwd`, `/etc/shadow`, `SAM`, `SYSTEM`

### Cloud Secrets
- `.azure/`, `.gcloud/`, `.kube/config`

**Full list:** See `arifos_core/fag.py` lines 47-106.

---

## Verdicts Explained

| Verdict | Meaning | Exit Code | Example |
|---------|---------|-----------|---------|
| **SEAL** | All floors passed. Content returned. | 0 | `README.md` → ✅ |
| **VOID** | Critical breach (F1/F2/F9 fail). Access denied. | 1 | `.env` → ❌ |
| **888_HOLD** | Ambiguous case. Human review needed. | 88 | Reserved |

---

## Integration Tests (12/12 Passing)

```bash
pytest tests/test_fag.py -v
```

### Test Coverage

| Test Class | Count | Focus |
|------------|-------|-------|
| `TestFAGBasicRead` | 2 | Safe file reads, subdirectory access |
| `TestFAGF1Amanah` | 2 | Path traversal blocking, root jail enforcement |
| `TestFAGF2Truth` | 2 | Nonexistent files, directory rejection |
| `TestFAGF4DeltaS` | 1 | Binary file rejection |
| `TestFAGF9CDark` | 2 | .env blocking, SSH key blocking |
| `TestFAGConvenienceFunction` | 1 | `fag_read()` wrapper |
| `TestFAGLedgerIntegration` | 2 | Cooling Ledger enable/disable |

---

## Architecture

### Class: `FAG`

```python
class FAG:
    def __init__(
        self,
        root: str = ".",
        read_only: bool = True,
        enable_ledger: bool = True,
        job_id: str = "fag-session"
    )

    def read(self, path: str) -> FAGReadResult
```

### Dataclass: `FAGReadResult`

```python
@dataclass
class FAGReadResult:
    verdict: str                    # SEAL | VOID | 888_HOLD
    path: str                       # Absolute path
    content: Optional[str]          # File content (if SEAL)
    reason: Optional[str]           # Why VOID/HOLD?
    floor_scores: Dict[str, float] # F1-F9 scores
    ledger_entry_id: Optional[str] # Cooling Ledger ID (if enabled)
```

---

## Key Files

| File | Purpose |
|------|---------|
| `arifos_core/fag.py` | Core FAG class (400+ lines) |
| `scripts/arifos_safe_read.py` | CLI tool (150+ lines) |
| `arifos_core/mcp/tools/fag_read.py` | MCP tool wrapper (100+ lines) |
| `tests/test_fag.py` | Test suite (175 lines, 12 tests) |
| `pyproject.toml` | CLI registration (`[project.scripts]`) |

---

## Design Decisions

### Why "Deny by Default"?

FAG starts with **VOID verdict** and only upgrades to **SEAL** if all floors pass. This is constitutional pessimism:

- Safer to reject good than accept bad
- Explicit allow-listing (forbidden patterns must be removed)
- F1 Amanah LOCK: no exceptions

### Why "Read-Only"?

Write operations require human approval (888_HOLD). v41.0.0-alpha only supports **reads**. Future versions may add:

- `FAG.write()` with Phoenix-72 approval
- `FAG.delete()` with Tri-Witness consensus
- `FAG.execute()` with zkPC proof

### Why "Root Jail"?

F1 Amanah demands reversibility. Root jail ensures:

- No `/etc/passwd` access
- No `C:\Windows\System32` tampering
- Symlink resolution stays within jail
- Absolute paths rejected

---

## Troubleshooting

### Issue: "Command not found: arifos-safe-read"

**Solution:** Reinstall package:

```bash
pip install -e .
```

### Issue: "VOID verdict but file exists"

**Possible reasons:**

1. File matches forbidden pattern (check `arifos_core/fag.py` lines 47-106)
2. File is binary (check with `file` command)
3. Path outside root jail (use `--root` flag)

### Issue: "Ledger entry not created"

**Check:**

- `enable_ledger=True` in constructor
- Cooling Ledger directory exists (`cooling_ledger/`)
- Verdict is SEAL or SABAR (VOID doesn't log)

---

## Future Roadmap (v41 → v42)

| Version | Feature | Status |
|---------|---------|--------|
| **v41.0.0** | FAG read with 5 floors | ✅ SHIPPED |
| **v41.1** | Write operations (Phoenix-72 gated) | PLANNED Q1 2026 |
| **v41.2** | Directory scans with aggregate verdicts | PLANNED Q2 2026 |
| **v42.0** | zkPC proofs for I/O (cryptographic receipts) | RESEARCH |

---

## Philosophy

> **"File access is governance, not convenience."**

In traditional systems, file I/O is a technical operation. In arifOS, **every read is a constitutional decision**:

- Does this serve the weakest stakeholder? (F6 Kr)
- Is this reversible? (F1 Amanah)
- Does this reduce confusion? (F4 DeltaS)
- Am I certain this is safe? (F7 Omega0)

FAG embeds these questions **into the filesystem layer**, making bad I/O structurally impossible.

---

**Made with 🔥 by Arif Fazil**  
*v41.0.0-alpha | 12/12 Tests Passing | CLI + Python + MCP | Deny by Default*  
*Last Updated: January 2025 | Safe-FS → FAG Rename | Phase 1 Complete*
