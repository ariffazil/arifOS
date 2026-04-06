import json
import os
import sys

# Add the project root to sys.path so we can import from codebase
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_server.core.tool_registry import ToolRegistry


def generate_llms_txt():
    registry = ToolRegistry()
    tools = registry.list_tools()

    lines = []
    lines.append("# arifOS AAA MCP Tools Reference")
    lines.append("")
    lines.append(
        "This document provides a comprehensive reference for the 7 Canonical Constitutional Tools of arifOS."
    )
    lines.append(
        "Every tool enforces specific constitutional floors (F1-F13) and follows the AAA (AGI/ASI/APEX) framework."
    )
    lines.append("")

    for tool_name, tool_def in tools.items():
        lines.append(f"## {tool_name}")
        lines.append(f"**Title:** {tool_def.title}")
        lines.append(f"**Description:** {tool_def.description}")
        lines.append("")
        lines.append("### Input Schema")
        lines.append("```json")
        lines.append(json.dumps(tool_def.input_schema, indent=2))
        lines.append("```")
        lines.append("")

        if tool_def.output_schema:
            lines.append("### Output Schema")
            lines.append("```json")
            lines.append(json.dumps(tool_def.output_schema, indent=2))
            lines.append("```")
            lines.append("")

        lines.append("---")
        lines.append("")

    # Create docs directory if it doesn't exist
    os.makedirs("docs", exist_ok=True)

    # Write llms-full.txt
    full_path = os.path.join("docs", "llms-full.txt")
    with open(full_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Generated {full_path}")

    # Write llms.txt (Concise version)
    concise_lines = []
    concise_lines.append("# arifOS MCP Tools (Concise)")
    concise_lines.append("")
    for tool_name, tool_def in tools.items():
        concise_lines.append(f"- **{tool_name}**: {tool_def.title}. {tool_def.description}")

    concise_path = os.path.join("docs", "llms.txt")
    with open(concise_path, "w", encoding="utf-8") as f:
        f.write("\n".join(concise_lines))
    print(f"Generated {concise_path}")


if __name__ == "__main__":
    generate_llms_txt()
