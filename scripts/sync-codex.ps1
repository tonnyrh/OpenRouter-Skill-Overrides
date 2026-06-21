Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$codexSkills = Join-Path $env:USERPROFILE ".codex\skills"

$skills = @(
    "openrouter-glm52",
    "openrouter-heavy-task-gate",
    "openrouter-model-advisor"
)

foreach ($skill in $skills) {
    $source = Join-Path $repoRoot "skills\$skill"
    $target = Join-Path $codexSkills $skill

    if (-not (Test-Path -LiteralPath $source)) {
        throw "Missing source skill: $source"
    }

    New-Item -ItemType Directory -Force -Path $target | Out-Null
    Copy-Item -Path (Join-Path $source "*") -Destination $target -Recurse -Force
    Write-Host "Synced $skill -> $target"
}

Write-Host "Codex OpenRouter custom skills are in sync."
