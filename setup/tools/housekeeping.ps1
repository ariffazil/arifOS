# Housekeeping Script - Organize arifOS Documentation
# Moves all setup documentation to proper locations

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  arifOS Documentation Housekeeping" -ForegroundColor Cyan
Write-Host "  Organizing files into proper structure" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Create directories if they don't exist
Write-Host "Creating directory structure..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "docs/setup" | Out-Null
New-Item -ItemType Directory -Force -Path "scripts/setup" | Out-Null

# Move documentation files to docs/setup/
Write-Host "`nMoving documentation files to docs/setup/..." -ForegroundColor Yellow

$docFiles = @(
    "IDE_AGNOSTIC_SUMMARY.md",
    "DEPENDENCY_ENHANCEMENT_SUMMARY.md",
    "RECOMMENDED_DEPENDENCIES_RESEARCH.md",
    "TOOLS_QUICK_START.md",
    "DEVELOPMENT_SETUP.md",
    "QUICK_START.md",
    "SETUP_COMPLETE.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Write-Host "  Moving $file" -ForegroundColor Cyan
        Move-Item -Path $file -Destination "docs/setup/" -Force
    } else {
        Write-Host "  Skipping $file (not found)" -ForegroundColor Gray
    }
}

# Move setup scripts to scripts/setup/
Write-Host "`nMoving setup scripts to scripts/setup/..." -ForegroundColor Yellow

$scriptFiles = @(
    "install_recommended_deps.ps1"
)

foreach ($file in $scriptFiles) {
    if (Test-Path $file) {
        Write-Host "  Moving $file" -ForegroundColor Cyan
        Move-Item -Path $file -Destination "scripts/setup/" -Force
    } else {
        Write-Host "  Skipping $file (not found)" -ForegroundColor Gray
    }
}

# Keep these in root (frequently accessed)
Write-Host "`nKeeping in root directory:" -ForegroundColor Yellow
$rootFiles = @(
    "BOOTSTRAP_GUIDE.md",
    "DOCUMENTATION_INDEX.md",
    "README.md",
    "AGENTS.md",
    "bootstrap.py",
    "bootstrap.ps1",
    "bootstrap.sh",
    "verify_setup.py"
)

foreach ($file in $rootFiles) {
    if (Test-Path $file) {
        Write-Host "  ? $file" -ForegroundColor Green
    } else {
        Write-Host "  ? $file (missing)" -ForegroundColor Red
    }
}

# Update DOCUMENTATION_INDEX.md paths
Write-Host "`nUpdating documentation paths..." -ForegroundColor Yellow

if (Test-Path "DOCUMENTATION_INDEX.md") {
    $content = Get-Content "DOCUMENTATION_INDEX.md" -Raw
    
    # Update paths
    $content = $content -replace '\[IDE_AGNOSTIC_SUMMARY\.md\]\(IDE_AGNOSTIC_SUMMARY\.md\)', '[docs/setup/IDE_AGNOSTIC_SUMMARY.md](docs/setup/IDE_AGNOSTIC_SUMMARY.md)'
    $content = $content -replace '\[DEPENDENCY_ENHANCEMENT_SUMMARY\.md\]\(DEPENDENCY_ENHANCEMENT_SUMMARY\.md\)', '[docs/setup/DEPENDENCY_ENHANCEMENT_SUMMARY.md](docs/setup/DEPENDENCY_ENHANCEMENT_SUMMARY.md)'
    $content = $content -replace '\[RECOMMENDED_DEPENDENCIES_RESEARCH\.md\]\(RECOMMENDED_DEPENDENCIES_RESEARCH\.md\)', '[docs/setup/RECOMMENDED_DEPENDENCIES_RESEARCH.md](docs/setup/RECOMMENDED_DEPENDENCIES_RESEARCH.md)'
    $content = $content -replace '\[TOOLS_QUICK_START\.md\]\(TOOLS_QUICK_START\.md\)', '[docs/setup/TOOLS_QUICK_START.md](docs/setup/TOOLS_QUICK_START.md)'
    $content = $content -replace '\[DEVELOPMENT_SETUP\.md\]\(DEVELOPMENT_SETUP\.md\)', '[docs/setup/DEVELOPMENT_SETUP.md](docs/setup/DEVELOPMENT_SETUP.md)'
    $content = $content -replace '\[QUICK_START\.md\]\(QUICK_START\.md\)', '[docs/setup/QUICK_START.md](docs/setup/QUICK_START.md)'
    $content = $content -replace '\[SETUP_COMPLETE\.md\]\(SETUP_COMPLETE\.md\)', '[docs/setup/SETUP_COMPLETE.md](docs/setup/SETUP_COMPLETE.md)'
    
    Set-Content "DOCUMENTATION_INDEX.md" -Value $content
    Write-Host "  ? Updated DOCUMENTATION_INDEX.md" -ForegroundColor Green
}

# Create README in docs/setup/
Write-Host "`nCreating docs/setup/README.md..." -ForegroundColor Yellow

$setupReadme = @"
# Setup Documentation

This directory contains all development setup documentation.

## Quick Start

New to arifOS? Start here:

1. **[../../../BOOTSTRAP_GUIDE.md](../../../BOOTSTRAP_GUIDE.md)** - One-command setup
2. **[IDE_AGNOSTIC_SUMMARY.md](IDE_AGNOSTIC_SUMMARY.md)** - Works with any IDE
3. **[QUICK_START.md](QUICK_START.md)** - Essential commands

## Full Documentation

- **[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** - What was installed
- **[DEVELOPMENT_SETUP.md](DEVELOPMENT_SETUP.md)** - Full IDE configuration
- **[DEPENDENCY_ENHANCEMENT_SUMMARY.md](DEPENDENCY_ENHANCEMENT_SUMMARY.md)** - Tool recommendations
- **[RECOMMENDED_DEPENDENCIES_RESEARCH.md](RECOMMENDED_DEPENDENCIES_RESEARCH.md)** - Deep research (35+ tools)
- **[TOOLS_QUICK_START.md](TOOLS_QUICK_START.md)** - How to use each tool

## Bootstrap Scripts

Located in project root:
- ``bootstrap.py`` - Cross-platform Python script
- ``bootstrap.ps1`` - Windows PowerShell script
- ``bootstrap.sh`` - macOS/Linux Bash script

## See Also

- [../../DOCUMENTATION_INDEX.md](../../DOCUMENTATION_INDEX.md) - Complete documentation index
- [../../README.md](../../README.md) - Project overview
- [../../AGENTS.md](../../AGENTS.md) - Agent specifications
"@

Set-Content "docs/setup/README.md" -Value $setupReadme
Write-Host "  ? Created docs/setup/README.md" -ForegroundColor Green

# Summary
Write-Host "`n================================================================" -ForegroundColor Cyan
Write-Host "  Housekeeping Complete!" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "New structure:" -ForegroundColor Green
Write-Host "  Root directory (frequently accessed):"
Write-Host "    - BOOTSTRAP_GUIDE.md" -ForegroundColor Cyan
Write-Host "    - DOCUMENTATION_INDEX.md" -ForegroundColor Cyan
Write-Host "    - bootstrap.py / bootstrap.ps1 / bootstrap.sh" -ForegroundColor Cyan
Write-Host "    - verify_setup.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  docs/setup/ (setup documentation):"
Write-Host "    - IDE_AGNOSTIC_SUMMARY.md" -ForegroundColor Cyan
Write-Host "    - QUICK_START.md" -ForegroundColor Cyan
Write-Host "    - DEVELOPMENT_SETUP.md" -ForegroundColor Cyan
Write-Host "    - And 4 more..." -ForegroundColor Cyan
Write-Host ""
Write-Host "  scripts/setup/ (setup utilities):"
Write-Host "    - install_recommended_deps.ps1" -ForegroundColor Cyan
Write-Host ""

Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Review the new structure"
Write-Host "  2. Test bootstrap script: .\bootstrap.ps1 --full"
Write-Host "  3. Commit changes to Git"
Write-Host ""

Write-Host "DITEMPA BUKAN DIBERI — Documentation is organized! ???" -ForegroundColor Green
Write-Host ""
