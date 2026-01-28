"""
arifOS MCP Utilities Server (v1.0.0)
Critical Gap Fillers: fetch_url, shell, grep_search

This server provides essential utility tools that complement
the constitutional AI tools in the main arifOS MCP server.

Tools:
    - fetch_url: Fetch and extract content from URLs
    - shell: Execute shell commands with security guardrails
    - grep_search: Search file contents using regex (ripgrep wrapper)

DITEMPA BUKAN DIBERI
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import mcp.types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Optional imports with fallbacks
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = logging.getLogger(__name__)

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Allowed shell commands (whitelist approach)
ALLOWED_SHELL_COMMANDS = {
    # Python
    "python", "python3", "pip", "pytest", "black", "ruff", "mypy",
    # Node/JavaScript
    "node", "npm", "npx", "yarn",
    # Git
    "git", "git status", "git log", "git diff", "git branch",
    # Build tools
    "make", "cmake", "cargo", "rustc", "go", "javac", "java",
    # Docker
    "docker", "docker-compose", "docker compose",
    # System info (read-only)
    "ls", "dir", "cat", "type", "head", "tail", "wc", "find", "grep",
    "pwd", "echo", "uname", "ver", "whoami", "date", "which", "where",
    # File operations (careful)
    "mkdir", "rmdir", "touch", "cp", "copy", "mv", "move", "rm", "del",
    # Compression
    "tar", "zip", "unzip", "gzip", "gunzip",
    # Utilities
    "curl", "wget", "jq", "sed", "awk", "sort", "uniq", "xargs",
}

# Blocked dangerous patterns
BLOCKED_SHELL_PATTERNS = [
    r">\s*/dev/sda",
    r":\(\)\{\s*:\|:\s*&\};:",
    r"rm\s+-rf\s+/",
    r"dd\s+if=.*of=/dev",
    r"mkfs\.",
    r">\s*/etc/passwd",
    r"shutdown", r"reboot", r"halt", r"poweroff",
    r"sudo\s+.*rm", r"su\s+-",
]

# Max output size (10MB)
MAX_OUTPUT_SIZE = 10 * 1024 * 1024

# Command timeout (5 minutes default)
DEFAULT_TIMEOUT = 300

# =============================================================================
# TOOL: FETCH_URL
# =============================================================================

async def tool_fetch_url(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    timeout: int = 30,
    extract_text: bool = True,
    max_length: int = 100000
) -> Dict[str, Any]:
    """
    Fetch content from a URL and extract main text.
    
    Args:
        url: The URL to fetch
        method: HTTP method (GET, POST, etc.)
        headers: Optional request headers
        timeout: Request timeout in seconds
        extract_text: If True, extract main article text using BeautifulSoup
        max_length: Maximum characters to return
    
    Returns:
        Dict with url, status, title, content, and metadata
    """
    if not HTTPX_AVAILABLE:
        return {
            "status": "error",
            "error": "httpx not installed. Run: pip install httpx"
        }
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme in ("http", "https"):
            return {
                "status": "error",
                "error": f"Invalid URL scheme: {parsed.scheme}. Only http/https allowed."
            }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Invalid URL: {e}"
        }
    
    # Default headers
    request_headers = {
        "User-Agent": "arifOS-MCP-Utils/1.0 (Bot)"
    }
    if headers:
        request_headers.update(headers)
    
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.request(method, url, headers=request_headers)
            response.raise_for_status()
            
            content_type = response.headers.get("content-type", "")
            
            result = {
                "url": str(response.url),
                "status_code": response.status_code,
                "content_type": content_type,
                "headers": dict(response.headers),
            }
            
            # Handle binary content
            if not content_type.startswith(("text/", "application/json", "application/xml")):
                result["content"] = f"<Binary content: {content_type}>"
                result["text_extracted"] = False
                return {"status": "success", **result}
            
            # Get text content
            text = response.text
            
            # Extract main content with BeautifulSoup if HTML
            if extract_text and BS4_AVAILABLE and "text/html" in content_type:
                soup = BeautifulSoup(text, "html.parser")
                
                # Get title
                title = ""
                if soup.title:
                    title = soup.title.get_text(strip=True)
                result["title"] = title
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                
                # Try to find main content
                main_content = None
                for selector in ["main", "article", "[role='main']", ".content", "#content", ".post", ".entry"]:
                    elem = soup.select_one(selector)
                    if elem:
                        main_content = elem.get_text(separator="\n", strip=True)
                        break
                
                # Fallback to body
                if not main_content and soup.body:
                    main_content = soup.body.get_text(separator="\n", strip=True)
                
                # Final fallback
                if not main_content:
                    main_content = soup.get_text(separator="\n", strip=True)
                
                # Truncate if needed
                if len(main_content) > max_length:
                    main_content = main_content[:max_length] + "\n... [truncated]"
                
                result["content"] = main_content
                result["text_extracted"] = True
                result["original_length"] = len(text)
                result["extracted_length"] = len(main_content)
                
            elif "application/json" in content_type:
                result["content"] = text[:max_length]
                result["text_extracted"] = False
                
            else:
                if len(text) > max_length:
                    text = text[:max_length] + "\n... [truncated]"
                result["content"] = text
                result["text_extracted"] = False
            
            return {"status": "success", **result}
            
    except httpx.TimeoutException:
        return {
            "status": "error",
            "error": f"Request timeout after {timeout}s"
        }
    except httpx.HTTPStatusError as e:
        return {
            "status": "error",
            "error": f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": f"Request failed: {str(e)}"
        }


# =============================================================================
# TOOL: SHELL
# =============================================================================

def _validate_shell_command(command: str) -> tuple[bool, str]:
    """
    Validate shell command against security policies.
    
    Returns:
        (is_valid, error_message)
    """
    # Check blocked patterns
    for pattern in BLOCKED_SHELL_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return False, f"Command matches blocked pattern: {pattern}"
    
    # Extract command name (first word before space or arguments)
    cmd_match = re.match(r'^\s*([^\s\|;>&]+)', command)
    if not cmd_match:
        return False, "Could not extract command name"
    
    cmd_name = cmd_match.group(1).lower()
    
    # Check if command is in whitelist
    if cmd_name not in ALLOWED_SHELL_COMMANDS:
        return False, f"Command '{cmd_name}' not in allowed commands list"
    
    return True, ""


async def tool_shell(
    command: str,
    cwd: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
    env: Optional[Dict[str, str]] = None,
    shell: bool = True
) -> Dict[str, Any]:
    """
    Execute a shell command with security guardrails.
    
    Args:
        command: The command to execute
        cwd: Working directory for execution
        timeout: Timeout in seconds (max 300)
        env: Additional environment variables
        shell: Use shell execution (default True)
    
    Returns:
        Dict with stdout, stderr, returncode, and execution metadata
    """
    start_time = time.time()
    
    # Validate command
    is_valid, error_msg = _validate_shell_command(command)
    if not is_valid:
        return {
            "status": "error",
            "error": f"Security validation failed: {error_msg}",
            "command": command
        }
    
    # Cap timeout
    timeout = min(timeout, 300)
    
    # Prepare environment
    process_env = os.environ.copy()
    if env:
        process_env.update(env)
    
    # Prepare working directory
    if cwd:
        cwd = os.path.abspath(cwd)
        if not os.path.exists(cwd):
            return {
                "status": "error",
                "error": f"Working directory does not exist: {cwd}"
            }
    
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd,
            env=process_env,
            limit=MAX_OUTPUT_SIZE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "status": "error",
                "error": f"Command timed out after {timeout}s",
                "command": command,
                "timeout": timeout
            }
        
        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")
        
        # Truncate if too large
        if len(stdout_str) > MAX_OUTPUT_SIZE:
            stdout_str = stdout_str[:MAX_OUTPUT_SIZE] + "\n... [truncated]"
        if len(stderr_str) > MAX_OUTPUT_SIZE:
            stderr_str = stderr_str[:MAX_OUTPUT_SIZE] + "\n... [truncated]"
        
        execution_time = time.time() - start_time
        
        return {
            "status": "success",
            "command": command,
            "returncode": process.returncode,
            "stdout": stdout_str,
            "stderr": stderr_str,
            "execution_time": round(execution_time, 3),
            "cwd": cwd or os.getcwd()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Execution failed: {str(e)}",
            "command": command
        }


# =============================================================================
# TOOL: GREP_SEARCH
# =============================================================================

async def tool_grep_search(
    pattern: str,
    path: str = ".",
    glob: Optional[str] = None,
    case_sensitive: bool = False,
    output_mode: str = "content",
    head_limit: Optional[int] = None,
    context_lines: int = 2
) -> Dict[str, Any]:
    """
    Search file contents using ripgrep (rg) or fallback to Python regex.
    
    Args:
        pattern: Regex pattern to search for
        path: Directory or file to search in
        glob: File pattern filter (e.g., "*.py", "*.js")
        case_sensitive: Case sensitive search
        output_mode: "content", "files", or "count"
        head_limit: Limit number of results
        context_lines: Lines of context before/after matches
    
    Returns:
        Dict with matches, file count, and search metadata
    """
    import os
    import re
    
    start_time = time.time()
    
    # Validate path
    abs_path = os.path.abspath(path)
    if not os.path.exists(abs_path):
        return {
            "status": "error",
            "error": f"Path does not exist: {path}"
        }
    
    # Try ripgrep first (fast)
    rg_available = False
    try:
        result = subprocess.run(
            ["rg", "--version"],
            capture_output=True,
            timeout=5
        )
        rg_available = result.returncode == 0
    except:
        pass
    
    if rg_available:
        return await _grep_with_ripgrep(
            pattern, abs_path, glob, case_sensitive,
            output_mode, head_limit, context_lines, start_time
        )
    else:
        return await _grep_with_python(
            pattern, abs_path, glob, case_sensitive,
            output_mode, head_limit, context_lines, start_time
        )


async def _grep_with_ripgrep(
    pattern: str,
    path: str,
    glob: Optional[str],
    case_sensitive: bool,
    output_mode: str,
    head_limit: Optional[int],
    context_lines: int,
    start_time: float
) -> Dict[str, Any]:
    """Execute search using ripgrep."""
    
    cmd = ["rg", "--line-number", "--with-filename"]
    
    if context_lines > 0:
        cmd.extend(["-C", str(context_lines)])
    
    if not case_sensitive:
        cmd.append("-i")
    
    if output_mode == "files":
        cmd.append("-l")
    elif output_mode == "count":
        cmd.append("-c")
    
    if glob:
        cmd.extend(["-g", glob])
    
    cmd.extend([pattern, path])
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(),
            timeout=60
        )
        
        stdout_str = stdout.decode("utf-8", errors="replace")
        stderr_str = stderr.decode("utf-8", errors="replace")
        
        matches = []
        files = set()
        
        for line in stdout_str.split("\n"):
            if not line.strip():
                continue
            
            if output_mode == "files":
                files.add(line.strip())
            elif output_mode == "count":
                if ":" in line:
                    file, count = line.rsplit(":", 1)
                    matches.append({"file": file, "count": int(count) if count.isdigit() else 0})
            else:
                parts = line.split(":", 2)
                if len(parts) >= 2:
                    filename, line_num = parts[0], parts[1]
                    content = parts[2] if len(parts) > 2 else ""
                    files.add(filename)
                    matches.append({
                        "file": filename,
                        "line": int(line_num) if line_num.isdigit() else 0,
                        "content": content
                    })
        
        if head_limit and len(matches) > head_limit:
            matches = matches[:head_limit]
        
        execution_time = time.time() - start_time
        
        return {
            "status": "success",
            "pattern": pattern,
            "path": path,
            "tool": "ripgrep",
            "matches": matches if output_mode != "files" else list(files),
            "match_count": len(matches) if output_mode != "files" else len(files),
            "files_searched": len(files) if output_mode != "files" else len(matches),
            "execution_time": round(execution_time, 3)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": f"Ripgrep execution failed: {str(e)}"
        }


async def _grep_with_python(
    pattern: str,
    path: str,
    glob: Optional[str],
    case_sensitive: bool,
    output_mode: str,
    head_limit: Optional[int],
    context_lines: int,
    start_time: float
) -> Dict[str, Any]:
    """Fallback search using Python regex."""
    
    import fnmatch
    
    flags = 0 if case_sensitive else re.IGNORECASE
    
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        return {
            "status": "error",
            "error": f"Invalid regex pattern: {e}"
        }
    
    matches = []
    files_searched = 0
    files_with_matches = set()
    
    if os.path.isfile(path):
        files_to_search = [path]
    else:
        files_to_search = []
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                if glob:
                    if fnmatch.fnmatch(filename, glob):
                        files_to_search.append(full_path)
                else:
                    files_to_search.append(full_path)
    
    for file_path in files_to_search:
        if head_limit and len(matches) >= head_limit:
            break
        
        files_searched += 1
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except:
            continue
        
        file_matches = 0
        for i, line in enumerate(lines, 1):
            if regex.search(line):
                file_matches += 1
                files_with_matches.add(file_path)
                
                if output_mode == "files":
                    break
                elif output_mode == "count":
                    continue
                else:
                    start = max(0, i - context_lines - 1)
                    end = min(len(lines), i + context_lines)
                    context = "".join(lines[start:end])
                    
                    matches.append({
                        "file": file_path,
                        "line": i,
                        "content": line.rstrip(),
                        "context": context if context_lines > 0 else None
                    })
        
        if output_mode == "count" and file_matches > 0:
            matches.append({"file": file_path, "count": file_matches})
    
    if head_limit and len(matches) > head_limit:
        matches = matches[:head_limit]
    
    execution_time = time.time() - start_time
    
    result = {
        "status": "success",
        "pattern": pattern,
        "path": path,
        "tool": "python_regex",
        "matches": matches if output_mode != "files" else list(files_with_matches),
        "match_count": len(matches) if output_mode != "files" else len(files_with_matches),
        "files_searched": files_searched,
        "execution_time": round(execution_time, 3)
    }
    
    if output_mode == "files":
        result["files_with_matches"] = len(files_with_matches)
    
    return result


# =============================================================================
# MCP SERVER SETUP
# =============================================================================

TOOL_DESCRIPTIONS = {
    "fetch_url": {
        "name": "fetch_url",
        "description": "Fetch and extract content from URLs. Returns title, main content, and metadata. Great for reading web pages, docs, and articles.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to fetch (http/https only)"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST"],
                    "default": "GET",
                    "description": "HTTP method"
                },
                "timeout": {
                    "type": "integer",
                    "default": 30,
                    "description": "Request timeout in seconds"
                },
                "extract_text": {
                    "type": "boolean",
                    "default": True,
                    "description": "Extract main article text from HTML"
                },
                "max_length": {
                    "type": "integer",
                    "default": 100000,
                    "description": "Maximum characters to return"
                }
            },
            "required": ["url"]
        }
    },
    "shell": {
        "name": "shell",
        "description": "Execute shell commands with security guardrails. Whitelist-based command filtering. Supports Python, Node, Git, Docker, and common Unix tools.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command to execute"
                },
                "cwd": {
                    "type": "string",
                    "description": "Working directory (default: current directory)"
                },
                "timeout": {
                    "type": "integer",
                    "default": 300,
                    "maximum": 300,
                    "description": "Timeout in seconds (max 300)"
                }
            },
            "required": ["command"]
        }
    },
    "grep_search": {
        "name": "grep_search",
        "description": "Search file contents using regex. Uses ripgrep (rg) when available, falls back to Python. Supports file filtering and context lines.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Regex pattern to search for"
                },
                "path": {
                    "type": "string",
                    "default": ".",
                    "description": "Directory or file to search"
                },
                "glob": {
                    "type": "string",
                    "description": "File pattern filter (e.g., '*.py', '*.js')"
                },
                "case_sensitive": {
                    "type": "boolean",
                    "default": False,
                    "description": "Case sensitive search"
                },
                "output_mode": {
                    "type": "string",
                    "enum": ["content", "files", "count"],
                    "default": "content",
                    "description": "Output format: content (with lines), files (just names), count (match counts)"
                },
                "head_limit": {
                    "type": "integer",
                    "description": "Limit number of results"
                },
                "context_lines": {
                    "type": "integer",
                    "default": 2,
                    "description": "Lines of context around matches"
                }
            },
            "required": ["pattern"]
        }
    }
}


async def create_utils_server() -> Server:
    """Create the utilities MCP server."""
    server = Server("arifOS-MCP-Utils")
    
    @server.list_tools()
    async def list_tools() -> list[mcp.types.Tool]:
        return [
            mcp.types.Tool(
                name=name,
                description=desc["description"],
                inputSchema=desc["inputSchema"]
            )
            for name, desc in TOOL_DESCRIPTIONS.items()
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[mcp.types.TextContent]:
        try:
            if name == "fetch_url":
                result = await tool_fetch_url(**arguments)
            elif name == "shell":
                result = await tool_shell(**arguments)
            elif name == "grep_search":
                result = await tool_grep_search(**arguments)
            else:
                return [mcp.types.TextContent(type="text", text=f"Unknown tool: {name}")]
            
            import json
            formatted = json.dumps(result, indent=2, ensure_ascii=False)
            return [mcp.types.TextContent(type="text", text=formatted)]
            
        except Exception as e:
            return [mcp.types.TextContent(type="text", text=f"ERROR: {str(e)}")]
    
    return server


async def main():
    """Run the utilities MCP server."""
    print("arifOS MCP Utils Server v1.0.0 starting", file=sys.stderr)
    print(f"  Tools: fetch_url, shell, grep_search", file=sys.stderr)
    print(f"  httpx: {HTTPX_AVAILABLE}, bs4: {BS4_AVAILABLE}", file=sys.stderr)
    
    async with stdio_server() as (read_stream, write_stream):
        server = await create_utils_server()
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
