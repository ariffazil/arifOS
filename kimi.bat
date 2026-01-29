@echo off
if exist .kimi\mcp.json (
    python -m uv tool run --from kimi-cli kimi --mcp-config-file .kimi\mcp.json %*
) else (
    python -m uv tool run --from kimi-cli kimi %*
)
