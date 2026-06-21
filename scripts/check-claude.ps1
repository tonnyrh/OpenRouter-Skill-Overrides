param(
    [switch]$LiveGlm,
    [switch]$LiveFlux
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$claudeRoot = Join-Path $env:USERPROFILE ".claude"
$claudeSkills = Join-Path $claudeRoot "skills"

$pythonFiles = @(
    (Join-Path $repoRoot "skills\openrouter-glm52\scripts\call_glm52.py"),
    (Join-Path $repoRoot "skills\openrouter-model-advisor\scripts\recommend_model.py"),
    (Join-Path $repoRoot "skills\flux2pro\scripts\generate_flux.py"),
    (Join-Path $claudeSkills "openrouter-glm52\scripts\call_glm52.py"),
    (Join-Path $claudeSkills "openrouter-model-advisor\scripts\recommend_model.py"),
    (Join-Path $claudeSkills "flux2pro\scripts\generate_flux.py")
)

$script = @"
import ast
from pathlib import Path
paths = $($pythonFiles | ConvertTo-Json)
if isinstance(paths, str):
    paths = [paths]
for path in paths:
    ast.parse(Path(path).read_text(encoding="utf-8"))
    print(f"syntax OK: {path}")
"@

$script | python -

$advisorScript = Join-Path $claudeSkills "openrouter-model-advisor\scripts\recommend_model.py"

python $advisorScript `
    --task "Second-pass review of a large coding task in a local repository" `
    --mode coding `
    --priority balanced `
    --limit 2

$cheap = python $advisorScript `
    --task "Draft a cheap short changelog summary" `
    --mode text `
    --priority cost `
    --limit 2 | ConvertFrom-Json

if ($cheap.recommended_model.quality_tier -eq "premium" -or $cheap.requires_confirmation) {
    throw "Cost routing regression: expected a non-premium choice without confirmation."
}

$numberQuest = python $advisorScript `
    --task "Generate final NumberQuest game assets with precise style" `
    --project NumberQuest `
    --current-model black-forest-labs/flux.2-pro `
    --mode image `
    --priority balanced `
    --limit 2 | ConvertFrom-Json

if ($numberQuest.recommended_model.id -ne "openai/gpt-5-image" -or -not $numberQuest.requires_confirmation) {
    throw "NumberQuest routing regression: expected GPT-5 Image with switch confirmation."
}

Write-Host "advisor policy OK: cheap routing and NumberQuest switch gate"

if ($LiveGlm) {
    python (Join-Path $claudeSkills "openrouter-glm52\scripts\call_glm52.py") `
        --max-tokens 300 `
        "Answer only with: OK"
}

if ($LiveFlux) {
    $fluxOutput = Join-Path $env:TEMP "claude-flux2pro-live-check.png"
    python (Join-Path $claudeSkills "flux2pro\scripts\generate_flux.py") `
        "Tiny blue dot centered on a white background" `
        --aspect-ratio 1:1 `
        --image-size 0.5K `
        --seed 7 `
        --output $fluxOutput

    if (-not (Test-Path -LiteralPath $fluxOutput)) {
        throw "FLUX live check did not create $fluxOutput"
    }
    Write-Host "FLUX live check OK: $fluxOutput"
}
