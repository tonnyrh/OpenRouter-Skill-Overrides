Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$claudeRoot = Join-Path $env:USERPROFILE ".claude"
$claudeSkills = Join-Path $claudeRoot "skills"
$claudeCommands = Join-Path $claudeRoot "commands"

$skills = @(
    "openrouter-glm52",
    "openrouter-heavy-task-gate",
    "openrouter-model-advisor",
    "flux2pro"
)

foreach ($skill in $skills) {
    $source = Join-Path $repoRoot "skills\$skill"
    $target = Join-Path $claudeSkills $skill

    if (-not (Test-Path -LiteralPath $source)) {
        throw "Missing source skill: $source"
    }

    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force
    Write-Host "Synced $skill -> $target"
}

New-Item -ItemType Directory -Force -Path $claudeCommands | Out-Null
Copy-Item -Path (Join-Path $repoRoot "claude\commands\*.md") -Destination $claudeCommands -Force
Write-Host "Synced Claude commands -> $claudeCommands"

Write-Host "Claude Code OpenRouter custom skills and commands are in sync."
