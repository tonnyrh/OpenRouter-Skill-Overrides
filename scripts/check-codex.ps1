param(
    [switch]$LiveGlm
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$codexSkills = Join-Path $env:USERPROFILE ".codex\skills"

$pythonFiles = @(
    (Join-Path $repoRoot "skills\openrouter-glm52\scripts\call_glm52.py"),
    (Join-Path $repoRoot "skills\openrouter-model-advisor\scripts\recommend_model.py"),
    (Join-Path $repoRoot "skills\openrouter-flux2-pro\scripts\generate_flux2_pro.py"),
    (Join-Path $codexSkills "openrouter-glm52\scripts\call_glm52.py"),
    (Join-Path $codexSkills "openrouter-model-advisor\scripts\recommend_model.py"),
    (Join-Path $codexSkills "openrouter-flux2-pro\scripts\generate_flux2_pro.py")
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

$advisorScript = Join-Path $codexSkills "openrouter-model-advisor\scripts\recommend_model.py"

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
    python (Join-Path $codexSkills "openrouter-glm52\scripts\call_glm52.py") `
        --max-tokens 300 `
        "Svar kun med: OK"
}
