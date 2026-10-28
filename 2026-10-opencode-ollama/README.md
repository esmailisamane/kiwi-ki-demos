# OpenCode 2 + Ollama: lokal und kostenlos coden – richtig einrichten

Dateien zum Video **„OpenCode 2 + Ollama Tutorial Deutsch: Lokal & kostenlos coden – richtig einrichten“**
(Kanal KIwi – KI einfach erklärt). Kein offizielles Projekt von OpenCode/Anomaly oder Ollama.

Eingerichtet am 27.10.2026 mit OpenCode 2.2.0, Ollama 0.35.0 und dem Modell `qwen3:4b-instruct` auf einem Laptop mit
4 GB Grafikspeicher.

## Die drei Einstellungen aus dem Video

1. **Genug Kontext.** OpenCode schickt schon beim ersten Schritt rund 7.000 Tokens (Anweisungen + Werkzeuge). Mit Ollamas
   4.096 Tokens wurde der Text bei uns still gekürzt (`truncating input prompt limit=2050 prompt=7009`), das Modell sah die
   Frage nicht mehr. Mit der [Modelfile](Modelfile) entsteht eine Variante mit 16.384 Tokens:
   ```
   ollama pull qwen3:4b-instruct
   ollama create qwen3-4b-instruct-16k -f Modelfile
   ```
   Ollama selbst empfiehlt für OpenCode 64k. Bei uns wurde das kleine Modell damit 13 GB groß und lief zu 84 % auf dem
   Prozessor. Mehr Grafikspeicher = mehr Kontext.
2. **Zeitgrenze als Zahl.** OpenCode wartet laut Doku höchstens 5 Minuten auf den Anfang der Antwort. In
   [opencode.json](opencode.json) steht deshalb `"headerTimeout": 1800000` (30 Minuten). Mit `false` hat OpenCode bei uns
   trotzdem nach 5 Minuten abgebrochen. Ob die Datei geladen wird, zeigt `opencode debug config`.
3. **Ein Modell ohne langes Nachdenken.** „Sag nur: hallo“ dauerte mit `qwen3:4b` (denkt erst nach) 2:28 min, mit
   `qwen3:4b-instruct` 0:53 min.

## Die Rechte-Liste

[opencode.json](opencode.json) verbietet zuerst alles und erlaubt dann gezielt: lesen und suchen im Projekt (ohne `.env`),
eine bestimmte Datei ändern (`shop/lieferung.py` – für dein Projekt anpassen) und als einzigen Befehl `python -m pytest`.
Zugriff außerhalb des Ordners bleibt verboten. Die letzte passende Regel gewinnt.

Warum: In Version 2 darf der Build-Agent laut Doku standardmäßig auch außerhalb des Projektordners lesen und ändern, ohne zu
fragen. Bei uns hat OpenCode durch einen Fehler in unserem Aufbau im übergeordneten Ordner gearbeitet und dort eine Datei
überschrieben.

## Weitere Beobachtungen

- Der Hintergrund-Dienst setzt abgebrochene Sitzungen von selbst fort („The server restarted while you were working.
  Continue from where you left off …“). Aufräumen: `opencode session list`, `opencode session delete <id>`,
  `opencode service stop`; einzelne Aufträge ohne gemeinsamen Dienst: `opencode run --standalone "…"`.
- [netzwerk_log.ps1](netzwerk_log.ps1) schreibt alle 2 Sekunden die Verbindungen von OpenCode nach außen auf.
  [ausgaben/netzwerk_lokaler_lauf.csv](ausgaben/netzwerk_lokaler_lauf.csv): Während eines rein lokalen Laufs gingen nur
  Verbindungen zu `models.opencode.ai` (Liste der Modelle); beim Start außerdem zu GitHub. Die Inhalte sind verschlüsselt,
  wir sehen nur die Ziele.
- Alte Anleitungen zeigen Version 1 (`npm install -g opencode-ai`, `"provider"`, `"permission"`). Version 2:
  `npm install -g @opencode/cli`, `"providers"`, `"permissions"`, nur noch `AGENTS.md` (kein `CLAUDE.md`).

## Grenzen

Auf unserem Laptop dauerte jeder Schritt des Agenten mehrere Minuten, und das kleine Modell machte Fehler (z. B. Markdown-Zeichen
in einer Python-Datei). Für kurze, klare Aufgaben geht es; für große Umbauten brauchst du mehr Grafikspeicher oder ein
Cloud-Modell. Deine Zeiten hängen stark von deiner Hardware ab.

Quellen: [opencode.ai/v2/docs](https://opencode.ai/v2/docs) · [github.com/anomalyco/opencode](https://github.com/anomalyco/opencode) ·
[docs.ollama.com/integrations/opencode](https://docs.ollama.com/integrations/opencode)
