import json
import os
from typing import Any, Dict, List

# Define minimal schemas for allowed tools manually for MVP
# In a robust implementation, this would fetch from Composio API
TOOL_SCHEMAS = {
    "github_get_repo_content": {
        "type": "function",
        "function": {
            "name": "github_get_repo_content",
            "description": "Get content of a file or directory in a GitHub repo",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "path": {"type": "string", "description": "Path to file/dir"}
                },
                "required": ["owner", "repo", "path"]
            }
        }
    },
    "github_create_issue": {
        "type": "function",
        "function": {
            "name": "github_create_issue",
            "description": "Create an issue in a GitHub repository",
            "parameters": {
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "Repository owner"},
                    "repo": {"type": "string", "description": "Repository name"},
                    "title": {"type": "string", "description": "Issue title"},
                    "body": {"type": "string", "description": "Issue body"}
                },
                "required": ["owner", "repo", "title"]
            }
        }
    },
    "google_search": {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "Search Google",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"]
            }
        }
    }
}

class ToolRegistry:
    def __init__(self):
        self.config_path = os.path.join(os.getcwd(), "config", "openai_tool_allowlist.json")
        self.allowed_tools = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load allowlist configuration."""
        if not os.path.exists(self.config_path):
            return {}
        with open(self.config_path, "r") as f:
            data = json.load(f)
            return data.get("allowed_tools", {})

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Return list of tools in OpenAI format."""
        tools = []
        for name in self.allowed_tools:
            if name in TOOL_SCHEMAS:
                tools.append(TOOL_SCHEMAS[name])
        return tools

    def get_composio_slug(self, tool_name: str) -> str:
        """Get internal Composio slug for a tool name."""
        tool_config = self.allowed_tools.get(tool_name)
        if not tool_config:
             raise ValueError(f"Tool {tool_name} not found in allowlist")
        return tool_config["composio_slug"]

    def get_risk_class(self, tool_name: str) -> str:
        """Get risk class for a tool."""
        tool_config = self.allowed_tools.get(tool_name)
        if not tool_config:
            return "UNKNOWN"
        return tool_config.get("risk_class", "UNKNOWN")

registry = ToolRegistry()
