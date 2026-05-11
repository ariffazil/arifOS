param(
    [ValidateSet("tools/list", "tools/call", "raw")]
    [string]$Mode = "tools/list",

    [string]$ToolName,

    [string]$ArgumentsJson = "{}",

    [string]$RequestJson,

    [string]$PythonExe = "python",

    [string]$RepoRoot = "C:\Users\arif.fazil\OneDrive - PETRONAS\Documents\DOWNLOADS\arifOS-main",

    [int]$TimeoutSeconds = 30,

    [switch]$RawFrames
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function New-McpFrame {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Id,

        [Parameter(Mandatory = $true)]
        [string]$Method,

        [Parameter(Mandatory = $true)]
        [object]$Params
    )

    return [ordered]@{
        jsonrpc = "2.0"
        id = $Id
        method = $Method
        params = $Params
    }
}

function ConvertTo-CompactJson {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Value
    )

    return ($Value | ConvertTo-Json -Depth 100 -Compress)
}

function Parse-JsonOrThrow {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Json,

        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    try {
        return $Json | ConvertFrom-Json -Depth 100
    }
    catch {
        throw "$Label is not valid JSON. $($_.Exception.Message)"
    }
}

function Build-RequestFrame {
    if ($Mode -eq "tools/list") {
        return (New-McpFrame -Id 2 -Method "tools/list" -Params ([ordered]@{}))
    }

    if ($Mode -eq "tools/call") {
        if ([string]::IsNullOrWhiteSpace($ToolName)) {
            throw "ToolName is required when Mode is tools/call."
        }

        $arguments = Parse-JsonOrThrow -Json $ArgumentsJson -Label "ArgumentsJson"
        return (New-McpFrame -Id 2 -Method "tools/call" -Params ([ordered]@{
            name = $ToolName
            arguments = $arguments
        }))
    }

    if ([string]::IsNullOrWhiteSpace($RequestJson)) {
        throw "RequestJson is required when Mode is raw."
    }

    $rawRequest = Parse-JsonOrThrow -Json $RequestJson -Label "RequestJson"
    if (-not $rawRequest.PSObject.Properties.Name.Contains("id")) {
        throw "Raw request must include an id so the response can be matched."
    }
    return $rawRequest
}

function Invoke-ArifosMcp {
    param(
        [Parameter(Mandatory = $true)]
        [object]$RequestFrame
    )

    $initializeFrame = New-McpFrame -Id 1 -Method "initialize" -Params ([ordered]@{
        protocolVersion = "2025-11-05"
        capabilities = [ordered]@{}
        clientInfo = [ordered]@{
            name = "arifos-powershell-client"
            version = "1.0"
        }
    })

    $initializedNotification = [ordered]@{
        jsonrpc = "2.0"
        method = "notifications/initialized"
        params = [ordered]@{}
    }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $PythonExe
    $psi.Arguments = "-m arifosmcp.runtime stdio"
    $psi.WorkingDirectory = $RepoRoot
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.CreateNoWindow = $true
    $psi.EnvironmentVariables["PYTHONPATH"] = $RepoRoot
    $psi.EnvironmentVariables["ARIFOS_MINIMAL_STDIO"] = "1"

    $proc = New-Object System.Diagnostics.Process
    $proc.StartInfo = $psi

    if (-not $proc.Start()) {
        throw "Failed to start arifOS MCP process."
    }

    try {
        foreach ($frame in @($initializeFrame, $initializedNotification, $RequestFrame)) {
            $proc.StandardInput.WriteLine((ConvertTo-CompactJson -Value $frame))
        }
        $proc.StandardInput.Close()

        $stdoutTask = $proc.StandardOutput.ReadToEndAsync()
        $stderrTask = $proc.StandardError.ReadToEndAsync()

        if (-not $proc.WaitForExit($TimeoutSeconds * 1000)) {
            try {
                $proc.Kill()
            }
            catch {
            }
            throw "Timed out waiting for MCP response after $TimeoutSeconds seconds."
        }

        $stdout = $stdoutTask.GetAwaiter().GetResult()
        $stderr = $stderrTask.GetAwaiter().GetResult()

        $frames = @()
        $parseErrors = @()

        foreach ($line in ($stdout -split "`r?`n")) {
            if ([string]::IsNullOrWhiteSpace($line)) {
                continue
            }

            try {
                $frames += ,($line | ConvertFrom-Json -Depth 100)
            }
            catch {
                $parseErrors += ,([ordered]@{
                    line = $line
                    error = $_.Exception.Message
                })
            }
        }

        $requestId = $RequestFrame.id
        $initResponse = $null
        $requestResponse = $null

        foreach ($frame in $frames) {
            if ($null -ne $frame.id -and $frame.id -eq 1) {
                $initResponse = $frame
            }
            if ($null -ne $frame.id -and $frame.id -eq $requestId) {
                $requestResponse = $frame
            }
        }

        $decodedTextJson = $null
        if ($null -ne $requestResponse -and $null -ne $requestResponse.result -and $null -ne $requestResponse.result.content) {
            foreach ($contentBlock in $requestResponse.result.content) {
                if ($contentBlock.type -eq "text" -and -not [string]::IsNullOrWhiteSpace($contentBlock.text)) {
                    try {
                        $decodedTextJson = $contentBlock.text | ConvertFrom-Json -Depth 100
                    }
                    catch {
                    }
                    break
                }
            }
        }

        return [pscustomobject]@{
            ok = ($null -ne $requestResponse -and $null -eq $requestResponse.error)
            init = $initResponse
            response = $requestResponse
            decodedTextJson = $decodedTextJson
            stderr = $stderr.Trim()
            parseErrors = $parseErrors
            rawStdout = $stdout
        }
    }
    finally {
        if (-not $proc.HasExited) {
            try {
                $proc.Kill()
            }
            catch {
            }
        }
        $proc.Dispose()
    }
}

$requestFrame = Build-RequestFrame
$result = Invoke-ArifosMcp -RequestFrame $requestFrame

if ($RawFrames) {
    $result | ConvertTo-Json -Depth 100
}
elseif ($null -ne $result.decodedTextJson) {
    $result.decodedTextJson | ConvertTo-Json -Depth 100
}
elseif ($null -ne $result.response) {
    $result.response | ConvertTo-Json -Depth 100
}
else {
    $result | ConvertTo-Json -Depth 100
}
