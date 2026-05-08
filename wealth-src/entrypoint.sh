#!/bin/bash
cd /app
exec python -c "from internal.monolith import mcp; mcp.run(transport='streamable-http', show_banner=False)"
