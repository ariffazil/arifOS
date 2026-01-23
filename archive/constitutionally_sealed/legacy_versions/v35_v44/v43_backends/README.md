# v43 Backend Adapters Archive

**Archived:** 2026-01-08
**Reason:** Superseded by v45/v46 adapter architecture
**Phase:** Post-Trinity AAA Orthogonal Architecture refactor

---

## Archived Files

### llm_backends_v43.py (1,104 lines)
**Original Location:** `arifos_core/integration/adapters/llm_backends_v43.py`

**Why Archived:**
- Referenced non-existent spec file: `spec/v43/interface_and_authority.json` (deleted in v44)
- Used v43 floor validation logic (pre-Trinity architecture)
- Superseded by current adapter implementations in `arifos_core/adapters/`

**Functionality:**
- Unified LLM backend factory for OpenAI, Anthropic, Google Gemini, SEA-LION, Llama, Perplexity
- Spec-driven validation against `llm_contract` requirements
- Floor constraint enforcement (F1-F9) at adapter level

**Replacement:**
- Current adapters use v45 constitutional floors specification
- Trinity AAA architecture (AGI, ASI, APEX) for floor enforcement
- Modern adapters in `arifos_core/adapters/llm_*.py`

### BACKENDS_v43_QUICK_START.md
**Original Location:** `arifos_core/integration/adapters/BACKENDS_v43_QUICK_START.md`

**Why Archived:**
- Documentation for v43 backend architecture
- References deleted v43 spec files
- No longer applicable to v45/v46 architecture

**Replacement:**
- Current documentation in main README.md
- Adapter usage documented in `docs/`

---

## Migration Path (if needed)

If v43 backend functionality is needed:

1. **For OpenAI/Anthropic/Google:**
   - Use adapters in `arifos_core/adapters/`
   - Reference v45 constitutional floors: `spec/v45/constitutional_floors.json`

2. **For Custom Backends:**
   - Follow Trinity AAA pattern
   - Implement adapter interface with AGI/ASI/APEX floor checks
   - Register with apex_prime.py for verdict authority

3. **For Legacy v43 Compatibility:**
   - Restore files from this archive
   - Update spec references from v43 to v45
   - Refactor floor logic to use Trinity kernels

---

## References

- **v43 Spec Migration:** See `archive/spec_history/v43/`
- **Trinity Architecture:** See `docs/ARCHITECTURE_AND_NAMING_v46.md`
- **Floor Evolution:** See `spec/v45/constitutional_floors.json`
- **Adapter Pattern:** See `arifos_core/adapters/README.md`

---

**Archive Status:** FROZEN (read-only, historical reference)
**Last Active Version:** v43.x (pre-TEARFRAME, pre-Trinity)
