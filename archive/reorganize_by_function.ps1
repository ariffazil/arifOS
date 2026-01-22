# Setup Directory Reorganization Script
# Organizes by FUNCTION not file type

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  arifOS Setup Reorganization - Function-Based Structure" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Creating function-based directory structure..." -ForegroundColor Yellow
Write-Host ""

# Create new structure
New-Item -ItemType Directory -Force -Path "setup" | Out-Null
New-Item -ItemType Directory -Force -Path "setup/bootstrap" | Out-Null
New-Item -ItemType Directory -Force -Path "setup/docs" | Out-Null
New-Item -ItemType Directory -Force -Path "setup/tools" | Out-Null
New-Item -ItemType Directory -Force -Path "setup/verification" | Out-Null

Write-Host "? Created setup/ directory structure" -ForegroundColor Green
Write-Host ""

# Move bootstrap scripts
Write-Host "Moving bootstrap files..." -ForegroundColor Yellow
$bootstrapFiles = @(
    "bootstrap.py",
    "bootstrap.ps1", 
    "bootstrap.sh",
    "BOOTSTRAP_GUIDE.md"
)

foreach ($file in $bootstrapFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "setup/bootstrap/" -Force
        Write-Host "  ? Moved $file" -ForegroundColor Cyan
    }
}

# Move documentation
Write-Host "`nMoving documentation files..." -ForegroundColor Yellow
$docFiles = @(
    "IDE_AGNOSTIC_SUMMARY.md",
    "QUICK_START.md",
    "DEVELOPMENT_SETUP.md",
    "SETUP_COMPLETE.md",
    "DEPENDENCY_ENHANCEMENT_SUMMARY.md",
    "RECOMMENDED_DEPENDENCIES_RESEARCH.md",
    "TOOLS_QUICK_START.md",
    "DOCUMENTATION_INDEX.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "setup/docs/" -Force
        Write-Host "  ? Moved $file" -ForegroundColor Cyan
    }
}

# Move tools
Write-Host "`nMoving tool scripts..." -ForegroundColor Yellow
$toolFiles = @(
    "install_recommended_deps.ps1",
    "housekeeping.ps1"
)

foreach ($file in $toolFiles) {
    if (Test-Path $file) {
        Move-Item -Path $file -Destination "setup/tools/" -Force
        Write-Host "  ? Moved $file" -ForegroundColor Cyan
    }
}

# Move verification
Write-Host "`nMoving verification scripts..." -ForegroundColor Yellow
if (Test-Path "verify_setup.py") {
    Move-Item -Path "verify_setup.py" -Destination "setup/verification/" -Force
    Write-Host "  ? Moved verify_setup.py" -ForegroundColor Cyan
}

# Keep these in root (required by tools)
Write-Host "`nKeeping in root (required by tools):" -ForegroundColor Yellow
$rootConfigs = @(
    ".pre-commit-config.yaml",
    "pytest.ini",
    "mypy.ini",
    "pyproject.toml",
    ".env",
    ".env.example"
)

foreach ($file in $rootConfigs) {
    if (Test-Path $file) {
        Write-Host "  ? $file" -ForegroundColor Green
    }
}

# Create README files
Write-Host "`nCreating README files..." -ForegroundColor Yellow

# Main setup README
$setupReadme = @"
# Setup Directory

All setup-related files organized by function.

## Quick Start

**New machine setup:**
``````bash
# From project root
python setup/bootstrap/bootstrap.py --full
``````

## Directory Structure

``````
setup/
??? bootstrap/          # Bootstrap scripts and guides
?   ??? bootstrap.py    # Cross-platform Python script
?   ??? bootstrap.ps1   # Windows PowerShell script
?   ??? bootstrap.sh    # macOS/Linux Bash script
?   ??? BOOTSTRAP_GUIDE.md
?
??? docs/              # Setup documentation
?   ??? IDE_AGNOSTIC_SUMMARY.md      # Why it works everywhere
?   ??? QUICK_START.md               # Essential commands
?   ??? DEVELOPMENT_SETUP.md         # Full IDE configuration
?   ??? DEPENDENCY_ENHANCEMENT_SUMMARY.md
?   ??? RECOMMENDED_DEPENDENCIES_RESEARCH.md
?   ??? TOOLS_QUICK_START.md
?   ??? DOCUMENTATION_INDEX.md
?
??? tools/             # Installation and utility scripts
?   ??? install_recommended_deps.ps1
?   ??? housekeeping.ps1
?
??? verification/      # Verification and testing
    ??? verify_setup.py
``````

## Configuration Files (Root)

These must stay in project root:
- ``.pre-commit-config.yaml`` - Git hooks (required by pre-commit)
- ``pytest.ini`` - Test configuration (required by pytest)
- ``mypy.ini`` - Type checking (required by mypy)
- ``pyproject.toml`` - Package metadata (required by pip)

## Usage

### Bootstrap New Machine
``````bash
# Windows
.\setup\bootstrap\bootstrap.ps1 --full

# macOS/Linux
./setup/bootstrap/bootstrap.sh --full

# Cross-platform
python setup/bootstrap/bootstrap.py --full
``````

### Verify Installation
``````bash
python setup/verification/verify_setup.py
``````

### Install Additional Tools
``````powershell
.\setup\tools\install_recommended_deps.ps1
``````

### Read Documentation
Start with: ``setup/docs/DOCUMENTATION_INDEX.md``

## See Also

- [../README.md](../README.md) - Project overview
- [../AGENTS.md](../AGENTS.md) - Agent specifications
- [../L1_THEORY/](../L1_THEORY/) - Constitutional law
"@

Set-Content "setup/README.md" -Value $setupReadme
Write-Host "  ? Created setup/README.md" -ForegroundColor Green

# Bootstrap README
$bootstrapReadme = @"
# Bootstrap Scripts

One-command setup for fresh clone.

## Usage

**Windows:**
``````powershell
.\bootstrap.ps1 --full
``````

**macOS/Linux:**
``````bash
chmod +x bootstrap.sh
./bootstrap.sh --full
``````

**Cross-platform:**
``````bash
python bootstrap.py --full
``````

## Modes

- ``--full`` - Full setup (recommended)
- ``--minimal`` - Core only
- ``--auto`` - Auto mode (no prompts)

## What It Does

1. Checks Python 3.10+
2. Creates virtual environment
3. Installs dependencies
4. Sets up pre-commit hooks
5. Creates .env file
6. Runs verification

## See Also

- [BOOTSTRAP_GUIDE.md](BOOTSTRAP_GUIDE.md) - Detailed guide
- [../docs/QUICK_START.md](../docs/QUICK_START.md) - After bootstrap
"@

Set-Content "setup/bootstrap/README.md" -Value $bootstrapReadme
Write-Host "  ? Created setup/bootstrap/README.md" -ForegroundColor Green

# Docs README
$docsReadme = @"
# Setup Documentation

All setup and configuration documentation.

## Start Here

1. **[IDE_AGNOSTIC_SUMMARY.md](IDE_AGNOSTIC_SUMMARY.md)** - Works with any IDE
2. **[QUICK_START.md](QUICK_START.md)** - Essential commands
3. **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete index

## Full Guides

- **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - IDE configuration
- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - What was installed
- **[DEPENDENCY_ENHANCEMENT_SUMMARY.md](DEPENDENCY_ENHANCEMENT_SUMMARY.md)** - Tool recommendations
- **[RECOMMENDED_DEPENDENCIES_RESEARCH.md](RECOMMENDED_DEPENDENCIES_RESEARCH.md)** - Deep dive (35+ tools)
- **[TOOLS_QUICK_START.md](TOOLS_QUICK_START.md)** - How to use each tool

## Quick Reference

- Bootstrap: [../bootstrap/BOOTSTRAP_GUIDE.md](../bootstrap/BOOTSTRAP_GUIDE.md)
- Verification: [../verification/](../verification/)
- Tools: [../tools/](../tools/)
"@

Set-Content "setup/docs/README.md" -Value $docsReadme
Write-Host "  ? Created setup/docs/README.md" -ForegroundColor Green

# Tools README
$toolsReadme = @"
# Setup Tools

Installation and utility scripts.

## Install Additional Tools

``````powershell
.\install_recommended_deps.ps1
``````

Choose from:
1. Critical tools only
2. Production tools
3. Full stack
4. Everything

## Housekeeping

Reorganize files (if needed):
``````powershell
.\housekeeping.ps1
``````

## See Also

- [../docs/RECOMMENDED_DEPENDENCIES_RESEARCH.md](../docs/RECOMMENDED_DEPENDENCIES_RESEARCH.md) - Tool research
- [../docs/TOOLS_QUICK_START.md](../docs/TOOLS_QUICK_START.md) - Usage guide
"@

Set-Content "setup/tools/README.md" -Value $toolsReadme
Write-Host "  ? Created setup/tools/README.md" -ForegroundColor Green

# Verification README
$verificationReadme = @"
# Verification Scripts

Verify your installation is working correctly.

## Run Verification

``````bash
# Activate environment first
source .venv/bin/activate  # macOS/Linux
.\.venv\Scripts\Activate.ps1  # Windows

# Run verification
python verify_setup.py
``````

## Expected Output

``````
[OK] Python Version     Python 3.14.0
[OK] NumPy              NumPy 2.4.0
[OK] Pydantic           pydantic 2.12.5
[OK] LiteLLM            litellm
[OK] FastAPI            fastapi 0.128.0
[OK] Uvicorn            uvicorn 0.40.0
[OK] FastMCP            FastMCP 2.14.2
[OK] DSPy               DSPy 2.6.5
[OK] Pytest             pytest 9.0.2
[OK] Black              black 25.12.0
[OK] Ruff               ruff
[OK] arifOS APEX Prime  v46.3.1? OK
[OK] Docker             Docker version 29.1.3

[OK] All checks passed! (13/13)
``````

## Troubleshooting

If checks fail:
1. Activate virtual environment
2. Reinstall: ``pip install -e ".[all]"``
3. Check [../docs/DEVELOPMENT_SETUP.md](../docs/DEVELOPMENT_SETUP.md)
"@

Set-Content "setup/verification/README.md" -Value $verificationReadme
Write-Host "  ? Created setup/verification/README.md" -ForegroundColor Green

# Update paths in bootstrap scripts
Write-Host "`nUpdating paths in bootstrap scripts..." -ForegroundColor Yellow

# Update bootstrap.py
if (Test-Path "setup/bootstrap/bootstrap.py") {
    $content = Get-Content "setup/bootstrap/bootstrap.py" -Raw
    $content = $content -replace 'Path\("verify_setup.py"\)', 'Path("../verification/verify_setup.py")'
    Set-Content "setup/bootstrap/bootstrap.py" -Value $content
    Write-Host "  ? Updated bootstrap.py" -ForegroundColor Cyan
}

# Summary
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  Reorganization Complete!" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "New function-based structure:" -ForegroundColor Green
Write-Host ""
Write-Host "  setup/" -ForegroundColor Yellow
Write-Host "  ??? bootstrap/          # Bootstrap scripts & guide" -ForegroundColor Cyan
Write-Host "  ?   ??? bootstrap.py"
Write-Host "  ?   ??? bootstrap.ps1"
Write-Host "  ?   ??? bootstrap.sh"
Write-Host "  ?   ??? BOOTSTRAP_GUIDE.md"
Write-Host "  ?   ??? README.md"
Write-Host "  ?"
Write-Host "  ??? docs/              # Setup documentation" -ForegroundColor Cyan
Write-Host "  ?   ??? IDE_AGNOSTIC_SUMMARY.md"
Write-Host "  ?   ??? QUICK_START.md"
Write-Host "  ?   ??? DEVELOPMENT_SETUP.md"
Write-Host "  ?   ??? DOCUMENTATION_INDEX.md"
Write-Host "  ?   ??? ... (4 more docs)"
Write-Host "  ?"
Write-Host "  ??? tools/             # Installation scripts" -ForegroundColor Cyan
Write-Host "  ?   ??? install_recommended_deps.ps1"
Write-Host "  ?   ??? housekeeping.ps1"
Write-Host "  ?"
Write-Host "  ??? verification/      # Verification scripts" -ForegroundColor Cyan
Write-Host "  ?   ??? verify_setup.py"
Write-Host "  ?"
Write-Host "  ??? README.md          # Setup overview"
Write-Host ""
Write-Host "  Root (configs):" -ForegroundColor Yellow
Write-Host "  ??? .pre-commit-config.yaml" -ForegroundColor Green
Write-Host "  ??? pytest.ini" -ForegroundColor Green
Write-Host "  ??? mypy.ini" -ForegroundColor Green
Write-Host "  ??? pyproject.toml" -ForegroundColor Green
Write-Host ""

Write-Host "Usage:" -ForegroundColor Yellow
Write-Host "  # Bootstrap" -ForegroundColor Cyan
Write-Host "  python setup/bootstrap/bootstrap.py --full"
Write-Host ""
Write-Host "  # Verify" -ForegroundColor Cyan
Write-Host "  python setup/verification/verify_setup.py"
Write-Host ""
Write-Host "  # Read docs" -ForegroundColor Cyan
Write-Host "  cat setup/docs/QUICK_START.md"
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Test bootstrap: python setup/bootstrap/bootstrap.py --full"
Write-Host "  2. Update README.md with new paths"
Write-Host "  3. Commit changes"
Write-Host ""

Write-Host "DITEMPA BUKAN DIBERI — Organized by function! ???" -ForegroundColor Green
Write-Host ""
