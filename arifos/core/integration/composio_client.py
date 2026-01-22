import os
from typing import Any, Dict, List, Optional

from composio_core import App, Composio


class ComposioClient:
    def __init__(self):
        self.api_key = os.getenv("COMPOSIO_API_KEY")
        # In a real scenario, we initialize the SDK here
        # self.composio = Composio(api_key=self.api_key)
        pass

    async def list_tools(self, filter_apps: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List tools available via Composio.
        Currently returns detailed mocked schema matching the allowlist for development.
        """
        # TODO: Replace with real SDK call:
        # apps = self.composio.apps.get()

        # Mocking return based on filter for now to ensure server runs without API key
        mock_tools = {
            "google_search": {
                "name": "google_search",
                "description": "Search the web using Google",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"}
                    },
                    "required": ["query"]
                }
            },
            "github_read_issue": {
                "name": "github_read_issue",
                "description": "Read comments and details of a GitHub issue",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "owner": {"type": "string"},
                        "repo": {"type": "string"},
                        "issue_number": {"type": "integer"}
                    },
                    "required": ["owner", "repo", "issue_number"]
                }
            }
        }

        results = []
        if filter_apps:
            for app_name in filter_apps:
                if app_name in mock_tools:
                    results.append(mock_tools[app_name])
        return results

    async def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        Execute a tool via Composio SDK.
        """
        # TODO: Real SDK execution
        # action = self.composio.get_action(tool_name)
        # response = action.execute(args)

        # Mock execution
        return f"[Composio Mock] Executed {tool_name} successfully with args: {args}"

# Singleton instance
composio_client = ComposioClient()
