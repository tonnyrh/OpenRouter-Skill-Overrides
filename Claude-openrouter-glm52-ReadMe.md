# Claude Code — OpenRouter / GLM 5.2 oppsett

Denne mappen inneholder bruker-nivå tilpasninger for [Claude Code](https://claude.ai/code) med støtte for å sende tunge oppgaver til **GLM 5.2** via [OpenRouter](https://openrouter.ai).

---

## Mappestruktur

```
~/.claude/
├── Claude-openrouter-glm52-ReadMe.md                        ← denne filen
│
├── openrouter-skills/               ← git-klon av OpenRouterTeam/skills (upstream, urørt)
│   └── skills/
│       ├── openrouter-models/
│       ├── openrouter-generations/
│       ├── openrouter-typescript-sdk/
│       └── ... (14 offisielle skills)
│
├── skills/                          ← custom skills (ikke i upstream)
│   ├── openrouter-glm52/
│   │   ├── SKILL.md                 ← kontekst og bruksanvisning for Claude
│   │   ├── scripts/
│   │   │   └── call_glm52.py        ← Python-script som kaller OpenRouter API
│   │   └── references/
│   │       └── openrouter-usage.md  ← API-mønstre og SDK-eksempler
│   └── openrouter-heavy-task-gate/
│       └── SKILL.md                 ← beslutningslogikk: når skal GLM brukes?
│
└── commands/                        ← Claude Code slash-kommandoer (globale)
    ├── glm52.md                     ← /glm52  — send prompt direkte til GLM 5.2
    └── heavy-task-gate.md           ← /heavy-task-gate — beslutningsport
```

> **Merk:** `~/.codex/` og `~/.claude/` er helt adskilte. De deler ingen filer og kan oppdateres uavhengig av hverandre.

---

## Hva er tilpasset vs. upstream

| Komponent | Kilde | Kan oppdateres fra upstream |
|---|---|---|
| `openrouter-skills/` | `github.com/OpenRouterTeam/skills` (git-klon) | Ja — `git pull` |
| `skills/openrouter-glm52/` | Custom (Codex-generert, ikke i upstream) | Nei — vedlikeholdes manuelt |
| `skills/openrouter-heavy-task-gate/` | Custom | Nei — vedlikeholdes manuelt |
| `commands/glm52.md` | Custom | Nei |
| `commands/heavy-task-gate.md` | Custom | Nei |

### Tilpasninger i `call_glm52.py`

Filen er basert på en Codex-generert versjon. Følgende endringer er gjort i forhold til originalversjonen:

- **Null-fix:** `print(content if content is not None else "")` — GLM 5.2 returnerer av og til `"content": null` (JSON) ved reasoning-tokens. Originalens `print(content)` ville skrevet ut den bokstavelige strengen `None`.
- **HTTP-Referer:** endret fra `https://openai.com/codex` til `https://claude.ai/code` for å reflektere riktig klient i OpenRouter-dashbordet.
- **X-Title:** endret til `Claude Code OpenRouter GLM 5.2 Skill`.

---

## Forutsetninger

| Krav | Versjon | Sjekk |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Git | Valgfri, trengs for `git pull`-oppdateringer | `git --version` |
| Claude Code | Siste versjon | `claude --version` |
| `OPENROUTER_API_KEY` | Nøkkel fra openrouter.ai | Se under |

### Sett API-nøkkel

Sett nøkkelen permanent i Windows bruker-miljøet (én gang):

```powershell
[System.Environment]::SetEnvironmentVariable("OPENROUTER_API_KEY", "sk-or-...", "User")
```

Eller midlertidig for gjeldende sesjon:

```powershell
$env:OPENROUTER_API_KEY = "sk-or-..."
```

---

## Installasjon (førstegangsoppsett)

### 1. Klon upstream OpenRouter-skills

```powershell
git clone https://github.com/OpenRouterTeam/skills "$env:USERPROFILE\.claude\openrouter-skills"
```

### 2. Opprett custom skills-mappe

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\openrouter-glm52\scripts"
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\openrouter-glm52\references"
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\openrouter-heavy-task-gate"
```

### 3. Kopier custom skill-filer

Kopier følgende filer fra dette repoet (eller fra `~/.codex/skills/openrouter-glm52/` hvis Codex er installert):

| Fra | Til |
|---|---|
| `call_glm52.py` | `~/.claude/skills/openrouter-glm52/scripts/call_glm52.py` |
| `SKILL.md` (glm52) | `~/.claude/skills/openrouter-glm52/SKILL.md` |
| `openrouter-usage.md` | `~/.claude/skills/openrouter-glm52/references/openrouter-usage.md` |
| `SKILL.md` (heavy-task-gate) | `~/.claude/skills/openrouter-heavy-task-gate/SKILL.md` |

### 4. Opprett Claude Code commands-mappe og kommandofiler

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\commands"
```

Kopier `commands/glm52.md` og `commands/heavy-task-gate.md` til `~/.claude/commands/`.

### 5. Verifiser

```powershell
python "$env:USERPROFILE\.claude\skills\openrouter-glm52\scripts\call_glm52.py" --max-tokens 20 "Say: OK"
```

Forventet output: `OK`

---

## Bruk

### `/glm52` — direkte kall til GLM 5.2

```
/glm52 Hva er risikoen med denne migrasjonen?
```

```
/glm52 --reasoning-effort xhigh <kompleks arkitekturspørsmål>
```

Større kontekst kan pipes inn — Claude Code samler relevant kode, diff eller feilmeldinger og sender det til modellen.

### `/heavy-task-gate` — automatisk beslutningsport

Aktiveres av Claude Code selv (eller manuelt) når en oppgave ser tung ut. Claude spør:

> *Denne oppgaven er tung nok til at GLM 5.2 kan være nyttig som second pass. Vil du at jeg kjører /glm52 på relevant kontekst før jeg implementerer?*

Svar `ja` → relevant kontekst sendes til GLM 5.2, svaret brukes som input til implementasjonen.  
Svar `nei` → Claude Code fortsetter uten OpenRouter.

**Hva teller som "tungt":**
- Arkitekturavgjørelser eller migrasjonsplaner
- Refaktorering på tvers av flere moduler eller tjenester
- Vanskelige bugs der lokale bevis er uklare
- CI/test-feil med flere mulige rotårsaker
- Produksjon, deploy, database, autentisering, sikkerhet eller datarisikooppgaver
- Ytelse, parallellitet, caching eller distribuerte systemer

---

## Oppdatering

### Offisielle OpenRouter-skills (upstream)

```powershell
git -C "$env:USERPROFILE\.claude\openrouter-skills" pull
```

Dette oppdaterer alle 14 offisielle skills (models, generations, typescript-sdk, osv.) uten å røre custom skills eller kommandoer.

### Custom skills (`openrouter-glm52`, `openrouter-heavy-task-gate`)

Disse finnes **ikke** i upstream-repoet. De vedlikeholdes manuelt i `~/.claude/skills/`. Sammenlign gjerne med `~/.codex/skills/` for å se om Codex-versjonen har blitt endret.

```powershell
# Vis forskjell mellom Codex-versjon og Claude-versjon av call_glm52.py
git diff --no-index `
    "$env:USERPROFILE\.codex\skills\openrouter-glm52\scripts\call_glm52.py" `
    "$env:USERPROFILE\.claude\skills\openrouter-glm52\scripts\call_glm52.py"
```

---

## Separasjon mellom Codex og Claude Code

| | Codex CLI (`~/.codex/`) | Claude Code (`~/.claude/`) |
|---|---|---|
| Skills-kilde | `gh skill install OpenRouterTeam/skills` | `git clone` + manuelt |
| Offisielle skills | `~/.codex/skills/openrouter-{models,generations,...}/` | `~/.claude/openrouter-skills/skills/` |
| GLM 5.2 script | `~/.codex/skills/openrouter-glm52/scripts/call_glm52.py` | `~/.claude/skills/openrouter-glm52/scripts/call_glm52.py` |
| Kommandoer | Codex skill-system | `~/.claude/commands/*.md` |
| Oppdatering | `gh skill install ... --scope user` | `git pull` (upstream) / manuelt (custom) |

De to installasjonene deler ingen filer og kan operere helt uavhengig.
