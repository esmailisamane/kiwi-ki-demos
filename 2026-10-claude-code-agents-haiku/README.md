# Claude Code Agents: Subagents mit Haiku 5.5 im echten Test

Code und echte Ergebnisse zum Video **„Claude Code Agents Tutorial Deutsch: Subagents mit Haiku 5.5 im echten Test“**
(Kanal KIwi – KI einfach erklärt). Kein offizielles Projekt von Anthropic.

Die Idee: Wir haben in einem kleinen Python-Shop **36 Fehler versteckt** (18 Dateien, 2 Fehler pro Datei, alle 14 Tests
grün) und fünf Teams danach suchen lassen. Mal ein Modell allein, mal ein Chef mit Subagents.

Getestet am 12.10.2026 mit Claude Code 2.1.296 unter Windows 11, Claude Pro. Modelle: Sonnet 5.5 und Haiku 5.5.

## Ergebnis

| Runde | Team | Zeit (Mittel aus 3) | Verbrauch* (Mittel aus 3) | gefundene Fehler je Lauf |
|---|---|---|---|---|
| 6 Dateien, 12 Fehler | Sonnet 5.5 allein | 15,9 s | 4,56 Cent | 12, 12, 12 |
| 6 Dateien, 12 Fehler | Haiku 5.5 allein | 25,2 s | 0,43 Cent | 12, 12, 12 |
| 6 Dateien, 12 Fehler | Sonnet-Chef + 3 Haiku-Subagents | 21,3 s | 4,73 Cent | 12, 12, 12 |
| 6 Dateien, 12 Fehler | Sonnet-Chef + 3 Sonnet-Subagents | 20,8 s | 8,45 Cent | 12, 12, 12 |
| 6 Dateien, 12 Fehler | Haiku-Chef + 3 Haiku-Subagents | 19,8 s | 0,66 Cent | 12, 12, 12 |
| 18 Dateien, 36 Fehler | Sonnet 5.5 allein | 38,8 s | 11,95 Cent | 36, 36, 36 |
| 18 Dateien, 36 Fehler | Haiku 5.5 allein | 40,3 s | 0,83 Cent | 35, 35, 34 |
| 18 Dateien, 36 Fehler | Sonnet-Chef + 6 Haiku-Subagents | 31,7 s | 10,57 Cent (davon Subagents: 0,90) | 36, 35, 34 |
| 18 Dateien, 36 Fehler | Sonnet-Chef + 6 Sonnet-Subagents | 31,0 s | 20,57 Cent | 36, 36, 36 |
| 18 Dateien, 36 Fehler | Haiku-Chef + 6 Haiku-Subagents | 29,5 s | 1,24 Cent | 34, 36, 36 |

\* Rechnerischer API-Listenpreis in US-Cent, so wie Claude Code ihn je Lauf ausgibt (`total_cost_usd`). Im Abo wird das
nicht einzeln berechnet. Die Zahl zeigt, wie viel ein Lauf verbraucht. Wie das Abo Haiku gegen Sonnet gewichtet, haben wir
in keiner offiziellen Quelle gefunden.

Was wir daraus mitnehmen:

1. Kleine Aufgabe: Subagents bringen nichts. Sie waren langsamer als Sonnet allein und nicht günstiger.
2. Große Aufgabe, die sich aufteilen lässt: Mit Subagents war der Lauf rund 20 bis 25 % schneller.
3. Den Verbrauch bestimmt vor allem das Modell der Hauptsitzung. Die sechs Haiku-Subagents zusammen machten nur 9 % eines
   Laufs mit Sonnet-Chef aus.
4. Sonnet hat in allen 6 großen Läufen als Prüfer 36 von 36 gefunden, Haiku in 9 Läufen 34 bis 36.

Rechte-Test (`rechte_test.py`): Ein Subagent mit `tools: Read, Grep, Glob` hat die Datei nicht geändert und gemeldet, dass
ihm das Schreibwerkzeug fehlt. Derselbe Subagent ohne die `tools`-Zeile hat die Datei geändert.

## Grenzen

Kleines Projekt, eher einfache Fehler, reine Lese-Aufgabe, nur 3 Läufe pro Variante. Die Zeiten schwanken von Lauf zu
Lauf (z. B. 13,5 bis 18 s bei derselben Variante). Die Hauptsitzung lief mit Sonnet 5.5, der Standard in Claude Code ist
Opus 5.5. Modelle antworten nicht deterministisch, deine Zahlen werden abweichen.

## Dateien

| Pfad | Inhalt |
|---|---|
| `pruefer.md` | der Subagent aus dem Video zum Kopieren nach `.claude/agents/` in deinem Projekt (im Video ist die Beschreibung gekürzt) |
| `projekt/shop/` | der Test-Shop: 18 Dateien, 724 Zeilen, 36 absichtlich eingebaute Fehler. **Nicht produktiv verwenden.** |
| `projekt/tests/` | 14 Tests, alle grün (sie treffen die Fehler nicht) |
| `projekt/.claude/agents/` | `pruefer-haiku.md` und `pruefer-sonnet.md`, bis auf `model` identisch |
| `run_test.py` | startet eine Variante ohne Oberfläche (`claude -p`) und speichert das Ergebnis in `outputs/` |
| `rechte_test.py` | der Rechte-Test auf einer Kopie des Projekts |
| `auswertung/loesung.json` | die 36 Fehler (Achtung, Spoiler) |
| `auswertung/beweis.py` | zeigt jeden Fehler mit einem echten Aufruf: „36 von 36 eingebauten Fehlern bestätigt“ |
| `auswertung/auswerten.py`, `zusammenfassung.py` | zählen die gefundenen Fehler je Lauf und bilden die Mittelwerte |
| `outputs/` | alle 30 Läufe als JSON und Text, `ergebnis.md`, die zwei Rechte-Läufe |

## Selbst ausprobieren

Voraussetzung: Claude Code ist installiert und angemeldet, Python 3.10 oder neuer. Jeder Lauf verbraucht etwas von deinem
Kontingent.

```
cd projekt
python -m pytest -q                      # 14 passed
cd ..
python auswertung/beweis.py              # 36 von 36 eingebauten Fehlern bestätigt
python run_test.py klein allein-haiku    # 6 Dateien, eine Sitzung mit Haiku
python run_test.py gross team-haiku      # 18 Dateien, Haiku-Chef + 6 Haiku-Subagents
python auswertung/auswerten.py -v        # Treffer je Lauf, dazu alle weiteren Meldungen
python auswertung/zusammenfassung.py     # Mittelwerte je Variante
```

Varianten: `allein-sonnet`, `allein-haiku`, `sub-haiku`, `sub-sonnet`, `team-haiku`, jeweils mit `klein` oder `gross`.

Eigener Subagent in deinem Projekt:

```
mkdir .claude\agents                     # macOS / Linux: mkdir -p .claude/agents
copy pruefer.md .claude\agents\          # macOS / Linux: cp pruefer.md .claude/agents/
```

Wenn der Ordner neu ist, Claude Code einmal neu starten. Dann in Claude Code:
`Nutze den pruefer-Subagent und prüfe meine drei größten Dateien`.

## Quellen

- Subagents: https://code.claude.com/docs/en/sub-agents
- Kosten und Verbrauch: https://code.claude.com/docs/en/costs
- Modelle in Claude Code: https://code.claude.com/docs/en/model-config
- Modelle und Listenpreise: https://platform.claude.com/docs/en/about-claude/models/overview
- Changelog von Claude Code: https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md
- Release Notes (Haiku 5.5, 7.10.2026): https://support.claude.com/en/articles/12138966-release-notes
