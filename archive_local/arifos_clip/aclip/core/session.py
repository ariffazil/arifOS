import json
import os
from pathlib import Path

class Session:
    """Represents an A CLIP session, including all stage data."""
    def __init__(self, data=None):
        self.data = data or {}
        self.loaded_from_file = False

    @classmethod
    def load_or_init(cls):
        """Load an existing session from disk, or initialize a new one if none exists."""
        base = Path(".arifos_clip")
        base.mkdir(exist_ok=True)
        # Ensure subdirectories exist
        (base / "holds").mkdir(exist_ok=True)
        (base / "forge").mkdir(exist_ok=True)
        session_file = base / "session.json"
        if session_file.exists():
            # Load existing session
            with open(session_file, "r") as f:
                data = json.load(f)
            sess = cls(data)
            sess.loaded_from_file = True
        else:
            # Start a fresh session (data will be filled by 000 stage)
            sess = cls()
        return sess

    def save(self):
        """Save the session data to .arifos_clip/session.json."""
        base = Path(".arifos_clip")
        base.mkdir(exist_ok=True)
        session_file = base / "session.json"
        # Write JSON data (indent for readability)
        with open(session_file, "w") as f:
            json.dump(self.data, f, indent=2)

def get_cli_stage_file(filename):
    """
    Get the file path of a CLI stage module (e.g., '000_void.py'),
    regardless of numeric naming issues.
    """
    return Path(__file__).resolve().parent.parent / "cli" / filename
