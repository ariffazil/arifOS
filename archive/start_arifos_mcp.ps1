# arifOS MCP Launcher with Credential Manager Integration
# Loads GitHub token from Windows Credential Manager

# Function to get credential from Windows Credential Manager
function Get-StoredCredential {
    param([string]$Target)
    
    try {
        Add-Type -AssemblyName System.Security
        $cred = [System.Net.NetworkCredential]::new()
        
        # Use cmdkey to check if credential exists
        $result = cmdkey /list:$Target 2>&1
        if ($LASTEXITCODE -eq 0) {
            # Credential exists, try to load it using Windows API
            $sig = @'
[DllImport("Advapi32.dll", SetLastError = true, EntryPoint = "CredReadW", CharSet = CharSet.Unicode)]
public static extern bool CredRead(string target, int type, int reservedFlag, out IntPtr credentialPtr);
'@
            $CredReadType = Add-Type -MemberDefinition $sig -Name "CredManager" -Namespace "PsUtils" -PassThru -ErrorAction SilentlyContinue
            
            [IntPtr]$credPtr = [IntPtr]::Zero
            $success = $CredReadType::CredRead($Target, 1, 0, [ref]$credPtr)
            
            if ($success) {
                $credStruct = [System.Runtime.InteropServices.Marshal]::PtrToStructure($credPtr, [Type]([PSCustomObject]@{
                    Flags = [UInt32]
                    Type = [UInt32]
                    TargetName = [IntPtr]
                    Comment = [IntPtr]
                    LastWritten = [Int64]
                    CredentialBlobSize = [UInt32]
                    CredentialBlob = [IntPtr]
                    Persist = [UInt32]
                    AttributeCount = [UInt32]
                    Attributes = [IntPtr]
                    TargetAlias = [IntPtr]
                    UserName = [IntPtr]
                }.GetType()))
                
                if ($credStruct.CredentialBlobSize -gt 0) {
                    $password = [System.Runtime.InteropServices.Marshal]::PtrToStringUni($credStruct.CredentialBlob, $credStruct.CredentialBlobSize / 2)
                    return $password
                }
            }
        }
    } catch {
        Write-Host "[ERROR] Failed to load credential: $_" -ForegroundColor Red
    }
    
    return $null
}

# Load GitHub token from Credential Manager
Write-Host "[arifOS MCP] Loading GitHub token from Windows Credential Manager..." -ForegroundColor Cyan
$token = Get-StoredCredential -Target "arifos_github_token"

if ($token) {
    $env:GITHUB_TOKEN = $token
    $env:GITHUB_PERSONAL_ACCESS_TOKEN = $token
    Write-Host "[arifOS MCP] Token loaded successfully." -ForegroundColor Green
} else {
    Write-Host "[WARNING] GitHub token not found in Credential Manager." -ForegroundColor Yellow
    Write-Host "[WARNING] GitHub MCP may not work properly." -ForegroundColor Yellow
}

# Set Python path
$env:PYTHONPATH = "C:\Users\User\OneDrive\Documents\GitHub\arifOS"

# Launch arifOS MCP server
Write-Host "[arifOS MCP] Starting MCP server..." -ForegroundColor Cyan
& "C:\Users\User\AppData\Local\Programs\Python\Python314\python.exe" "C:\Users\User\OneDrive\Documents\GitHub\arifOS\arifos_mcp_entry.py"