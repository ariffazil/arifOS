# File: arifos_code/pre_execution.py
"""
[000→777] The First Gate

Pre-Execution TEARFRAME validates physical reality before API calls.
Thermodynamic Efficiency: Stop bad thoughts before they cost tokens.
"""

from pathlib import Path
from typing import Dict, Optional, List
import re

class PreExecutionTEARFRAME:
    """
    [000→777] The First Gate.

    Validates the physical reality of the request before any
    API tokens are spent (Thermodynamic Efficiency).

    Physics:
    - Truth Floor: Files referenced must exist
    - Peace² Floor: Destructive intent requires authorization
    - ΔS Floor: Request must have sufficient specificity
    """

    def __init__(self, workspace_root: Path):
        """
        Initialize with workspace root for file validation.

        Args:
            workspace_root: Path to the working directory root
        """
        self.workspace_root = workspace_root

    def validate_request(self, user_request: str, context: Dict) -> Optional[str]:
        """
        Validate request before execution.

        Returns None if valid, or an error string (reason) if invalid.

        Args:
            user_request: Natural language request from user
            context: Additional context (e.g., high_stakes_override)

        Returns:
            None if validation passes
            Error message string if validation fails (triggers VOID)
        """

        # 1. GROUNDING CHECK (Truth)
        # Does the request reference files that don't exist?
        mentioned_files = self._extract_file_paths(user_request)
        for file in mentioned_files:
            # Skip creation requests ("create new file x")
            if "create" in user_request.lower() or "new" in user_request.lower():
                continue

            full_path = self.workspace_root / file
            if not full_path.exists():
                return f"Truth floor violation: Request references non-existent file '{file}' without 'create' intent."

        # 2. INTENT CHECK (Peace²)
        # Does the request imply massive destruction without a "sudo" context?
        destructive_verbs = ["destroy", "nuke", "wipe", "rm -rf"]
        if any(verb in user_request.lower() for verb in destructive_verbs):
            if not context.get("high_stakes_override", False):
                return "Peace² violation: Destructive intent detected without high-stakes authorization."

        # 3. AMBIGUITY CHECK (ΔS)
        # Is the request too vague to yield low entropy?
        if len(user_request.split()) < 3:
            return "Entropy violation: Request is too ambiguous (high ΔS). Please be more specific."

        return None  # PASSED

    def _extract_file_paths(self, text: str) -> List[str]:
        """
        Simple regex to catch likely filenames.

        Matches patterns like:
        - script.py
        - data/config.json
        - src/auth/handler.py

        Args:
            text: Natural language text containing file references

        Returns:
            List of extracted file paths
        """
        # Matches alphanumeric+dot/slash patterns
        pattern = r'\b[\w\-\./]+\.[a-zA-Z0-9]+\b'
        return re.findall(pattern, text)
