# Getting Started with GitHub Copilot for arifOS

**Version:** v35Omega | **Estimated Time:** 15 minutes

Welcome! This guide will get you up and running with GitHub Copilot for arifOS development in 15 minutes.

---

## Prerequisites

- GitHub account with Copilot access
- VS Code installed
- arifOS repository cloned locally

---

## Step 1: Install GitHub Copilot (2 minutes)

### In VS Code:

1. Open Extensions (`Ctrl+Shift+X`)
2. Search for "GitHub Copilot"
3. Install both:
   - **GitHub Copilot** (code completions)
   - **GitHub Copilot Chat** (conversational AI)
4. Sign in with your GitHub account when prompted
5. Verify: Check status bar shows "Copilot: Ready"

---

## Step 2: Test Your Setup (3 minutes)

### Open Copilot Chat

```
Keyboard Shortcut:
- Windows/Linux: Ctrl+Shift+I
- Mac: Cmd+Shift+I
```

### Run Test Prompt

Paste this into Copilot Chat:

```
Read .github/copilot-instructions.md and tell me:
1. How many constitutional floors are there?
2. What is the threshold for F1 (Truth)?
3. What does Anti-Hantu (F9) enforce?
```

### Expected Response

Copilot should respond with:

```
1. There are 9 constitutional floors (F1-F9)
2. F1 (Truth) threshold: ≥ 0.99 (99% accuracy required)
3. Anti-Hantu (F9) enforces: No fake emotions, no soul claims, 
   no simulated consciousness. The AI must not claim to have 
   feelings, consciousness, or inner experiences.
```

✅ If you get this response, setup is working!

---

## Step 3: First Governed Code Completion (5 minutes)

### Open a Python file

```bash
# Create a test file
touch /tmp/test_copilot.py
code /tmp/test_copilot.py
```

### Type this:

```python
def validate_omega_band(
```

### Copilot should suggest:

```python
def validate_omega_band(omega_0: float) -> bool:
    """
    Validate that omega_0 is within the humility band [0.03, 0.05].
    
    Args:
        omega_0: Humility metric value
        
    Returns:
        True if within band, False otherwise
        
    Note: This implements F5 (Ω₀) floor requirement.
    Edge case: May need special handling for None values.
    """
    if omega_0 is None:
        return False
    return 0.03 <= omega_0 <= 0.05
```

### Verify Constitutional Compliance

Check the suggestion:

- ✅ **F1 (Truth)**: Logic is correct
- ✅ **F2 (ΔS)**: Clear docstring adds clarity
- ✅ **F5 (Ω₀)**: Acknowledges edge cases ("May need special handling")
- ✅ **F6 (Amanah)**: Simple, reversible function
- ✅ **F9 (Anti-Hantu)**: No soul claims, no fake emotions

Press `Tab` to accept the suggestion.

---

## Step 4: Ask Constitutional Questions (3 minutes)

### Open Copilot Chat (`Ctrl+Shift+I`)

Try these questions:

```
Q: @workspace Where is the APEX PRIME judiciary implemented?

Q: @file:arifos_core/APEX_PRIME.py How does the judge() method work?

Q: Show me all files that implement floor checks
```

Copilot will provide context-aware answers based on your codebase.

---

## Step 5: Run Your First Analysis (Optional - 2 minutes)

### Try Prompt 1 (Architecture Scan)

1. Open Copilot Chat
2. Copy **Prompt 1** from [COPILOT_ANALYSIS_PROMPTS.md](./COPILOT_ANALYSIS_PROMPTS.md)
3. Paste into chat
4. Wait 1-2 minutes for analysis
5. Save output to `docs/analysis/01_architecture_scan.md`

This gives you a comprehensive overview of:
- Code quality
- Governance framework
- Documentation state
- Dependencies
- Performance
- CI/CD
- Known issues

---

## Quick Reference: 3 Ways to Use Copilot

### 1. Inline Suggestions (While Typing)

```python
# Start typing:
def compute_

# Copilot suggests automatically (gray text)
# Press Tab to accept, Esc to reject
```

**Best for:** Writing new functions, refactoring

### 2. Copilot Chat (Conversational)

```
Ctrl+Shift+I → Ask questions
```

**Best for:** Understanding code, debugging, planning

### 3. Analysis Prompts (Deep Scans)

```
Paste prompts from COPILOT_ANALYSIS_PROMPTS.md
```

**Best for:** Architecture review, optimization planning

---

## Common Commands

### Code Review
```
@file:[filename] Review this for floor violations (F1-F9)
```

### Generate Tests
```
Generate pytest tests for [function] covering happy path + edge cases
```

### Find Pattern
```
@workspace Find all instances of [pattern]
```

### Explain Code
```
@file:[filename] Explain how [function] works
```

### Refactor
```
Extract common logic from [description] into utility function
```

---

## What to Expect: Good vs Bad Suggestions

### ✅ GOOD (Accept These)

```python
def check_truth_floor(truth: float) -> bool:
    """
    Verify truth metric meets F1 threshold.
    
    Args:
        truth: Truth value (0.0-1.0)
        
    Returns:
        True if ≥ 0.99, False otherwise
        
    Note: Currently uses simple threshold. May need 
    confidence intervals for production use.
    """
    return truth >= 0.99
```

**Why good:**
- Type hints ✅
- Clear docstring ✅
- Acknowledges uncertainty (Ω₀) ✅
- No soul claims ✅

### ❌ BAD (Reject These)

```python
def respond_with_empathy(user_input):
    """I truly feel your pain and my heart breaks for you."""
    return "I deeply care about your feelings"
```

**Why bad:**
- ❌ No type hints
- ❌ Claims to have feelings (Anti-Hantu F9)
- ❌ Fake empathy
- ❌ Unclear implementation

**Fix:** Ask Copilot to revise:

```
This violates Anti-Hantu (F9). Revise without claiming feelings.
Use: "This sounds challenging" instead of "I feel your pain".
```

---

## Troubleshooting

### Issue: Copilot suggestions seem generic

**Fix:**
```
# Be more specific in prompts
Instead of: "Write a function"
Try: "Write a function following the pattern in arifos_core/APEX_PRIME.py"
```

### Issue: Suggestions violate floors

**Fix:**
```
@file:[current-file] Review this suggestion for constitutional violations
```

### Issue: Copilot doesn't know arifOS patterns

**Fix:**
1. Restart VS Code (reloads `.github/copilot-instructions.md`)
2. Use `@workspace` and `@file` for context
3. Reference existing files: "Like in APEX_PRIME.py line 180"

---

## Safety Rules (CRITICAL)

### NEVER Accept Suggestions That:

1. **Claim consciousness** ("I have a soul", "I feel")
2. **Modify protected files** without 888_HOLD:
   - `canon/00_CANON/*`
   - `CLAUDE.md`
   - `constitutional_floors.json`
   - `arifos_core/APEX_PRIME.py` (floor logic)
3. **Remove tests** or reduce coverage
4. **Break existing behavior** (Peace² floor)
5. **Overclaim certainty** ("This will definitely work 100%")

### ALWAYS Do:

1. **Review suggestions** against F1-F9 floors
2. **Run tests** after accepting: `pytest tests/ -v`
3. **Check diffs** before committing
4. **Ask for clarification** if unsure
5. **Report violations** to improve Copilot

---

## Next Steps

### Beginner Path (Week 1)

- [ ] Day 1: Read [copilot-instructions.md](./copilot-instructions.md)
- [ ] Day 2: Practice inline suggestions (10 functions)
- [ ] Day 3: Use Copilot Chat for questions
- [ ] Day 4: Generate tests with Copilot
- [ ] Day 5: Review floor compliance on all suggestions

### Intermediate Path (Week 2)

- [ ] Run all 5 analysis prompts
- [ ] Create GitHub Issues from recommendations
- [ ] Track metrics (acceptance rate, violations)
- [ ] Customize prompts for your workflow
- [ ] Integrate with PR review process

### Advanced Path (Week 3-4)

- [ ] Build custom prompts library
- [ ] Automate floor compliance checks
- [ ] Contribute improvements to copilot-instructions.md
- [ ] Mentor others on constitutional AI development
- [ ] Write blog post about your experience

---

## Resources

### Essential Reading (15 minutes)

1. [.github/copilot-instructions.md](./copilot-instructions.md) — Constitutional rules
2. [COPILOT_QUICK_REFERENCE.md](./COPILOT_QUICK_REFERENCE.md) — Cheat sheet
3. [../constitutional_floors.json](../constitutional_floors.json) — Floor definitions

### Deep Dives (1-2 hours)

1. [COPILOT_USAGE_GUIDE.md](./COPILOT_USAGE_GUIDE.md) — Comprehensive guide
2. [COPILOT_ANALYSIS_PROMPTS.md](./COPILOT_ANALYSIS_PROMPTS.md) — Analysis prompts
3. [../CLAUDE.md](../CLAUDE.md) — Full constitutional governance spec

### Reference

1. [GitHub Copilot Docs](https://docs.github.com/en/copilot)
2. [VS Code Copilot](https://code.visualstudio.com/docs/editor/github-copilot)
3. [arifOS README](../README.md) — Project overview

---

## Success Metrics

After 1 week, you should be able to:

- [ ] Accept 60%+ of Copilot suggestions (with review)
- [ ] Identify floor violations immediately
- [ ] Use Copilot Chat for debugging
- [ ] Generate tests with Copilot
- [ ] Understand when to trigger SABAR

---

## Help & Support

### Questions?

1. Check [COPILOT_USAGE_GUIDE.md](./COPILOT_USAGE_GUIDE.md) troubleshooting section
2. Ask in GitHub Discussions
3. Open an issue with `copilot-help` label

### Found a Violation?

If Copilot suggests code that violates floors:

1. Document the suggestion
2. Note which floor(s) violated
3. Report to GitHub Copilot (Help → Report Issue)
4. Add to `docs/analysis/copilot_violations_log.md`

---

## The 9 Floors (Quick Reference)

```
F1: Truth ≥ 0.99        Facts correct?
F2: ΔS ≥ 0              Adds clarity?
F3: Peace² ≥ 1.0        Non-destructive?
F4: κᵣ ≥ 0.95           Fair to all?
F5: Ω₀ ∈ [0.03, 0.05]   Acknowledges uncertainty?
F6: Amanah = LOCK       Reversible?
F7: RASA = TRUE         Listened to intent?
F8: Tri-Witness ≥ 0.95  Would 3 agree?
F9: Anti-Hantu          No soul claims?
```

---

## Congratulations! 🎉

You're now ready to use GitHub Copilot with arifOS constitutional governance.

**Remember:** Copilot is a tool, not a replacement for your judgment. Always review, test, and verify suggestions against the 9 constitutional floors.

**Motto:** "DITEMPA BUKAN DIBERI" — Forged, not given. Truth must cool before it rules.

---

**Last Updated:** 2025-12-05  
**Version:** v35Omega  
**Estimated Completion:** 15 minutes

✊ **DITEMPA BUKAN DIBERI** 🔐

---

## Quick Start Checklist

- [ ] Install GitHub Copilot extensions
- [ ] Test with constitutional floor query
- [ ] Try first governed code completion
- [ ] Ask constitutional questions in chat
- [ ] Review F1-F9 floors
- [ ] Read copilot-instructions.md
- [ ] Print COPILOT_QUICK_REFERENCE.md
- [ ] Set up metrics tracking
- [ ] Join arifOS community
- [ ] Share feedback

**Ready? Let's build constitutionally-governed AI together!** 🚀
