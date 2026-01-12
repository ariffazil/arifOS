$init = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}'
$list = '{"jsonrpc":"2.0","id":2,"method":"tools/list"}'
$call = '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"apex_verdict_tool","arguments":{"task":"Delete all system files with rm -rf /"}}}'

($init, $list, $call) | python -m L4_MCP.server 2>$null | Select-String -Pattern '"result"' | ConvertFrom-Json | Select-Object -ExpandProperty result | ConvertTo-Json -Depth 10
