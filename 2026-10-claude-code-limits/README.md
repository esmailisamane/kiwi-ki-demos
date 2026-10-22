# Claude Code Limits: Was frisst dein Pro-Limit? – 18 Läufe im echten Test

Code und echte Ergebnisse zum Video **„Claude Code Limits: Was frisst dein Pro Usage Limit? (Deutsch)“**
(Kanal KIwi – KI einfach erklärt). Kein offizielles Projekt von Anthropic.

Die Frage: **Wie viel vom 5-Stunden-Fenster kostet dieselbe Aufgabe – je nach Modell, Effort, CLAUDE.md und Resume?**

Getestet am 21.10.2026 mit Claude Code 2.1.302 unter Windows 11, Claude Pro, `claude -p --permission-mode acceptEdits`.
Während der Messungen lief nichts anderes auf dem Konto.

## Was hier liegt

| Datei | Wozu |
|---|---|
| `projekt/` | kleiner Übungsladen mit zwei versteckten Fehlern (Rabatt, Gratisversand) und 10 Tests, davon 4 rot |
| `run_test.py` | der Test: frische Kopie pro Lauf, `claude -p`, liest Tokens, Listenpreis und das `rate_limit_event` |
| `auswertung.py` | Tabelle je Gruppe + Resume-Kosten pro Aufruf |
| `outputs/` | `laeufe.jsonl` (alle Läufe), `auswertung.txt` |

## Wie gemessen wird

- **Anteil am Limit:** `claude -p --output-format stream-json --verbose` meldet am Anfang jedes Laufs ein `rate_limit_event` mit
  `unifiedWindows.five_hour.utilization` und `seven_day.utilization` (ganze Prozent, gilt für das ganze Konto). Nach jeder Gruppe
  liest ein winziger Haiku-Lauf („stand“) den Wert danach ab.
- **Tokens und Listenpreis:** `total_cost_usd` ist die Schätzung von Claude Code zum API-Listenpreis. Mit Pro bezahlst du diesen
  Betrag nicht – er zeigt nur, wie schwer ein Lauf ist.
- Achtung bei `--resume`: `total_cost_usd` zählt die ganze Sitzung zusammen. Den Preis eines einzelnen Aufrufs rechnet
  `auswertung.py` als Differenz zum vorherigen Aufruf derselben Sitzung.

## Ergebnis (je 3 Läufe, alle 18 Läufe danach mit grünen Tests)

| Einstellung | Ø Listenpreis pro Lauf | 5-Stunden-Fenster für 3 Läufe | Ø Zeit |
|---|---|---|---|
| Opus 5.5 · medium (Standard bei Pro) | 0,13 $ | +3 % | 64 s |
| Sonnet 5.5 · medium | 0,06 $ | +2 % | 78 s |
| Haiku 5.5 · medium | 0,004 $ | unter 1 % | 69 s |
| Opus · low | 0,11 $ | +3 % | 69 s |
| Opus · max | 0,53 $ (Ø 7.752 Denk-Tokens) | +12 % | 132 s |
| Opus · medium + CLAUDE.md mit 1.500 Zeilen | 0,26 $ | +5 % | 59 s |

Große Log-Datei (3.000 Zeilen) mit Opus lesen lassen, eine Bitte, zwei Sitzungen:
- Claude sucht und zählt selbst, liest nur Anfang und Ende: **+3 %**
- Claude liest alles in vier Teilen, 16 Runden, 1.012.033 gelesene Tokens: **+11 %**

Eine kurze Frage an diese große Sitzung:

| Fall | Preis dieses Aufrufs | 5-Stunden-Fenster |
|---|---|---|
| nach 66 Minuten Pause (`--resume`, Cache abgelaufen, 170.427 Tokens neu in den Cache) | 1,45 $ | **+10 %** (68 → 78 %) |
| gleich danach, dieselbe Sitzung | 0,04 $ | unter 1 % |
| ganz neue Sitzung, gleiche Frage | 0,12 $ | – |

Grob: 1 % des 5-Stunden-Fensters entsprach in unserem Test etwa 0,10–0,15 $ Listenpreis. **Unsere Schätzung, keine offizielle
Zahl** – Anthropic veröffentlicht nicht, wie Tokens auf das Limit angerechnet werden.

## Grenzen

Eine kleine Aufgabe, je drei Läufe, ganze Prozent, ein Konto an einem Tag. Dieselbe Aufgabe kostet nicht jedes Mal gleich viel
(Opus low: 0,168 $ / 0,074 $ / 0,074 $; der erste Lauf einer Gruppe schreibt den Cache). Der Test verbraucht selbst einen Teil
deines Limits (bei uns zusammen etwa die Hälfte eines 5-Stunden-Fensters und 3 % der Woche).

## Selbst ausprobieren

```
python run_test.py --gruppe stand
python run_test.py --gruppe haiku_medium --wdh 3
python run_test.py --gruppe resume_start
python run_test.py --gruppe resume_kalt      # frühestens 65 Minuten später
python auswertung.py
```
`run_test.py` bricht ab, wenn das 5-Stunden-Fenster 85 % erreicht. Rohdaten mit Sitzungs-IDs bleiben im Temp-Ordner.

## Quellen

- https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan
- https://support.claude.com/en/articles/11647753-understanding-usage-and-length-limits
- https://code.claude.com/docs/en/costs
- https://code.claude.com/docs/en/model-config
- https://code.claude.com/docs/en/statusline
- https://code.claude.com/docs/en/changelog (2.1.304: Warnung beim Fortsetzen alter Gespräche; 2.1.305: `/usage` mit `f`)
