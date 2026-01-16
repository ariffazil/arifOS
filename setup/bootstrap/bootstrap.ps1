# arifOS Bootstrap Script (PowerShell)
# Automatically sets up development environment on fresh clone
#
# Usage:
#   .\bootstrap.ps1                 # Interactive mode
#   .\bootstrap.ps1 -Auto           # Auto mode (use defaults)
#   .\bootstrap.ps1 -Minimal        # Minimal setup (core only)
#   .\bootstrap.ps1 -Full           # Full setup (all tools)

param(
    [switch]$Auto,
    [switch]$Minimal,
    [switch]$Full,
    [switch]$Help
)

# Color functions
function Write-Header($text) {
    Write-Host "`n$('='*70)" -ForegroundColor Blue
    Write-Host $text -ForegroundColor Blue
    Write-Host "$('='*70)`n" -ForegroundColor Blue
}

function Write-Success($text) {
    Write-Host "? $text" -ForegroundColor Green
}

function Write-ErrorMsg($text) {
    Write-Host "? $text" -ForegroundColor Red
}

function Write-InfoMsg($text) {
    Write-Host "? $text" -ForegroundColor Cyan
}

function Write-WarningMsg($text) {
    Write-Host "? $text" -ForegroundColor Yellow
}

if ($Help) {
    Write-Host @"
arifOS Bootstrap Script

Automatically sets up development environment on fresh clone.

Usage:
    .\bootstrap.ps1                 # Interactive mode
    .\bootstrap.ps1 -Auto           # Auto mode (use defaults)
    .\bootstrap.ps1 -Minimal        # Minimal setup (core only)
    .\bootstrap.ps1 -Full           # Full setup (all tools)

Options:
    -Auto       Run automatically without prompts
    -Minimal    Install only core dependencies
    -Full       Install all development tools (recommended)
    -Help       Show this help message

DITEMPA BUKAN DIBERI - Your environment will be forged!
"@
    exit 0
}

# Determine mode
if ($Minimal) {
    $mode = "minimal"
} elseif ($Full -or $Auto) {
    $mode = "full"
} else {
    Write-Header "arifOS Development Environment Bootstrap"
    Write-Host "Choose setup mode:"
    Write-Host "1. Minimal - Core dependencies only"
    Write-Host "2. Full - Core + all development tools (recommended)"
    $choice = Read-Host "`nEnter choice (1-2, default 2)"
    $mode = if ($choice -eq "1") { "minimal" } else { "full" }
}

Write-Host "`nRunning $mode setup...`n" -ForegroundColor Yellow

# Step 1: Check Python version
Write-Header "Step 1: Checking Python Version"

try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python (\d+)\.(\d+)\.(\d+)") {
        $major = [int]$Matches[1]
        $minor = [int]$Matches[2]
        if ($major -eq 3 -and $minor -ge 10) {
            Write-Success "Python $pythonVersion detected (required: 3.10+)"
        } else {
            Write-ErrorMsg "Python $pythonVersion detected (required: 3.10+)"
            Write-InfoMsg "Please install Python 3.10+ from https://python.org"
            exit 1
        }
    }
} catch {
    Write-ErrorMsg "Python not found"
    Write-InfoMsg "Please install Python 3.10+ from https://python.org"
    exit 1
}

# Check Git
try {
    $gitVersion = git --version 2>&1
    Write-Success "Git is installed"
} catch {
    Write-ErrorMsg "Git is not installed"
    Write-InfoMsg "Please install Git from https://git-scm.com"
    exit 1
}

# Check Docker (optional)
try {
    $dockerVersion = docker --version 2>&1
    Write-Success "Docker is installed"
} catch {
    Write-WarningMsg "Docker is not installed (optional but recommended)"
}

# Step 2: Create virtual environment
Write-Header "Step 2: Creating Virtual Environment"

if (Test-Path ".venv") {
    Write-InfoMsg "Virtual environment already exists at .venv"
    if (-not $Auto) {
        $response = Read-Host "Recreate it? (y/N)"
        if ($response -eq 'y') {
            Write-InfoMsg "Removing existing virtual environment..."
            Remove-Item -Recurse -Force .venv
        } else {
            Write-Success "Using existing virtual environment"
        }
    } else {
        Write-Success "Using existing virtual environment"
    }
}

if (-not (Test-Path ".venv")) {
    Write-InfoMsg "Creating virtual environment at .venv..."
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Virtual environment created successfully"
    } else {
        Write-ErrorMsg "Failed to create virtual environment"
        exit 1
    }
}

# Step 3: Install dependencies
Write-Header "Step 3: Installing Dependencies"

$pythonExe = ".\.venv\Scripts\python.exe"

# Upgrade pip
Write-InfoMsg "Upgrading pip..."
& $pythonExe -m pip install --upgrade pip | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Success "pip upgraded"
} else {
    Write-ErrorMsg "Failed to upgrade pip"
    exit 1
}

# Install arifOS
Write-InfoMsg "Installing arifOS package..."
if ($mode -eq "minimal") {
    & $pythonExe -m pip install -e .
} else {
    & $pythonExe -m pip install -e ".[all]"
}

if ($LASTEXITCODE -eq 0) {
    Write-Success "arifOS installed successfully"
} else {
    Write-ErrorMsg "Failed to install arifOS"
    exit 1
}

# Install dev tools if full mode
if ($mode -eq "full") {
    Write-InfoMsg "Installing development tools..."
    
    $devTools = @(
        "pre-commit",
        "safety",
        "bandit",
        "detect-secrets",
        "pytest-cov",
        "pytest-xdist",
        "mypy",
        "types-requests",
        "types-pyyaml"
    )
    
    foreach ($tool in $devTools) {
        Write-InfoMsg "Installing $tool..."
        & $pythonExe -m pip install $tool | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Write-WarningMsg "Failed to install $tool (continuing...)"
        }
    }
    
    Write-Success "Development tools installed"
}

# Step 4: Setup pre-commit (if full mode)
if ($mode -eq "full") {
    Write-Header "Step 4: Setting Up Pre-commit Hooks"
    
    if (Test-Path ".pre-commit-config.yaml") {
        Write-InfoMsg "Installing pre-commit hooks..."
        & $pythonExe -m pre_commit install | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Pre-commit hooks installed"
            
            if (-not $Auto) {
                $response = Read-Host "Run pre-commit on all files now? (y/N)"
                if ($response -eq 'y') {
                    Write-InfoMsg "Running pre-commit on all files (this may take a while)..."
                    & $pythonExe -m pre_commit run --all-files
                }
            }
        } else {
            Write-WarningMsg "Failed to install pre-commit hooks (non-critical)"
        }
    } else {
        Write-WarningMsg "Pre-commit config not found, skipping..."
    }
}

# Step 5: Setup .env file
Write-Header "Step 5: Setting Up Environment File"

if (Test-Path ".env.example") {
    if (-not (Test-Path ".env")) {
        Write-InfoMsg "Creating .env file from .env.example..."
        Copy-Item .env.example .env
        Write-Success ".env file created"
        Write-WarningMsg "Remember to edit .env and add your API keys!"
    } else {
        Write-InfoMsg ".env file already exists"
    }
} else {
    Write-WarningMsg ".env.example not found, skipping..."
}

# Step 6: Run verification
Write-Header "Step 6: Verifying Installation"

if (Test-Path "verify_setup.py") {
    Write-InfoMsg "Running verification..."
    & $pythonExe verify_setup.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-WarningMsg "Verification failed, but setup is complete"
        Write-InfoMsg "You may need to manually install some dependencies"
    }
} else {
    Write-WarningMsg "verify_setup.py not found, skipping verification..."
}

# Show next steps
Write-Header "?? Setup Complete!"

Write-Host "Your arifOS development environment is ready!`n" -ForegroundColor Green

Write-Host "Next steps:`n" -ForegroundColor Yellow

Write-Host "1. Activate the virtual environment:"
Write-Host "   .\.venv\Scripts\Activate.ps1`n" -ForegroundColor Cyan

Write-Host "2. Edit .env file with your API keys:"
Write-Host "   notepad .env`n" -ForegroundColor Cyan

Write-Host "3. Run tests:"
Write-Host "   pytest`n" -ForegroundColor Cyan

Write-Host "4. Read the documentation:"
Write-Host "   docs/setup/QUICK_START.md`n" -ForegroundColor Cyan

Write-Host "5. Start coding!"
Write-Host "   code .  # VS Code" -ForegroundColor Cyan
Write-Host "   # Or use your preferred editor`n" -ForegroundColor Cyan

Write-Host "DITEMPA BUKAN DIBERI — Your environment is forged! ???`n" -ForegroundColor Green
