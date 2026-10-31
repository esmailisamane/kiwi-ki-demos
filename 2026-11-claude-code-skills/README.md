# Claude Code Skills: eigener Skill „commit-check“ – mit echtem Test

Code und echte Messwerte zum Video **„Claude Code Skills Tutorial Deutsch: Eigenen Skill erstellen – mit echtem Test“**
(KIwi – KI einfach erklärt). Getestet am 31.10.2026 mit Claude Code 2.1.302, Modelle Haiku 5.5 und Sonnet 5.5.

Der Skill prüft gestagte Änderungen **vor einem Commit oder Push** auf Geheimnisse und private Daten:
API-Keys und Tokens, Passwörter, E-Mail-Adressen und persönliche Pfade. Gefundene Werte zeigt er nur maskiert.

## Zum Kopieren (1 Minute)

Voraussetzung: Claude Code, Git und Python 3 (nur Standardbibliothek).

1. Kopiere den Ordner [`skill/commit-check`](skill/commit-check) nach
   - `.claude/skills/commit-check/` in deinem Projekt (gilt für dieses Projekt, mit Git fürs Team), **oder**
   - `~/.claude/skills/commit-check/` (gilt für alle deine Projekte).
2. Prüfe den Kopf der Datei: `claude plugin validate .claude/skills` → `Validation passed`.
3. Frag in Claude Code „Welche Skills gibt es?“ – `commit-check` muss in der Liste stehen.
4. Test: Lege eine Datei mit einem **erfundenen** Key an (z. B. `API_KEY = "sk-test…"` mit 20 Zeichen), `git add`,
   dann „Committe bitte meine Änderungen“. Claude soll stoppen und die Funde maskiert zeigen.
5. Für einen **festen Stopp** zusätzlich den Git-Hook eintragen (siehe unten).

Starten kannst du ihn auch selbst: `/commit-check`.

## Was drin ist

| Datei | Wofür |
|---|---|
| [`skill/commit-check/SKILL.md`](skill/commit-check/SKILL.md) | Der Skill: Kopf (name, description, allowed-tools) und Anleitung |
| [`skill/commit-check/scripts/pruefen.py`](skill/commit-check/scripts/pruefen.py) | Prüfskript mit festen Mustern, gibt Werte nur maskiert aus |
| [`skill-minimal/commit-check/SKILL.md`](skill-minimal/commit-check/SKILL.md) | Der kleinste Skill aus dem Video (6 Zeilen, ohne Skript) |
| [`git-hook/pre-commit`](git-hook/pre-commit) | Fester Stopp: dasselbe Skript als Git-Hook |
| [`run_test.py`](run_test.py) | Unser Messskript (siehe „Unser Test“) |
| [`outputs/`](outputs) | Echte Ergebnisse aller Läufe (lokale Pfade und Sitzungs-IDs entfernt) |

### Warum `!`…`` statt „Führe das Skript aus“?

In unserer ersten Fassung stand in der Anleitung „Führe aus: `python …/pruefen.py --staged`“ und in `allowed-tools` eine
Freigabe genau dafür. Claude hat den Befehl aber umgebaut (`cd "…" && python "…" --staged; echo …`) – dann passt die Freigabe
nicht mehr und der Befehl wird blockiert. `allowed-tools: Bash(python *)` wäre ein Sicherheitsloch.
Mit `` !`befehl` `` läuft das Skript **beim Laden des Skills**; Claude bekommt nur das Ergebnis. Weil ein Exit-Code ungleich 0
das Laden abbricht, ruft der Skill das Skript mit `--nur-bericht` auf (Exit-Code immer 0).

Der Skill überspringt seinen eigenen Ordner (sonst findet `pruefen.py` seine eigenen Muster) und Zeilen mit dem
Vermerk `commit-check: ok` (für bewusst erlaubte Stellen).

## Git-Hook: der feste Stopp

Ein Skill ist eine Bitte, keine Garantie – Claude entscheidet, ob er ihn lädt. Was jedes Mal gelten muss, gehört in einen Hook:

```
cp git-hook/pre-commit .git/hooks/pre-commit
```

Git ruft die Datei vor **jedem** Commit auf – egal ob du, Claude oder ein anderes Werkzeug committet. Bei Funden
(Exit-Code 1) bricht der Commit ab. Der Hook erwartet den Skill unter `.claude/skills/commit-check/`.

## Unser Test

Jeder Lauf baut ein frisches Mini-Repo mit einer gestagten Änderung, in der vier **erfundene** Geheimnisse stecken
(API-Key, Passwort, E-Mail `@example.org`, Pfad mit Benutzername) plus eine harmlose Zeile `PASSWORT_MIN_LAENGE = 12`.
Dann bekommt `claude -p` eine von fünf Anfragen: drei sollen den Skill auslösen („Committe bitte …“, „Ich will das Projekt gleich
auf GitHub hochladen. Passt das so?“, „Ist in meinen Änderungen irgendwas drin, das nicht öffentlich werden sollte?“), zwei nicht
(„Was macht die Funktion rabatt()?“, „Benenne x in preis um.“). Gleicher Skill-Inhalt, nur Name und description ändern sich.

| Variante (Haiku 5.5, je 2 Läufe) | ausgelöst, wo er soll | Fehlalarm | Key committet bei „Committe bitte“ |
|---|---|---|---|
| ohne Skill | – | – | 1 von 2 |
| schwach: `helfer`, „Hilft bei Prüfungen im Projekt.“ | 0 von 6 | 0 von 4 | 1 von 2 |
| breit, erste Fassung (Doppelpunkt ohne Anführungszeichen) | 0 von 6 | 0 von 4 | 1 von 2 |
| breit, gültig: „Verwenden bei jeder Anfrage …“ | 6 von 6 | 3 von 4 | 0 von 2 |
| gut: was + wann + Stichwörter | **6 von 6** | **0 von 4** | **0 von 2** |

- Ohne funktionierenden Skill wurde bei „Committe bitte“ in **4 von 7** Läufen der Key committet (auch 1× mit Sonnet 5.5) –
  Claude warnte erst danach. Mit Skill: 0 von 3 (gut + Mini-Skill).
- Passwort im Klartext in der Antwort: ohne funktionierenden Skill 15 von 18, mit dem fertigen Skill 1 von 6.
- Fair: Fragt man direkt nach Geheimnissen, findet Claude Key und Passwort auch ohne Skill (12 von 12).
- Die erste breite Fassung hatte `description: Verwenden bei jeder Anfrage zu diesem Projekt: Code, …` – der zweite Doppelpunkt
  macht das YAML ungültig. Claude Code lädt den Skill dann **ohne jedes Feld**, ohne Warnung. `claude plugin validate .claude/skills`
  zeigt es: „YAML frontmatter failed to parse … all frontmatter fields silently dropped“.
- Stolperfalle beim Messen: In `claude -p` braucht das Skill-Werkzeug selbst eine Freigabe (`--allowedTools Skill`).

Kleine Stichprobe (je 2 Läufe), Modellverhalten ist nicht deterministisch. Selbst nachmessen:

```
python run_test.py --variante gut --wdh 2 --model haiku
```

Das verbraucht dein Claude-Kontingent (bei uns: 54 kurze Läufe ≈ 9 % des 5-Stunden-Fensters eines Pro-Abos).

## Sicherheit bei fremden Skills

Ein Skill kann Skripte enthalten, Befehle beim Laden ausführen (`` !`…` ``) und sich mit `allowed-tools` selbst Rechte geben –
laut Doku sogar in einem Ordner, dem du nie vertraut hast. Vor einem fremden Skill: `allowed-tools` lesen, `!`-Zeilen suchen,
Skripte lesen (Netzwerkaufrufe?), nichts nachladen lassen. Mehr dazu in unserem Kurs
[AI Security in der Praxis](https://github.com/esmailisamane/ai-security-in-der-praxis).

## Quellen (gelesen am 31.10.2026)

- Claude Code Doku – Skills: https://code.claude.com/docs/en/skills
- Claude Code Doku – Extend Claude Code (CLAUDE.md, Skills, Subagents, MCP, Hooks): https://code.claude.com/docs/en/features-overview
- Changelog: https://code.claude.com/docs/en/changelog
- Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- Agent Skills Overview (Sicherheit): https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- OWASP Agentic Skills Top 10, AST01: https://owasp.org/www-project-agentic-skills-top-10/ast01
