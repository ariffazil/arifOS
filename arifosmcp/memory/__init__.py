"""
arifosmcp/memory — Multi-agent shared memory subsystem.

Packages:
    shared_memory_mcp   Redis-backed hot scratchpad (get/set/list/clear/expire)

The vector memory layer (vector_query, vector_store, vector_forget, generate,
query) lives in arifosmcp.runtime.tools_internal.engineering_memory_dispatch_impl
via the constitutional Qdrant/LanceDB hybrid backend.

Stage: 555_MEMORY | Trinity: OMEGA Ω | Floors: F1, F10, F13
"""
