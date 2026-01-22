#!/usr/bin/env python3
"""
arifOS Bootstrap Script
Automatically sets up development environment on fresh clone

Usage:
    python bootstrap.py                    # Interactive mode
    python bootstrap.py --auto             # Auto mode (use defaults)
    python bootstrap.py --minimal          # Minimal setup (core only)
    python bootstrap.py --full             # Full setup (all tools)

This script:
1. Checks Python version
2. Creates virtual environment
3. Installs dependencies
4. Sets up pre-commit hooks
5. Configures development tools
6. Runs verification

DITEMPA BUKAN DIBERI - Your environment will be forged!
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import Optional, Tuple

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}? {text}{Colors.END}")

def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}? {text}{Colors.END}")

def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}? {text}{Colors.END}")

def print_warning(text: str):
    """Print warning message"""
    print(f"{Colors.YELLOW}? {text}{Colors.END}")

def run_command(cmd: str, check: bool = True, capture: bool = False) -> Tuple[bool, Optional[str]]:
    """Run shell command and return success status"""
    try:
        if capture:
            result = subprocess.run(
                cmd, 
                shell=True, 
                check=check,
                capture_output=True,
                text=True
            )
            return True, result.stdout.strip()
        else:
            subprocess.run(cmd, shell=True, check=check)
            return True, None
    except subprocess.CalledProcessError as e:
        if capture:
            return False, str(e)
        return False, None

def check_python_version() -> bool:
    """Check if Python version is 3.10+"""
    print_header("Step 1: Checking Python Version")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version_str} detected (required: 3.10+)")
        return True
    else:
        print_error(f"Python {version_str} detected (required: 3.10+)")
        print_info("Please install Python 3.10 or higher from https://python.org")
        return False

def check_git() -> bool:
    """Check if Git is installed"""
    success, _ = run_command("git --version", check=False, capture=True)
    if success:
        print_success("Git is installed")
        return True
    else:
        print_error("Git is not installed")
        print_info("Please install Git from https://git-scm.com")
        return False

def check_docker() -> bool:
    """Check if Docker is installed (optional)"""
    success, _ = run_command("docker --version", check=False, capture=True)
    if success:
        print_success("Docker is installed")
        return True
    else:
        print_warning("Docker is not installed (optional but recommended)")
        return False

def create_virtual_environment() -> bool:
    """Create Python virtual environment"""
    print_header("Step 2: Creating Virtual Environment")
    
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print_info("Virtual environment already exists at .venv")
        response = input("Recreate it? (y/N): ").lower().strip()
        if response == 'y':
            print_info("Removing existing virtual environment...")
            import shutil
            shutil.rmtree(venv_path)
        else:
            print_success("Using existing virtual environment")
            return True
    
    print_info("Creating virtual environment at .venv...")
    success, _ = run_command(f"{sys.executable} -m venv .venv")
    
    if success:
        print_success("Virtual environment created successfully")
        return True
    else:
        print_error("Failed to create virtual environment")
        return False

def get_activation_command() -> str:
    """Get the correct activation command for the platform"""
    system = platform.system()
    if system == "Windows":
        return ".venv\\Scripts\\activate"
    else:
        return "source .venv/bin/activate"

def get_python_executable() -> str:
    """Get the correct Python executable path"""
    system = platform.system()
    if system == "Windows":
        return ".venv\\Scripts\\python.exe"
    else:
        return ".venv/bin/python"

def install_dependencies(mode: str = "full") -> bool:
    """Install Python dependencies"""
    print_header("Step 3: Installing Dependencies")
    
    python_exe = get_python_executable()
    
    # Upgrade pip first
    print_info("Upgrading pip...")
    success, _ = run_command(f"{python_exe} -m pip install --upgrade pip")
    if not success:
        print_error("Failed to upgrade pip")
        return False
    
    # Install arifOS
    print_info("Installing arifOS package...")
    if mode == "minimal":
        success, _ = run_command(f"{python_exe} -m pip install -e .")
    else:
        success, _ = run_command(f'{python_exe} -m pip install -e ".[all]"')
    
    if not success:
        print_error("Failed to install arifOS")
        return False
    
    print_success("arifOS installed successfully")
    
    # Install dev tools if full mode
    if mode == "full":
        print_info("Installing development tools...")
        dev_tools = [
            "pre-commit",
            "safety",
            "bandit",
            "detect-secrets",
            "pytest-cov",
            "pytest-xdist",
            "mypy",
            "types-requests",
            "types-pyyaml"
        ]
        
        for tool in dev_tools:
            print_info(f"Installing {tool}...")
            success, _ = run_command(f"{python_exe} -m pip install {tool}")
            if not success:
                print_warning(f"Failed to install {tool} (continuing...)")
        
        print_success("Development tools installed")
    
    return True

def setup_precommit() -> bool:
    """Set up pre-commit hooks"""
    print_header("Step 4: Setting Up Pre-commit Hooks")
    
    python_exe = get_python_executable()
    
    # Check if pre-commit config exists
    if not Path(".pre-commit-config.yaml").exists():
        print_warning("Pre-commit config not found, skipping...")
        return True
    
    # Install pre-commit hooks
    print_info("Installing pre-commit hooks...")
    success, _ = run_command(f"{python_exe} -m pre_commit install")
    
    if success:
        print_success("Pre-commit hooks installed")
        
        # Run pre-commit on all files (optional)
        response = input("Run pre-commit on all files now? (y/N): ").lower().strip()
        if response == 'y':
            print_info("Running pre-commit on all files (this may take a while)...")
            run_command(f"{python_exe} -m pre_commit run --all-files", check=False)
        
        return True
    else:
        print_warning("Failed to install pre-commit hooks (non-critical)")
        return True

def setup_env_file() -> bool:
    """Set up .env file from .env.example"""
    print_header("Step 5: Setting Up Environment File")
    
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_example.exists():
        print_warning(".env.example not found, skipping...")
        return True
    
    if env_file.exists():
        print_info(".env file already exists")
        return True
    
    print_info("Creating .env file from .env.example...")
    import shutil
    shutil.copy(env_example, env_file)
    
    print_success(".env file created")
    print_warning("Remember to edit .env and add your API keys!")
    
    return True

def run_verification() -> bool:
    """Run verification script"""
    print_header("Step 6: Verifying Installation")
    
    python_exe = get_python_executable()
    
    if not Path("../verification/verify_setup.py").exists():
        print_warning("verify_setup.py not found, skipping verification...")
        return True
    
    print_info("Running verification...")
    success, _ = run_command(f"{python_exe} verify_setup.py")
    
    return success

def show_next_steps():
    """Show next steps to user"""
    print_header("?? Setup Complete!")
    
    activation_cmd = get_activation_command()
    
    print(f"{Colors.GREEN}Your arifOS development environment is ready!{Colors.END}\n")
    
    print(f"{Colors.BOLD}Next steps:{Colors.END}\n")
    
    print(f"1. Activate the virtual environment:")
    print(f"   {Colors.CYAN}{activation_cmd}{Colors.END}\n")
    
    print(f"2. Edit .env file with your API keys:")
    print(f"   {Colors.CYAN}notepad .env  # Windows{Colors.END}")
    print(f"   {Colors.CYAN}nano .env    # Linux/macOS{Colors.END}\n")
    
    print(f"3. Run tests:")
    print(f"   {Colors.CYAN}pytest{Colors.END}\n")
    
    print(f"4. Read the documentation:")
    print(f"   {Colors.CYAN}docs/setup/QUICK_START.md{Colors.END}\n")
    
    print(f"5. Start coding!")
    print(f"   {Colors.CYAN}code .  # VS Code{Colors.END}")
    print(f"   {Colors.CYAN}# Or use your preferred editor{Colors.END}\n")
    
    print(f"{Colors.BOLD}DITEMPA BUKAN DIBERI{Colors.END} � Your environment is forged! ???\n")

def main():
    """Main bootstrap function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bootstrap arifOS development environment")
    parser.add_argument("--auto", action="store_true", help="Run in auto mode (no prompts)")
    parser.add_argument("--minimal", action="store_true", help="Minimal setup (core only)")
    parser.add_argument("--full", action="store_true", help="Full setup (all tools)")
    
    args = parser.parse_args()
    
    # Determine mode
    if args.minimal:
        mode = "minimal"
    elif args.full or args.auto:
        mode = "full"
    else:
        # Interactive mode
        print_header("arifOS Development Environment Bootstrap")
        print("\nChoose setup mode:")
        print("1. Minimal - Core dependencies only")
        print("2. Full - Core + all development tools (recommended)")
        
        choice = input("\nEnter choice (1-2, default 2): ").strip() or "2"
        mode = "minimal" if choice == "1" else "full"
    
    print(f"\n{Colors.BOLD}Running {mode} setup...{Colors.END}\n")
    
    # Step 1: Check prerequisites
    if not check_python_version():
        return 1
    
    if not check_git():
        return 1
    
    check_docker()  # Optional
    
    # Step 2: Create virtual environment
    if not create_virtual_environment():
        return 1
    
    # Step 3: Install dependencies
    if not install_dependencies(mode):
        return 1
    
    # Step 4: Setup pre-commit (if full mode)
    if mode == "full":
        setup_precommit()
    
    # Step 5: Setup .env file
    setup_env_file()
    
    # Step 6: Run verification
    if not run_verification():
        print_warning("Verification failed, but setup is complete")
        print_info("You may need to manually install some dependencies")
    
    # Show next steps
    show_next_steps()
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

