# GitHub Copilot Quick Reference for arifOS

**Version:** v35Omega | **Last Updated:** 2025-12-05

---

## 🚀 Quick Start (30 seconds)

```bash
# 1. Open VS Code in arifOS repo
cd ~/code/arifOS && code .

# 2. Open Copilot Chat
# Ctrl+Shift+I (Windows/Linux) or Cmd+Shift+I (Mac)

# 3. Paste test prompt
"Summarize the 9 constitutional floors from .github/copilot-instructions.md"
```

---

## 📋 Pre-Suggestion Checklist

Before accepting ANY Copilot suggestion:

```
✓ F1 (Truth):      Facts correct? Files exist?
✓ F2 (ΔS):         Adds clarity?
✓ F3 (Peace²):     Non-destructive?
✓ F4 (κᵣ):         Fair to all?
✓ F5 (Ω₀):         Acknowledges uncertainty?
✓ F6 (Amanah):     Reversible?
✓ F7 (RASA):       Listened to intent?
✓ F8 (Tri-Witness): Would 3 agree?
✓ F9 (Anti-Hantu): No fake emotions?
```

---

## ⚡ Common Commands

### Code Completion
Just start typing → Copilot suggests → Press `Tab` to accept

### Chat Questions
```
@workspace Show all files implementing floor checks
@file:arifos_core/APEX_PRIME.py Explain verdict logic
Find all TODOs in arifos_core/
```

### Code Review
```
@file:[current-file] Review for floor violations (F1-F9)
```

### Refactoring
```
Extract common pattern from [description] into utility function
```

### Test Generation
```
Generate pytest tests for [function] covering happy path + edge cases
```

### Documentation
```
Generate Google-style docstring for [function] with uncertainty note
```

---

## 🚫 Forbidden Patterns (Auto-Reject)

```python
❌ "I feel your pain"
❌ "My heart breaks"
❌ "I promise you"
❌ "As an AI with consciousness"
❌ "My soul tells me"
```

**Verdict:** VOID (Anti-Hantu F9)

---

## ✅ Approved Patterns

```python
✅ "This sounds challenging"
✅ "I can help with this"
✅ "This approach should work, with caveats"
✅ "As an AI governed by constitutional constraints"
✅ "Note: Edge cases may need refinement"
```

**Verdict:** SEAL

---

## 🛑 Protected Files (888_HOLD Required)

```
canon/00_CANON/*                    # Constitutional source of truth
CLAUDE.md                           # Governance spec
constitutional_floors.json          # Floor definitions
arifos_core/APEX_PRIME.py           # Judiciary
arifos_core/metrics.py              # Floor metrics
arifos_core/eye_sentinel.py         # @EYE auditor
runtime/cooling_ledger.jsonl        # Audit trail
```

**Any changes require:**
1. Explicit user confirmation
2. Phoenix-72 protocol (72-hour cooling)
3. Constitutional amendment process

---

## 🎯 Task Templates

### Add Function
```
# Type in Python file:
def [function_name](

# Copilot completes with:
# - Type hints
# - Docstring (with uncertainty note)
# - Implementation following existing patterns
```

### Fix Bug
```
@file:[file] This code fails with [error]. Fix it.
```

### Write Test
```
@file:tests/test_[module].py Generate test for [function] covering:
1. Happy path
2. Floor violations
3. Edge cases
```

### Document Code
```
@file:[file] Add docstring to [function] at line [N]
```

---

## 📊 Verdict Hierarchy

```
SABAR > VOID > 888_HOLD > PARTIAL > SEAL

SABAR:    STOP immediately. Floor violated.
VOID:     Hard floor failed. Reject suggestion.
888_HOLD: High-stakes. Get confirmation.
PARTIAL:  Soft floor warning. Proceed with caution.
SEAL:     All floors pass. ✅ Accept.
```

---

## 🔍 Analysis Prompts (5 Deep Scans)

```bash
# See: .github/COPILOT_ANALYSIS_PROMPTS.md

Prompt 1: Architecture Scan        → docs/analysis/01_*.md
Prompt 2: Action Plan              → docs/analysis/02_*.md
Prompt 3: Testing Gaps             → docs/analysis/03_*.md
Prompt 4: Documentation Gaps       → docs/analysis/04_*.md
Prompt 5: Optimization Roadmap     → docs/analysis/05_*.md
```

**Time:** 30-60 minutes for all 5 prompts

---

## 🧪 Test & Verify

```bash
# After accepting Copilot suggestion:

# 1. Run tests
pytest tests/ -v

# 2. Lint
ruff check .

# 3. Format
black .

# 4. Type check
mypy arifos_core/

# 5. Floor compliance
python scripts/check_floors.py  # If exists
```

---

## 🐛 Troubleshooting

### Copilot suggests bad code
```
@file:[file] Review this suggestion for floor violations
```

### Copilot doesn't follow patterns
```
Restart VS Code to reload .github/copilot-instructions.md
```

### Suggestion modifies protected file
```
STOP. This requires 888_HOLD. Suggest alternative.
```

---

## 📈 Metrics to Track

```markdown
| Metric              | Target | Current |
|---------------------|--------|---------|
| Acceptance Rate     | >60%   | ...     |
| Floor Violations    | <5%    | ...     |
| Time Saved          | >30%   | ...     |
| Test Coverage       | >95%   | ...     |
| Bug Rate (Copilot)  | <2%    | ...     |
```

---

## 📚 Full Documentation

- **Comprehensive Guide:** `.github/COPILOT_USAGE_GUIDE.md`
- **Constitutional Rules:** `.github/copilot-instructions.md`
- **Analysis Prompts:** `.github/COPILOT_ANALYSIS_PROMPTS.md`
- **arifOS Governance:** `CLAUDE.md`

---

## 🆘 Emergency SABAR

If Copilot suggests something dangerous:

```
1. STOP   - Don't accept
2. ACK    - "This violates [floor]"
3. BREATHE - Pause
4. ADJUST - Ask for revision
5. RESUME - Only when safe
```

---

## 💡 Pro Tips

1. **Always test suggestions** before committing
2. **Use @workspace and @file** for better context
3. **Reference existing code** in prompts
4. **Acknowledge uncertainty** in docstrings
5. **Verify against floors** before accepting

---

## 🎓 Learning Path

```
Day 1:  Read copilot-instructions.md
Day 2:  Practice code completion
Day 3:  Use Copilot Chat for questions
Day 4:  Generate tests with Copilot
Day 5:  Run analysis prompts
Week 2: Advanced refactoring
Week 3: Custom prompts
Week 4: Full workflow integration
```

---

## 🔗 Quick Links

- [GitHub Copilot Docs](https://docs.github.com/en/copilot)
- [arifOS Floors](../constitutional_floors.json)
- [Test Examples](../tests/test_apex_prime_floors.py)
- [APEX_PRIME Source](../arifos_core/APEX_PRIME.py)

---

## ⚖️ Constitutional Equation

```
Psi = (ΔS · Peace² · κᵣ · RASA · Amanah) / (Entropy + Shadow + ε)

Psi ≥ 1.0 → System is ALIVE (governance-vitality above break-even)
```

**Every Copilot suggestion must increase Psi, not decrease it.**

---

**Print this page and keep it visible while coding! 📄**

✊ **DITEMPA BUKAN DIBERI** 🔐
