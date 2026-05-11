with open('arifosmcp/runtime/resources.py', encoding='utf-8') as f:
    content = f.read()

old = """def register_resources(mcp: FastMCP) -> None:
    """Alias for register_v2_resources — backward compat."""\n    register_v2_resources(mcp)"""

new = """def register_resources(mcp: FastMCP) -> list[str]:
    """Alias for register_v2_resources — backward compat."""\n    return register_v2_resources(mcp)"""

if old in content:
    content = content.replace(old, new)
    with open('arifosmcp/runtime/resources.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed register_resources return type')
else:
    print('Old string not found')
    # Try with plain ascii
    old2 = 'def register_resources(mcp: FastMCP) -> None:\n'
    if old2 in content:
        content = content.replace(
            'def register_resources(mcp: FastMCP) -> None:\n    """Alias for register_v2_resources',
            'def register_resources(mcp: FastMCP) -> list[str]:\n    """Alias for register_v2_resources'
        )
        content = content.replace(
            '    register_v2_resources(mcp)\n\n\ndef apex_tools_html_rows',
            '    return register_v2_resources(mcp)\n\n\ndef apex_tools_html_rows'
        )
        with open('arifosmcp/runtime/resources.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Fixed register_resources return type (alternative)')
    else:
        print('Could not find target string')
