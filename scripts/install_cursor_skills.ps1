<#
.SYNOPSIS
    Install OpenRouter skills into the global Cursor personal skills directory.

.DESCRIPTION
    Wrapper around scripts/sync.py --tool cursor.
    Copies canonical skills from skills/* into %USERPROFILE%\.cursor\skills\*
    so OpenRouter helpers are discoverable from any Cursor workspace.

.EXAMPLE
    .\scripts\install_cursor_skills.ps1
#>

$RepoRoot = Split-Path $PSScriptRoot -Parent
$Sync = Join-Path $RepoRoot "scripts\sync.py"

if (-not (Test-Path $Sync)) {
    Write-Error "Missing sync script: $Sync"
    exit 1
}

$args = @($Sync, "--tool", "cursor")
python @args
exit $LASTEXITCODE
