#!/usr/bin/env python3
"""
arifOS MCP-Wiki Sync Verifier
Ensures the canonical MCP tool surface and Ω-Wiki stay aligned.
"""

import sys
from pathlib import Path

# Add project root to path to import tool specs
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from arifosmcp.runtime.tool_specs import TOOLS
except ImportError as e:
    print(f"FAILED: Could not import tool specs: {e}")
    sys.exit(1)

def verify_sync():
    wiki_pages_dir = Path("wiki/pages")
    mcp_names = {t.name for t in TOOLS}
    
    # Core wiki pages to check for tool names
    wiki_files = [
        wiki_pages_dir / "Trinity_Architecture.md",
        wiki_pages_dir / "Metabolic_Loop.md",
        wiki_pages_dir / "MCP_Tools.md"
    ]
    
    wiki_content = ""
    for wf in wiki_files:
        if wf.exists():
            wiki_content += "\n" + wf.read_text()
    
    missing_from_wiki = []
    for name in mcp_names:
        if name not in wiki_content:
            missing_from_wiki.append(name)
            
    if missing_from_wiki:
        print("❌ SYNC VIOLATION: The following MCP tools are missing from Ω-Wiki synthesis:")
        for tool in missing_from_wiki:
            print(f"  - {tool}")
        return False
    
    print("✅ SYNC VERIFIED: All canonical MCP tools are documented in Ω-Wiki.")
    return True

if __name__ == "__main__":
    if not verify_sync():
        sys.exit(1)
    sys.exit(0)
