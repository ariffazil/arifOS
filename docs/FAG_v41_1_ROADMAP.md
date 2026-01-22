# FAG v41.1 Roadmap — Write Operations with Phoenix-72

**Status:** PLANNED (Q1 2026)  
**Blocked Until:** v41.0.0-alpha validation complete (12/12 tests passing ✅)

---

## Executive Summary

FAG v41.0.0-alpha ships **read-only** filesystem governance. v41.1 extends this to **write operations** (create, update, delete) with Phoenix-72 amendment approval. This maintains constitutional sovereignty: AI proposes, humans seal.

---

## Design Principles

### 1. Authority Boundary (INV-2)

**Rule:** Write operations require **explicit human approval** via Phoenix-72.

| Operation | Risk | Approval Gate |
|-----------|------|---------------|
| **Read** | Low (info disclosure) | Floor checks only (v41.0) |
| **Write** | Medium (data corruption) | Phoenix-72 proposal + human seal |
| **Delete** | High (data loss) | Phoenix-72 + Tri-Witness consensus |
| **Execute** | Critical (system compromise) | v42+ (zkPC proof required) |

### 2. Reversibility (F1 Amanah)

**All write operations must be reversible:**

- File writes → Git commits (revertible)
- File deletes → Move to `.arifos_trash/` (recoverable for 90 days)
- No `shutil.rmtree()`, no `TRUNCATE`, no `DROP TABLE`

### 3. Cooling Period (SABAR)

**High-stakes writes require cooling:**

- Write proposals → 888_HOLD verdict
- 24-hour minimum review period
- Human approval via `arifos-seal-canon --file <proposal.json>`

---

## Proposed API

### Class: `FAG` (Extended)

```python
class FAG:
    """File Access Governance with constitutional I/O."""

    def __init__(
        self,
        root: str = ".",
        read_only: bool = True,  # v41.1: Becomes configurable
        enable_ledger: bool = True,
        job_id: str = "fag-session"
    )

    # v41.0.0 (SHIPPED)
    def read(self, path: str) -> FAGReadResult

    # v41.1 (PLANNED)
    def write(self, path: str, content: str) -> FAGWriteResult
    def delete(self, path: str) -> FAGDeleteResult
    def append(self, path: str, content: str) -> FAGWriteResult
```

### New Dataclass: `FAGWriteResult`

```python
@dataclass
class FAGWriteResult:
    verdict: str                    # 888_HOLD | VOID (never SEAL)
    path: str                       # Absolute path
    proposal_id: str                # Phoenix-72 proposal ID
    reason: Optional[str]           # Why 888_HOLD or VOID?
    floor_scores: Dict[str, float] # F1-F9 scores
    ledger_entry_id: Optional[str] # Cooling Ledger ID
```

### New Dataclass: `FAGDeleteResult`

```python
@dataclass
class FAGDeleteResult:
    verdict: str                    # 888_HOLD | VOID (requires Tri-Witness)
    path: str                       # Absolute path
    trash_path: Optional[str]       # Path in .arifos_trash/ (if moved)
    proposal_id: str                # Phoenix-72 proposal ID
    reason: Optional[str]           # Why 888_HOLD or VOID?
    floor_scores: Dict[str, float] # F1-F9 scores
    ledger_entry_id: Optional[str] # Cooling Ledger ID
```

---

## Floor Enforcement

| Floor | Read Check | Write Check | Delete Check |
|-------|------------|-------------|--------------|
| **F1 Amanah** | Path within jail | Reversible (Git/trash) | Move to trash (not rm) |
| **F2 Truth** | File exists | Parent directory exists | File exists before delete |
| **F4 DeltaS** | Not binary | Content is text | N/A |
| **F5 Peace²** | Metadata OK | Content non-toxic | N/A |
| **F7 Omega0** | Confidence 0.04 | Confidence 0.04 | Confidence 0.03 (cautious) |
| **F9 C_dark** | No secrets | No secrets in content | Cannot delete protected files |

### New Forbidden Write Patterns (F9 C_dark)

| Pattern | Risk | Action |
|---------|------|--------|
| Write to `.git/` | Repository corruption | VOID |
| Write to `/etc/`, `/sys/`, `/proc/` | System damage | VOID |
| Write to `C:\Windows\` | Windows corruption | VOID |
| Write credentials to disk | Secret leakage | VOID |
| Delete `.git/`, `README.md`, `LICENSE` | Project corruption | 888_HOLD + Tri-Witness |

---

## Phoenix-72 Integration

### Write Proposal Flow

```
1. AI calls FAG.write(path, content)
   ↓
2. FAG checks floors (F1, F2, F4, F5, F9)
   ↓
3. If floors pass:
   - Verdict: 888_HOLD
   - Create Phoenix-72 proposal
   - Log to Cooling Ledger
   - Return FAGWriteResult with proposal_id
   ↓
4. Human reviews proposal:
   arifos-propose-canon --list
   arifos-seal-canon --file proposals/FAG_WRITE_<id>.json
   ↓
5. On human approval:
   - Write content to disk
   - Git commit (if in repo)
   - Update ledger with SEAL verdict
```

### Delete Proposal Flow

```
1. AI calls FAG.delete(path)
   ↓
2. FAG checks Tri-Witness consensus (Human + AI + Earth)
   ↓
3. If critical file (README, LICENSE, .git/):
   - Verdict: 888_HOLD
   - Require explicit approval
   ↓
4. If non-critical:
   - Move to .arifos_trash/
   - Create restoration script
   - Log to Cooling Ledger
   ↓
5. Trash retention: 90 days (WARM band)
   - After 90d: Human approval required for permanent deletion
```

---

## CLI Extensions

### v41.1 New Commands

```bash
# Propose a file write
arifos-safe-write --path notes.txt --content "Hello arifOS" --dry-run

# Propose a file delete
arifos-safe-delete --path temp.log --reason "No longer needed"

# Review pending proposals
arifos-list-proposals --type fag_write

# Approve a write
arifos-seal-canon --file proposals/FAG_WRITE_20260115_001.json

# Restore from trash
arifos-restore-file --trash-id <id>

# Empty trash (requires approval)
arifos-empty-trash --older-than 90d
```

---

## Test Plan (36 Tests Planned)

### Test Suites

| Suite | Count | Focus |
|-------|-------|-------|
| `test_fag_write.py` | 12 | Write operations, Phoenix-72 proposals |
| `test_fag_delete.py` | 12 | Delete operations, trash recovery |
| `test_fag_phoenix_integration.py` | 6 | Phoenix-72 approval flow |
| `test_fag_git_integration.py` | 6 | Git commit automation |

### Key Test Cases

**Write Operations:**
- Safe write (text file, within jail) → 888_HOLD
- Write to .git/ → VOID
- Write to /etc/ → VOID
- Write binary content → VOID
- Write secrets to disk → VOID
- Human approval → SEAL + Git commit

**Delete Operations:**
- Delete temp file → Move to trash
- Delete README.md → 888_HOLD
- Delete .git/ → VOID
- Path traversal delete → VOID
- Restore from trash → SEAL
- Empty trash (90d old) → SEAL

---

## Security Considerations

### Attack Vectors

| Attack | Mitigation |
|--------|------------|
| **Write to .env** | F9 C_dark blocks credential writes |
| **Delete .git/** | 888_HOLD + Tri-Witness required |
| **Trash overflow** | 90-day auto-cleanup with ledger |
| **Git history rewrite** | VOID (no rebase, no force push) |
| **Symlink race** | Resolve symlinks, check jail boundary |

### Hard Stops (VOID Immediately)

- Write to system directories (`/etc/`, `C:\Windows\`)
- Delete protected files (README, LICENSE, .git/)
- Trash escape (symlinks outside jail)
- Git history modification (rebase, force push)

---

## Migration Path

### From v41.0.0-alpha to v41.1

**No breaking changes:**

- Default: `read_only=True` (v41.0 behavior)
- To enable writes: `FAG(root=".", read_only=False)`
- All writes require Phoenix-72 approval (888_HOLD)

**Opt-in feature flags:**

```python
fag = FAG(
    root=".",
    read_only=False,          # Enable writes (default: True)
    enable_ledger=True,       # Log all operations (default: True)
    require_approval=True,    # Force 888_HOLD (default: True)
    git_auto_commit=True,     # Auto-commit on seal (default: False)
)
```

---

## Roadmap Timeline

| Milestone | Date | Deliverable |
|-----------|------|-------------|
| **v41.0.0** | ✅ January 2025 | Read-only FAG (SHIPPED) |
| **v41.1-alpha** | February 2025 | Write proposal engine |
| **v41.1-beta** | March 2025 | Delete operations + trash |
| **v41.1-rc1** | April 2025 | Phoenix-72 integration tests |
| **v41.1-stable** | May 2025 | Git automation + docs |

---

## Hard Gates (v41.1 Blocked Until)

- ✅ v41.0.0 test suite passing (12/12)
- ✅ Cooling Ledger stable
- ✅ Phoenix-72 approval flow validated
- ⏳ MCP integration tested (in progress)
- ⏳ Write proposal schema finalized

**If a gate fails → pause, fix, retest. Do not rush.**

---

## Philosophy

> **"Write operations are constitutional decisions, not file operations."**

In traditional systems, writing to disk is a technical operation. In arifOS, **every write is a Phoenix-72 proposal**:

- Does this serve the project? (F6 Kr)
- Is this reversible? (F1 Amanah)
- Am I certain this is safe? (F7 Omega0)
- Has a human approved this? (INV-2 Authority Boundary)

FAG v41.1 embeds these questions into the filesystem layer, making ungoverned writes structurally impossible.

---

**DITEMPA BUKAN DIBERI** — Forged, not given. Write with intent, delete with consensus.

*Last Updated: January 2025 | v41.1 Planning | Phoenix-72 Integration Pending*
