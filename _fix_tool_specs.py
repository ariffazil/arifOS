with open('arifosmcp/runtime/tool_specs.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_block = '''    # -------------------------------------------------------------------------
    # 15. arifos.probe -- System Health Probe
    # -------------------------------------------------------------------------
    ToolSpec(
        name="arifos_probe",
        stage="111",
        purpose="Probe system status or component health",
        layer="MACHINE",
        description="Probe system status or component health (system, memory, vault, etc.).",
        trinity="Δ",
        floors=("F4", "F12"),
        input_schema={
            "type": "object",
            "properties": {
                "target": {"type": "string", "default": "system", "description": "Component to probe"},
                "probe_type": {"type": "string", "enum": ["status", "health", "metrics"], "default": "status"},
                "timeout_ms": {"type": "integer", "default": 5000},
            },
        },
        default_tier="low",
        read_only_hint=True,
        destructive_hint=False,
        open_world_hint=False,
        idempotent_hint=True,
    ),
    # -------------------------------------------------------------------------
    # 16. arifos.diag_substrate -- Substrate Protocol Conformance
    # -------------------------------------------------------------------------
    ToolSpec(
        name="arifos_diag_substrate",
        stage="911",
        purpose="Run substrate protocol conformance check",
        layer="EXECUTION",
        description="Maintainer: Run substrate protocol conformance check.",
        trinity="Ψ",
        floors=("F11",),
        input_schema={
            "type": "object",
            "properties": {
                "session_id": {"type": "string"},
            },
        },
        default_tier="low",
        read_only_hint=True,
        destructive_hint=False,
        open_world_hint=False,
        idempotent_hint=True,
    ),
    # -------------------------------------------------------------------------
    # 17. arifos.git_commit -- Governed Repository Mutation (Substrate)
    # -------------------------------------------------------------------------
'''

new_lines = lines[:529] + [new_block] + lines[592:]

with open('arifosmcp/runtime/tool_specs.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('Replaced lines 530-592')
