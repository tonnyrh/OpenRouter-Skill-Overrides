# OpenRouter Skill Overrides

Dette prosjektet er source of truth for lokale OpenRouter skill-tilpasninger brukt av Codex og Claude Code. Det skal holdes adskilt fra upstream-repoet `https://github.com/OpenRouterTeam/skills`.

Status per 2026-06-21:

- `C:\vscode\OpenRouter-Skill-Overrides` er foreløpig ikke et git-repo. Det finnes ingen lokal branch eller remote å sammenligne mot.
- Upstream OpenRouter-skills er installert i Codex under `C:\Users\TonnyRogerHolm(Test)\.codex\skills\openrouter-*`.
- Lokale custom-skills spores her under `skills\`.
- `openrouter-glm52` og `openrouter-heavy-task-gate` i dette prosjektet matcher de aktive Codex-skillene på `SKILL.md`-nivå.
- `openrouter-model-advisor` er lagt inn her fordi den er lokal beslutningslogikk over upstream modellmetadata og prosjektpreferanser.
- `skills\openrouter-glm52\scripts\call_glm52.py` og den aktive Codex-kopien har `content is None`-fiksen.

## Hva som er upstream

Disse skillene kommer fra `OpenRouterTeam/skills` og bør normalt oppdateres via upstream-installasjon, ikke redigeres lokalt:

- `openrouter-models`
- `openrouter-generations`
- `openrouter-typescript-sdk`
- andre offisielle OpenRouter-skills med `metadata.github-repo: https://github.com/OpenRouterTeam/skills`

Hvis upstream endrer script, modelldata eller skill-beskrivelser, bør de installeres på nytt i Codex i stedet for å kopieres manuelt inn her.

## Hva som er lokalt

Lokale tilpasninger som bør spores i dette prosjektet:

- `skills\openrouter-glm52`: enkel GLM 5.2-kaller via OpenRouter.
- `skills\openrouter-heavy-task-gate`: beslutningsport som spør før Codex bruker OpenRouter på tunge oppgaver.
- `skills\openrouter-model-advisor`: dynamisk modellrådgiver som kombinerer live OpenRouter-data, lokal modellnotatfil og prosjektpreferanser.
- `commands\`: Claude Code-kommandoer. Disse er relevante for Claude Code, ikke Codex direkte.
- `Claude-openrouter-glm52-ReadMe.md`: eldre Claude Code-notat. Bruk denne `README.md` som prosjektets hovedoversikt.

## Beslutningsflyt for OpenRouter

Målet er at OpenRouter hjelper når det faktisk gir verdi, uten å forstyrre vanlig kodearbeid.

1. Codex bruker lokal analyse først.
2. `openrouter-heavy-task-gate` slår inn på tunge, risikable eller tverrgående oppgaver.
3. Før penger brukes eller prosjektkontekst sendes ut, spør Codex kort om GLM 5.2/OpenRouter skal brukes som second pass.
4. Når modellvalget er uklart, brukes `openrouter-model-advisor` til live oppslag mot OpenRouter-modell-API-et.
5. Rådgiveren skal foreslå én anbefalt modell og få alternativer, ikke en lang modellkatalog.
6. Dyre/premium modeller eller modellbytte i et prosjekt skal bekreftes før bruk.
7. Når brukeren allerede har godkjent OpenRouter-bruk gjennom gate, kan `--allow-premium-without-confirmation` brukes for å unngå dobbeltspørsmål der GLM 5.2 er normalvalget.

Praktisk standard:

```powershell
python "$env:USERPROFILE\.codex\skills\openrouter-model-advisor\scripts\recommend_model.py" --task "Second-pass review of a large coding task in a local repository" --mode coding --priority balanced
```

For faktisk second pass etter godkjenning er lokal default:

```powershell
python "$env:USERPROFILE\.codex\skills\openrouter-glm52\scripts\call_glm52.py" --reasoning-effort high --max-tokens 3000 "<fokusert prompt>"
```

## Codex workflow

Rediger skills i dette repoet, ikke direkte under `.codex\skills`.

Synkroniser lokale custom-skills til aktiv Codex-installasjon:

```powershell
cd C:\vscode\OpenRouter-Skill-Overrides
.\scripts\sync-codex.ps1
```

Kjør en rask Codex-sjekk uten GLM-kostnad:

```powershell
.\scripts\check-codex.ps1
```

Kjør samme sjekk med en minimal GLM 5.2 live-test:

```powershell
.\scripts\check-codex.ps1 -LiveGlm
```

`check-codex.ps1` bruker `ast.parse` for Python-syntaks slik at den ikke trenger å skrive `__pycache__` under `.codex\skills`.

## Modellvalg

Standard tekst/koding/long-context:

- `z-ai/glm-5.2`
- brukes for repoanalyse, refaktor-review, migrasjonsplaner, testfeil med uklar årsak og større arkitekturspørsmål

Når live modelloppslag bør brukes:

- modellen kan ha endret pris, kontekstlengde, modalitet eller tilgjengelighet
- oppgaven er bilde, vision, lyd, video eller krever spesielle OpenRouter-parametre
- et prosjekt har en kjent nåværende modell og et bytte kan være aktuelt
- brukeren spør etter beste, billigste eller raskeste modell nå

Når live modelloppslag ikke bør brukes:

- små lokale kodeendringer
- enkel dokumentasjon
- allerede eksplisitt valgt modell
- når heavy-task-gate allerede har valgt normal GLM 5.2 second pass og det ikke finnes prosjektspesifikke krav

## Kjente avvik

- `C:\vscode\OpenRouter-Skill-Overrides` er ikke initialisert som git-repo.
- `skills\openrouter-glm52\scripts\call_glm52.py` skiller seg fra aktiv Codex-kopi bare på klientmetadata:
  - prosjektkopien bruker Claude Code headers
  - aktiv Codex-kopi bruker Codex headers
- begge kopier har `None`-safe output hvis OpenRouter returnerer `content: null`
- `openrouter-model-advisor` finnes nå både i prosjektkopien og som aktiv Codex-skill under `.codex\skills`.

## Anbefalt neste ryddegrep

Når du er klar for branch/repo:

```powershell
cd C:\vscode\OpenRouter-Skill-Overrides
git init
git add README.md skills commands Claude-openrouter-glm52-ReadMe.md
git commit -m "Track local OpenRouter skill customizations"
```

Deretter kan vi lage en egen branch for Codex-tilpasninger og eventuelt skille Claude Code-kommandoene ut i egen mappe eller repo.
