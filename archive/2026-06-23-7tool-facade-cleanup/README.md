# 2026-06-23 7-Tool Facade Cleanup Archive

This directory contains files that referenced the pre-freeze tool surface (13/15/16 tools, old names like arif_forge, arif_compose, arif_memory_recall, arif_ops_measure, arif_kernel_intercept as public, etc.).

**New reality**:
- Public: exactly 7 verbs (arif_init, arif_observe, arif_think, arif_route, arif_judge, arif_act, arif_seal)
- Everything else: internal_only or demoted
- See: arifosmcp/runtime/public_surface.py (CANONICAL_7)
- See: arifosmcp/constitutional_map.py (_PUBLIC_7 + auto-demote logic)
- Manifests updated to reflect 7

Files moved here for historical reference only. Do not rely on them for current implementation.

Generated during post-freeze audit and cleanup.
