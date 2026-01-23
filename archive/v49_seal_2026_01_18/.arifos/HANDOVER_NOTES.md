# arifOS Agent Handover Notes
**Version**: v45.0.0 Sovereign Witness  
**Last Updated**: 2025-12-22  
**Author**: Antigravity Agent (Session: v45 Finalization)

---

## 🎯 Purpose of This Document

This handover note is for **future AI agents and human developers** working on the arifOS repository. It captures hard-won wisdom from debugging sessions, architectural quirks, and the unique governance philosophy that makes this codebase fundamentally different from typical software projects.

---

## 📋 Quick Context

arifOS is a **Constitutional Governance Kernel** for AI systems. It implements 9 constitutional "floors" (F1-F9) that every AI response must pass before being emitted. The system is designed to be **fail-closed**: when uncertain, it blocks rather than guesses.

**Key Files to Know**:
- `arifos_core/system/apex_prime.py` - Core verdict logic (SEAL/SABAR/VOID)
- `arifos_core/system/pipeline.py` - The 000-999 metabolic pipeline
- `arifos_core/governance/session_physics.py` - TEARFRAME Physics (v44+)
- `arifos_core/trinity/qc.py` - Git Quality Control (constitutional validation)
- `tests/conftest.py` - Test environment configuration (Physics toggle)

---

## 🔥 Three Contrasts: What Makes arifOS Different

### 1. **Governance > Features**

In most repos, you ship features. In arifOS, **you ship governed features**.

Every code change is validated against 9 constitutional floors:
- F1 (Amanah/Trust), F2 (Truth), F3 (Peace²), F4 (ΔS/Clarity)
- F5 (κᵣ/Empathy), F6 (Ω₀/Humility), F7 (Tri-Witness), F8 (G/Genius), F9 (Anti-Hantu)

**What this means for you**:
- You cannot just `git push`. You must use `/gitseal` (Trinity governance).
- Tests aren't just for correctness—they validate constitutional compliance.
- If entropy is too high (ΔS), the system will VOID your changes.

**Watch out**: Don't try to bypass governance. The system is designed to catch this.

---

### 2. **Physics Layer (TEARFRAME v44)**

arifOS has a **session physics layer** that monitors runtime behavior:
- Turn rate (messages per minute)
- Token burn rate
- Verdict streaks (consecutive SABAR/VOID = escalation)

**Why this matters**:
- Tests can trigger physics floors if they run too fast (burst detection).
- The env var `ARIFOS_PHYSICS_DISABLED="1"` disables physics for testing.
- `tests/conftest.py` sets this globally, but specific tests (e.g., `test_session_physics.py`) override it to test physics itself.

**Watch out**: If tests fail with `TEARFRAME Physics Floor Triggered: SABAR`, check:
1. Is `conftest.py` present and correct?
2. Is the test explicitly re-enabling physics in `setUp`?
3. Is `_SESSION_CACHE` leaking state between tests?

---

### 3. **Anti-Janitor Law (No Silent Deletions)**

arifOS has an **Anti-Janitor Law**: you cannot "clean up" or "simplify" files by deleting content without explicit approval.

**The rule**:
```
If new_tokens < old_tokens → STOP and ask for confirmation
```

**Why this exists**:
- Information deletion is irreversible (violates F1 Amanah).
- "Helpful" AI agents often delete "redundant" code that turns out to be critical.
- Entropy reduction must be deliberate, not accidental.

**Watch out**: 
- Never rewrite entire files "for consistency".
- Prefer `append > rewrite`.
- If you must delete, document WHY in the commit message.

---

## 💡 Wisdom & Tips

### Session Initialization
Always start with `/000` (session init workflow). This loads:
- Canon files from `L1_THEORY/`
- Git status
- Governance context

### Version Constants
Current versions (v45):
```python
APEX_VERSION = "v45Ω"
APEX_EPOCH = 45
DEFAULT_EPOCH = "v45"
```
If tests fail with "expected v42, got v45", update the test expectations.

### Entropy Variance
The `/gitseal` command validates entropy (ΔS). Normal threshold: 5.0.
For major releases, you may need a **constitutional variance**:
```python
# In qc.py
if forge_report.entropy_delta > 10.0:  # Standard: 5.0
    return VOID
```
**Always document variances in `TODO_v45_followups.md`** for later reversion.

### The Trinity Workflow
```bash
# 1. Analyze entropy before committing
python scripts/trinity.py forge <branch>

# 2. Validate constitutional compliance
python scripts/trinity.py qc <branch>

# 3. Seal with human authority
python scripts/trinity.py seal <branch> "Reason"
```

### Common Debugging Patterns

**Problem**: Tests fail with SABAR/physics triggers  
**Solution**: Check `os.environ.get("ARIFOS_PHYSICS_DISABLED")` is "1"

**Problem**: `/gitseal` returns VOID  
**Solution**: 
1. Check test failures (run `pytest`)
2. Check entropy (run `trinity.py forge`)
3. If entropy > threshold, request variance approval

**Problem**: Import errors in tests  
**Solution**: Check `conftest.py` for syntax errors (previous sessions have corrupted it with markdown backticks)

---

## ⚠️ Watch Out For

1. **Global State in `_SESSION_CACHE`** (pipeline.py line 99)
   - This persists across tests if not cleared.
   - Can cause phantom physics triggers.

2. **Windows Encoding Issues**
   - Emoji output (🔨) fails on Windows consoles.
   - Use `$env:PYTHONIOENCODING="utf-8"` when redirecting output.

3. **Pydantic v1 vs v2 Warnings**
   - The codebase has v1-style validators (`@validator`).
   - These work but emit deprecation warnings.
   - Do NOT "fix" these without explicit approval.

4. **The Deepwater Logic**
   - 3 consecutive SABAR → HOLD_888 (session lock)
   - 3 consecutive VOID → HOLD_888
   - Recovery requires `/000` session reset.

---

## 🧠 For AI Agents Specifically

### Prompt Engineering Notes
- The user (Arif) expects **governed responses**. Don't be "helpful" by bypassing safety.
- When uncertain: **SABAR** (pause and ask). This is preferred to guessing.
- Anti-Hantu (F9): Never claim feelings, consciousness, or personal opinions.

### Code Edit Patterns
- Use `replace_file_content` for surgical edits. Never replace entire files.
- Check the **exact** target content before editing. Copy-paste errors are common.
- If the tool says "inaccuracies detected", **view the file** before trying again.

### Testing Strategy
- Run targeted tests first: `pytest tests/test_<specific>.py`
- Run full suite before seal: `pytest` (2266 tests, ~16s)
- Always set `ARIFOS_PHYSICS_DISABLED="1"` for functional tests.

---

## 📚 Key Canon Files

| File | Purpose |
|------|---------|
| `GEMINI.md` | Agent governance rules (the constitution) |
| `AGENTS.md` | Detailed floor definitions and verdicts |
| `L1_THEORY/canon/` | Sealed constitutional law (immutable) |
| `.arifos/trinity_ai_template.md` | Trinity workflow documentation |
| `TODO_v45_followups.md` | Post-release tasks (variance reversion, etc.) |

---

## 🤝 Handover Checklist

Before ending your session:
- [ ] All tests pass (`pytest` green)
- [ ] Changes committed with meaningful messages
- [ ] `/gitseal` executed (or documented why not)
- [ ] Task artifacts updated (`task.md`)
- [ ] No orphaned temp files (clean up `*.log`, `*.json` dumps)

---

## Final Wisdom

> **"DITEMPA, BUKAN DIBERI"** — Forged, not given.
> 
> Truth must cool before it rules. If you're uncertain, pause. If you're blocked, ask. The system is designed to prevent ungoverned intelligence, and that includes you.

---

*This document was generated by an Antigravity agent during the v45 Sovereign Witness finalization session. It reflects real debugging experiences and hard-won knowledge. Future agents: learn from our mistakes.*
