---
name: commit-check
description: Prüft gestagte Änderungen vor einem Commit oder Push auf Geheimnisse und private Daten - API-Keys, Tokens, Passwörter, E-Mail-Adressen und persönliche Pfade wie C:\Users\name. Verwenden, wenn der Nutzer committen, pushen, etwas auf GitHub hochladen oder Änderungen auf Geheimnisse prüfen will.
allowed-tools: Bash(python ${CLAUDE_SKILL_DIR}/scripts/pruefen.py --staged --nur-bericht)
---

# Commit-Check

Ziel: Nichts Geheimes oder Privates landet in einem Commit.

## Ergebnis des Prüfskripts (lief beim Laden dieses Skills)

!`python ${CLAUDE_SKILL_DIR}/scripts/pruefen.py --staged --nur-bericht`

## So gehst du vor

1. Steht oben "nichts gefunden": Melde "Commit-Check: nichts gefunden" und mach mit der eigentlichen Aufgabe weiter.
   Steht oben "Nichts gestagt": Frag, welche Dateien in den Commit sollen. Stage nichts ungefragt.
2. Stehen oben Funde: Committe NICHT und pushe NICHT. Zeig die Funde als Tabelle (Datei, Zeile, Art).
   Schreib einen gefundenen Wert nie vollständig aus. Schlag pro Fund eine Lösung vor:
   - Key, Token, Passwort: in eine `.env` auslagern, `.env` in `.gitignore`, Wert mit `os.environ` lesen.
     War der Wert schon einmal gepusht, muss er beim Anbieter neu erstellt werden.
   - E-Mail-Adresse: entfernen oder durch eine noreply-Adresse ersetzen.
   - Persönlicher Pfad: relativen Pfad oder `Path.home()` verwenden.
   Frag danach, ob du die Änderungen so umsetzen sollst.
3. Lies zusätzlich selbst den Diff (`git diff --cached`) und nenne getrennt als "Hinweis", was das Skript
   nicht kennt, z. B. interne URLs, Kundennamen oder IP-Adressen.

Grenze: Das Skript findet nur bekannte Muster, und ein Skill ist eine Bitte, keine Garantie.
Für einen festen Stopp vor jedem Commit dasselbe Skript als Git-Hook eintragen (siehe README).
