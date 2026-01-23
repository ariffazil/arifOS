# Install Recommended Dependencies for arifOS
# Run this script to install all recommended tools in phases

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  arifOS Recommended Dependencies Installation" -ForegroundColor Cyan
Write-Host "  Constitutional AI Development Enhancement" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment first
$venvPath = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & $venvPath
} else {
    Write-Host "ERROR: Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please run from arifOS root directory." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Choose installation phase:" -ForegroundColor Yellow
Write-Host "1. Critical Tools Only (Pre-commit, Security, Testing)" -ForegroundColor White
Write-Host "2. Production Tools (+ Documentation, Profiling, Database)" -ForegroundColor White
Write-Host "3. Full Stack (+ Agent Frameworks, Jupyter, Visualization)" -ForegroundColor White
Write-Host "4. Install All (Everything)" -ForegroundColor White
Write-Host "5. Custom Selection" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter choice (1-5)"

function Install-Critical {
    Write-Host "`n=====================================" -ForegroundColor Cyan
    Write-Host "Phase 1: CRITICAL TOOLS" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    
    Write-Host "`n[1/5] Pre-commit hooks..." -ForegroundColor Yellow
    pip install pre-commit pre-commit-hooks
    
    Write-Host "`n[2/5] Security scanners..." -ForegroundColor Yellow
    pip install safety pip-audit bandit detect-secrets
    
    Write-Host "`n[3/5] Testing tools..." -ForegroundColor Yellow
    pip install pytest-cov pytest-xdist pytest-timeout pytest-benchmark pytest-httpx requests-mock
    
    Write-Host "`n[4/5] Environment management..." -ForegroundColor Yellow
    pip install pip-tools python-dotenv
    
    Write-Host "`n[5/5] Type checking..." -ForegroundColor Yellow
    pip install mypy types-requests types-pyyaml
    
    Write-Host "`n? Critical tools installed!" -ForegroundColor Green
}

function Install-Production {
    Write-Host "`n=====================================" -ForegroundColor Cyan
    Write-Host "Phase 2: PRODUCTION TOOLS" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    
    Write-Host "`n[1/6] Documentation generators..." -ForegroundColor Yellow
    pip install mkdocs mkdocs-material "mkdocstrings[python]" mkdocs-mermaid2-plugin
    
    Write-Host "`n[2/6] Performance profiling..." -ForegroundColor Yellow
    pip install py-spy memory_profiler line_profiler scalene
    
    Write-Host "`n[3/6] Observability..." -ForegroundColor Yellow
    pip install opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi structlog
    
    Write-Host "`n[4/6] Database tools..." -ForegroundColor Yellow
    pip install sqlalchemy alembic psycopg2-binary asyncpg
    
    Write-Host "`n[5/6] Redis..." -ForegroundColor Yellow
    pip install redis aioredis
    
    Write-Host "`n[6/6] Vector database..." -ForegroundColor Yellow
    pip install chromadb sentence-transformers
    
    Write-Host "`n? Production tools installed!" -ForegroundColor Green
}

function Install-FullStack {
    Write-Host "`n=====================================" -ForegroundColor Cyan
    Write-Host "Phase 3: FULL STACK" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    
    Write-Host "`n[1/5] Agent frameworks..." -ForegroundColor Yellow
    pip install langchain langchain-core langchain-community llamaindex pyautogen crewai
    
    Write-Host "`n[2/5] API testing..." -ForegroundColor Yellow
    pip install httpx pytest-httpx locust openapi-spec-validator
    
    Write-Host "`n[3/5] CI/CD tools..." -ForegroundColor Yellow
    pip install tox nox "coverage[toml]"
    
    Write-Host "`n[4/5] Interactive tools..." -ForegroundColor Yellow
    pip install jupyter ipython ipykernel rich-cli
    
    Write-Host "`n[5/5] Quality tools..." -ForegroundColor Yellow
    pip install radon wily vulture interrogate commitizen matplotlib seaborn plotly
    
    Write-Host "`n? Full stack installed!" -ForegroundColor Green
}

function Show-Summary {
    Write-Host "`n================================================================" -ForegroundColor Cyan
    Write-Host "  INSTALLATION COMPLETE!" -ForegroundColor Cyan
    Write-Host "================================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Initialize pre-commit hooks:" -ForegroundColor White
    Write-Host "   pre-commit install" -ForegroundColor Gray
    Write-Host ""
    Write-Host "2. Run security scans:" -ForegroundColor White
    Write-Host "   safety check" -ForegroundColor Gray
    Write-Host "   bandit -r arifos_core/" -ForegroundColor Gray
    Write-Host ""
    Write-Host "3. Test with coverage:" -ForegroundColor White
    Write-Host "   pytest --cov=arifos_core --cov-report=html" -ForegroundColor Gray
    Write-Host ""
    Write-Host "4. Verify installation:" -ForegroundColor White
    Write-Host "   python verify_setup.py" -ForegroundColor Gray
    Write-Host ""
    Write-Host "5. Read the full guide:" -ForegroundColor White
    Write-Host "   RECOMMENDED_DEPENDENCIES_RESEARCH.md" -ForegroundColor Gray
    Write-Host ""
    Write-Host "DITEMPA BUKAN DIBERI - Your tools are forged! ??" -ForegroundColor Green
    Write-Host ""
}

# Execute based on choice
switch ($choice) {
    "1" {
        Install-Critical
        Show-Summary
    }
    "2" {
        Install-Critical
        Install-Production
        Show-Summary
    }
    "3" {
        Install-Critical
        Install-Production
        Install-FullStack
        Show-Summary
    }
    "4" {
        Write-Host "`n? Installing EVERYTHING..." -ForegroundColor Cyan
        Install-Critical
        Install-Production
        Install-FullStack
        Show-Summary
    }
    "5" {
        Write-Host "`n?? Custom Selection:" -ForegroundColor Cyan
        Write-Host ""
        
        $installCritical = Read-Host "Install critical tools? (y/n)"
        if ($installCritical -eq "y") { Install-Critical }
        
        $installProd = Read-Host "Install production tools? (y/n)"
        if ($installProd -eq "y") { Install-Production }
        
        $installFull = Read-Host "Install full stack? (y/n)"
        if ($installFull -eq "y") { Install-FullStack }
        
        Show-Summary
    }
    default {
        Write-Host "Invalid choice. Exiting." -ForegroundColor Red
        exit 1
    }
}

Write-Host "Run time: $((Get-Date).ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Gray
