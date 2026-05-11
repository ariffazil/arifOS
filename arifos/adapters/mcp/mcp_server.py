import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_REMOVED_PATHS: list[tuple[int, str]] = []
for _index in range(len(sys.path) - 1, -1, -1):
    _entry = sys.path[_index]
    try:
        if Path(_entry).resolve() == _REPO_ROOT:
            _REMOVED_PATHS.append((_index, _entry))
            sys.path.pop(_index)
    except OSError:
        continue

from fastmcp import FastMCP

for _index, _entry in reversed(_REMOVED_PATHS):
    sys.path.insert(_index, _entry)

from arifos.adapters.mcp.registry import register_all

mcp = FastMCP(
    "arifosmcp",
    instructions=(
        "Constitutional MCP server for arifOS. "
        "Expose 13 tools, 11 metabolic prompts, and 3 organ resources."
    ),
)

register_all(mcp)

if __name__ == "__main__":
    mcp.run()
