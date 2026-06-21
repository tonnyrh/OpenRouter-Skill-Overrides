param(
    [switch]$LiveGlm
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$claudeRoot = Join-Path $env:USERPROFILE ".claude"
$claudeSkills = Join-Path $claudeRoot "skills"

$pythonFiles = @(
    (Join-Path $repoRoot "skills\openrouter-glm52\scripts\call_glm52.py"),
    (Join-Path $repoRoot "skills\openrouter-model-advisor\scripts\recommend_model.py"),
    (Join-Path $claudeSkills "openrouter-glm52\scripts\call_glm52.py"),
    (Join-Path $claudeSkills "openrouter-model-advisor\scripts\recommend_model.py")
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

python (Join-Path $claudeSkills "openrouter-model-advisor\scripts\recommend_model.py") `
    --task "Second-pass review of a large coding task in a local repository" `
    --mode coding `
    --priority balanced `
    --limit 2

if ($LiveGlm) {
    python (Join-Path $claudeSkills "openrouter-glm52\scripts\call_glm52.py") `
        --max-tokens 300 `
        "Answer only with: OK"
}
