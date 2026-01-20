"""
arifos/system/executor/sandbox.py

The Hand (Primitive).
Executes commands in an isolated Docker container.
"""

import logging
import subprocess
import uuid
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class ExecutionSandbox:
    """
    Runs code in a disposable Docker container.
    """
    def __init__(self, image: str = "python:3.10-slim"):
        self.image = image
        self.container_id: Optional[str] = None

    def start(self):
        """Start the sandbox container."""
        try:
            # Run detached, interactive, with TTY
            cmd = ["docker", "run", "-d", "-it", "--rm", self.image, "/bin/bash"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            self.container_id = result.stdout.strip()
            logger.info(f"Sandbox started: {self.container_id}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start sandbox: {e.stderr}")
            raise

    def stop(self):
        """Stop and remove the container."""
        if self.container_id:
            subprocess.run(["docker", "kill", self.container_id], check=False, stdout=subprocess.DEVNULL)
            self.container_id = None

    def run_command(self, command: str) -> Tuple[int, str, str]:
        """
        Run a command inside the container.
        Returns: (exit_code, stdout, stderr)
        """
        if not self.container_id:
            self.start()

        # Wrap command in bash -c to handle redirects/pipes
        docker_cmd = ["docker", "exec", self.container_id, "/bin/bash", "-c", command]

        try:
            result = subprocess.run(docker_cmd, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return -1, "", str(e)

    def write_file(self, path: str, content: str):
        """Write content to a file inside the container."""
        if not self.container_id:
            self.start()

        # Write to temp file on host then cp? Or echo? Echo is safer for simple text.
        # For complex content, cleaner to use `docker cp` but requires a generic temp file pattern.
        # Using a simple python script execution inside is robust.

        escaped_content = content.replace('"', '\\"').replace("'", "\\'") # Naive escaping
        # Better: use python inside docker to write
        script = f"with open('{path}', 'w') as f: f.write(r'''{content}''')"
        # Execute this python snippet
        self.run_command(f"python3 -c \"{script}\"")

    def read_file(self, path: str) -> str:
        """Read file content from the container."""
        if not self.container_id:
             raise RuntimeError("Sandbox not started")

        code, out, err = self.run_command(f"cat {path}")
        if code != 0:
            raise FileNotFoundError(f"Could not read {path}: {err}")
        return out
