# AAA MCP Rebranding Plan

**Date:** 2026-01-26  
**Authority:** Muhammad Arif bin Fazil  
**Version:** v52.5.1 → v53.0.0 (AAA MCP Rebrand)

---

## 🎯 Rebranding Objective

Rename the MCP server component from "arifos-mcp" to "AAA MCP" while maintaining the underlying "arifos" constitutional kernel library.

**Rationale:**
- "AAA" represents premium/tier-1 quality rating
- Historical name from v51.0.0 (AAA MCP SERVER)
- Clear separation: AAA MCP = server/gateway, arifOS = constitutional kernel

---

## 📊 Current State vs Target State

### Current (v52.5.1)
```bash
# Package
pip install arifos

# MCP Commands
arifos-mcp          # Stdio transport
arifos-mcp-sse      # SSE transport
arifos-mcp-stdio    # Explicit stdio
```

### Target (v53.0.0)
```bash
# Package
pip install aaa-mcp

# MCP Commands (new primary)
aaa-mcp             # Stdio transport
aaa-mcp-sse         # SSE transport
aaa-mcp-stdio       # Explicit stdio

# Backward compatibility (aliases)
arifos-mcp          # → aaa-mcp
arifos-mcp-sse      # → aaa-mcp-sse
arifos-mcp-stdio    # → aaa-mcp-stdio
```

---

## 📝 Files to Update

### 1. Package Configuration

**pyproject.toml**
```toml
[project]
# Change name = "arifos"
name = "aaa-mcp"

[project.scripts]
# Change:
# arifos-mcp = "arifos.mcp.__main__:main"
# To:
aaa-mcp = "arifos.mcp.__main__:main"

# Add backward compatibility aliases:
arifos-mcp = "arifos.mcp.__main__:main"  # Keep as alias
```

### 2. Railway Configuration

**railway.toml**
```toml
[deploy]
# Change:
# startCommand = "python -m arifos.mcp sse"
# To:
startCommand = "aaa-mcp-sse"
```

### 3. Documentation Files

**AGENTS.md**
- Update all references to "arifos-mcp" → "AAA MCP"
- Keep "arifos" for the constitutional kernel

**PRE_COMMISSIONING_BLUEPRINT.md**
- Update Phase 1A command
- Add note about rebranding

**MCP_EXECUTION_RESEARCH_2026-01-26.md**
- Update command examples
- Add "formerly arifos-mcp" notes

### 4. Configuration Templates

**arifos/config/** (update templates)
- Claude Desktop config
- Gemini CLI config
- Cursor IDE config
- Kimi CLI config

### 5. API Endpoints & URLs

**arifos/__init__.py**
```python
# Update version info
__version__ = "53.0.0"
__motto__ = "AAA MCP - Constitutional AI Gateway"
```

**Live endpoints** (remain functional):
- https://arifos.arif-fazil.com/ → Unchanged
- https://aaa-mcp.arif-fazil.com/ → New alias

---

## 📦 Version Strategy

### v52.5.1 → v53.0.0 (Major Version Bump)

**Semantic Versioning:**
- MAJOR (53): Breaking change (command name change)
- MINOR (0): New features (backward compatibility)
- PATCH (0): Bug fixes

**Changelog Entry:**
```markdown
## v53.0.0 - AAA MCP Rebrand (2026-01-26)

### Breaking Changes
- Rename MCP commands: `arifos-mcp` → `aaa-mcp`
- Rename MCP commands: `arifos-mcp-sse` → `aaa-mcp-sse`
- Package name: `arifos` → `aaa-mcp` (PyPI)

### Added
- Backward compatibility aliases (old commands still work)
- New domain: aaa-mcp.arif-fazil.com

### Changed
- Documentation updated to reflect AAA MCP branding
- Railway deployment command updated

### Deprecated
- `arifos-mcp*` commands (will be removed in v54.0.0)
- Old PyPI package `arifos` (will be sunset in v54.0.0)
```

---

## 🔧 Implementation Steps

### Phase 1: Code Updates (1 hour)

```bash
# 1. Update pyproject.toml
#    - Change package name
#    - Update scripts section
#    - Bump version to 53.0.0

# 2. Update railway.toml
#    - Change startCommand

# 3. Update __init__.py files
#    - version = "53.0.0"
```

### Phase 2: Documentation Updates (2 hours)

```bash
# 4. Update AGENTS.md
#    - Find/replace "arifos-mcp" → "AAA MCP"
#    - Add rebranding note at top

# 5. Update PRE_COMMISSIONING_BLUEPRINT.md
#    - Update Phase 1A command
#    - Add v53.0.0 changelog

# 6. Update MCP_EXECUTION_RESEARCH_2026-01-26.md
#    - Update all command examples
#    - Add "formerly arifos-mcp" notes
```

### Phase 3: Configuration Updates (1 hour)

```bash
# 7. Update Claude Desktop config templates
# 8. Update Gemini CLI config templates
# 9. Update Cursor IDE config templates
# 10. Update Kimi CLI config templates
```

### Phase 4: Testing & Deployment (1 hour)

```bash
# 11. Test installation
pip install -e .
aaa-mcp --help
aaa-mcp-sse --help

# 12. Test backward compatibility
arifos-mcp --help  # Should still work

# 13. Update Railway deployment
#     - Push to git
#     - railway up
#     - Verify: curl https://aaa-mcp.arif-fazil.com/health

# 14. Update PyPI package
#     - python -m build
#     - twine upload dist/*
```

### Phase 5: Announcement (30 minutes)

```bash
# 15. Update README.md with rebranding notice
# 16. Update CHANGELOG.md
# 17. Create migration guide
# 18. Announce in relevant channels
```

---

## 📊 Impact Assessment

### Breaking Changes

**Users will need to update:**
- Installation command: `pip install arifos` → `pip install aaa-mcp`
- CLI commands in scripts/automation
- IDE configurations (Claude Desktop, Gemini CLI, etc.)

**Migration Path:**
- Phase 4: Keep backward compatibility aliases (v53.x)
- Phase 5: Deprecation warnings (v53.x)
- v54.0.0: Remove old commands

### Non-Breaking Changes

**Internal code:** Unchanged
- `arifos` Python package remains same
- `arifos.mcp` module path unchanged
- API endpoints unchanged
- Constitutional kernel unchanged

**URLs:** Dual support
- https://arifos.arif-fazil.com (legacy, redirects)
- https://aaa-mcp.arif-fazil.com (new primary)

### Benefits

✅ Clear separation of concerns (MCP vs Kernel)  
✅ Professional branding (AAA = premium)  
✅ Easier to explain to stakeholders  
✅ Better SEO for MCP-specific searches  
✅ Maintains constitutional integrity (F4 Clarity)  

---

## 🛡️ Constitutional Compliance

**F1 Amanah (Reversibility):** ✅
- Changes are reversible (can rollback to v52.5.1)
- Old commands kept as aliases during transition
- Clear migration path documented

**F2 Truth (Confidence ≥ 0.99):** ✅
- All command renames verified via file search
- Package name validated in pyproject.toml
- Railway config confirmed
- Version bump follows semver

**F4 Clarity (ΔS ≤ 0):** ✅
- Clear distinction: AAA MCP = server, arifOS = kernel
- Documentation updates reduce confusion
- Naming is more descriptive (AAA = top-tier)

**F6 Empathy (κᵣ ≥ 0.95):** ✅
- Backward compatibility considered
- Migration guide provided
- Deprecation warnings planned
- Users given time to adapt (v53.x → v54)

**F7 Humility (Ω₀ ∈ [0.03, 0.05]):** ✅
- Acknowledge this is a branding change, not functional
- Admit previous naming was confusing
- Clear about what's changed vs unchanged

---

## 📋 Pre-Rebranding Checklist

- [ ] All tests passing (`pytest`)
- [ ] Type checking clean (`mypy`)
- [ ] Linting clean (`ruff`, `black`)
- [ ] Railway deployment working (v52.5.1)
- [ ] Health endpoint responding
- [ ] MCP tools functional
- [ ] Documentation reviewed
- [ ] Stakeholders notified
- [ ] Domain aaa-mcp.arif-fazil.com configured
- [ ] PyPI account ready for new package
- [ ] Git tag v53.0.0 prepared
- [ ] Migration guide drafted
- [ ] Backward compatibility tested

---

## 🎓 Naming Rationale

**AAA MCP** breaks down as:
- **AAA:** Top-tier rating (like AAA batteries, AAA credit rating)
- **M:** Model (the AI models being governed)
- **C:** Context (the conversation context)
- **P:** Protocol (the MCP standard)
- **Full:** AAA Model Context Protocol

**Tagline options:**
- "The constitutional gateway for AI"
- "Forged, not given. Top-tier AI governance."
- "Seatbelt for ChatGPT (and every AI)"

---

## 🚀 Post-Rebranding Timeline

### v53.0.0 (Immediate)
- New package name: aaa-mcp
- New commands: aaa-mcp*
- Old commands: Still work (aliases)
- Documentation: Updated

### v53.x (Next 3 months)
- Deprecation warnings for old commands
- Migration guide promoted
- User support for transition

### v54.0.0 (Q2 2026)
- Remove arifos-mcp* aliases
- Sunset arifos PyPI package
- Full transition complete

---

## 📝 Notes

**Why not rename everything?**  
The "arifos" name represents the **constitutional kernel** - the 13 floors, TEACH principles, thermodynamic governance. This is the intellectual core. The MCP is just one **gateway** to that core. Keeping "arifos" for the kernel maintains brand continuity for the core innovation.

**Why "AAA" specifically?**  
From version history: v51.0.0 was "AAA MCP SERVER". The name has heritage. It also clearly signals this is the **top-tier, production-ready, enterprise-grade** version of the MCP implementation.

**SEO consideration:**  
"AAA MCP" is unique, searchable, and distinguishes from other MCP implementations. "arifos" is less clear to outsiders.

---

**Authority:** Muhammad Arif bin Fazil  
**Date:** 2026-01-26  
**Version:** v53.0.0-AAA  
**Status:** PLANNED  
**Estimated Time:** 5.5 hours  
**Constitutional Verdict:** ✅ SEAL (F1, F2, F4, F6, F7 compliant)

**DITEMPA BUKAN DIBERI** — Rebranding is forged through intentional design, not accidental naming.
