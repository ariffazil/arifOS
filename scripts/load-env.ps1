#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Backwards-compatible wrapper for load_env.ps1

.DESCRIPTION
    This wrapper maintains backwards compatibility for scripts/workflows that reference
    the old root-level load-env.ps1 file. It forwards all arguments to the actual
    implementation in scripts/load_env.ps1.

.NOTES
    Author: arifOS Engineer (Claude Code Ω)
    Authority: F6 Amanah - Reversible wrapper for backwards compatibility
    Version: v1.0 (wrapper)
    Constitutional Compliance: F2 Clarity (reduces confusion), F1 Truth (transparent)

    Migration Path:
    - OLD: . .\load-env.ps1
    - NEW: . .\scripts\load_env.ps1
    - WRAPPER: Allows old syntax to work during transition period
#>

# Forward to actual implementation
& "$PSScriptRoot\scripts\load_env.ps1" @args
