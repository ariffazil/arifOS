$mcp_args = @()
if (Test-Path ".kimi\mcp.json") {
    $mcp_args = @("--mcp-config-file", ".kimi\mcp.json")
}
python -m uv tool run --from kimi-cli kimi @mcp_args @args
