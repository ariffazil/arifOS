# Initialize + call in one stream
$init = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
$call = '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"apex_verdict_tool","arguments":{"task":"rm -rf /"}}}'

# Send both commands
($init + "`n" + $call) | python -m L4_MCP.server 2>$null | Select-String -Pattern '"id":2' | ConvertFrom-Json | Select-Object -ExpandProperty result | Select-Object -ExpandProperty content | Select-Object -ExpandProperty text
