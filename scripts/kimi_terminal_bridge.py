#!/usr/bin/env python3
"""
Kimi Terminal Bridge - Direct integration for copying terminal output

This script provides a direct bridge between terminal output and Kimi CLI,
enabling seamless copy/paste functionality with slash command support.
"""

import sys
import os
import tempfile
import argparse
from pathlib import Path
from typing import Optional, List

def capture_terminal_output(lines: int = 50, output_file: Optional[str] = None) -> str:
    """Capture the last N lines from terminal output file."""
    if output_file is None:
        output_file = os.path.expanduser(r"~\.arifos_clip\terminal_output.log")
    
    output_path = Path(output_file)
    if not output_path.exists():
        print(f"❌ Terminal output file not found: {output_file}", file=sys.stderr)
        print("💡 Tip: Configure VS Code to log terminal output to this file", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(output_path, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
        
        # Get last N lines
        captured_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        content = ''.join(captured_lines)
        
        print(f"📋 Captured {len(captured_lines)} lines from terminal output", file=sys.stderr)
        return content
    except Exception as e:
        print(f"❌ Error reading terminal output: {e}", file=sys.stderr)
        sys.exit(1)


def create_temp_file(content: str) -> str:
    """Create a temporary file with the captured content."""
    temp_dir = Path(tempfile.gettempdir()) / ".arifos_clip"
    temp_dir.mkdir(exist_ok=True)
    
    temp_file = temp_dir / f"terminal_capture_{os.getpid()}.log"
    
    with open(temp_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return str(temp_file)


def display_preview(content: str, max_lines: int = 10):
    """Display a preview of the captured content."""
    lines = content.splitlines()
    print("📝 Preview (first 10 lines):", file=sys.stderr)
    
    for i, line in enumerate(lines[:max_lines]):
        print(f"  {line}", file=sys.stderr)
    
    if len(lines) > max_lines:
        print(f"  ... ({len(lines) - max_lines} more lines)", file=sys.stderr)
    print(file=sys.stderr)


def execute_kimi_command(command: str, temp_file: str, args: List[str]):
    """Execute Kimi CLI with the captured content."""
    try:
        # Try to import and use Kimi CLI directly
        from kimi_cli.main import main as kimi_main
        
        # Build command line arguments
        kimi_args = [command, temp_file] + args
        
        print(f"🚀 Executing Kimi command: {' '.join(kimi_args)}", file=sys.stderr)
        
        # Save original argv and replace
        original_argv = sys.argv
        sys.argv = ["kimi"] + kimi_args
        
        try:
            kimi_main()
        finally:
            # Restore original argv
            sys.argv = original_argv
            
    except ImportError:
        print("⚠️  Direct Kimi CLI import failed, falling back to subprocess", file=sys.stderr)
        import subprocess
        
        kimi_args = ["kimi", command, temp_file] + args
        
        try:
            result = subprocess.run(kimi_args, capture_output=False)
            sys.exit(result.returncode)
        except FileNotFoundError:
            print("❌ Kimi CLI not found. Please install it first.", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Capture terminal output and send to Kimi CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /paste                    # Capture and paste to Kimi
  %(prog)s -l 100 /explain           # Capture 100 lines and explain
  %(prog)s -f custom.log /analyze    # Use custom output file
  %(prog)s --auto /debug             # Auto-detect terminal and capture
        """
    )
    
    parser.add_argument(
        "-l", "--lines",
        type=int,
        default=50,
        help="Number of lines to capture (default: 50)"
    )
    
    parser.add_argument(
        "-f", "--file",
        type=str,
        help="Path to terminal output file"
    )
    
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-detect VS Code terminal output location"
    )
    
    parser.add_argument(
        "-p", "--preview",
        action="store_true",
        help="Show preview before sending"
    )
    
    parser.add_argument(
        "command",
        type=str,
        nargs="?",
        default="/paste",
        help="Kimi slash command to execute (default: /paste)"
    )
    
    parser.add_argument(
        "args",
        nargs=argparse.REMAINDER,
        help="Additional arguments for the Kimi command"
    )
    
    args = parser.parse_args()
    
    # Determine output file
    output_file = args.file
    if args.auto:
        # Try to auto-detect VS Code terminal output
        vscode_terminal_path = Path.home() / ".vscode" / "terminal.log"
        if vscode_terminal_path.exists():
            output_file = str(vscode_terminal_path)
        else:
            print("⚠️  Auto-detect failed, using default location", file=sys.stderr)
    
    # Capture terminal output
    content = capture_terminal_output(args.lines, output_file)
    
    if not content.strip():
        print("⚠️  No content captured from terminal", file=sys.stderr)
        sys.exit(0)
    
    # Show preview if requested
    if args.preview:
        display_preview(content)
    
    # Create temp file
    temp_file = create_temp_file(content)
    
    try:
        # Execute Kimi command
        execute_kimi_command(args.command, temp_file, args.args)
    finally:
        # Schedule temp file cleanup
        try:
            os.unlink(temp_file)
        except:
            pass


if __name__ == "__main__":
    main()
