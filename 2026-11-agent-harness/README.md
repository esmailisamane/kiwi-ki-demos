# Agent Harness: Was aus einem LLM einen KI-Agenten macht – Mini-Harness zum Selberbauen

Code und echte Ausgaben zum Video **„Agent Harness erklärt: Was aus einem LLM einen KI-Agenten macht“**
(KIwi – KI einfach erklärt). Getestet am 01.11.2026 mit Python 3.12, Ollama 0.35.0 und dem Modell `llama3.2:3b`
(lokal, kostenlos) sowie Claude Code 2.1.302 (Modell Haiku 5.5, Pro-Abo).

**Agent = Modell + Harness.** Das Modell schreibt nur Text – oder den *Wunsch*, ein Werkzeug zu benutzen.
Alles andere ist der Harness: Werkzeuge anbieten und **wirklich ausführen**, die Schleife drehen, vor Gefährlichem
fragen, Gedächtnis und Kontext verwalten, Grenzen setzen und prüfen. Hier baust du so einen Harness in ~200 Zeilen
Python – nur mit der Standardbibliothek.

## Loslegen (5 Minuten)

1. [Ollama](https://ollama.com) installieren und das Modell holen: `ollama pull llama3.2:3b` (2 GB)
2. Diesen Ordner herunterladen und darin starten: `python mini_harness.py`
3. Fragen stellen, z. B. „Wann ist mein Zahnarzttermin?“ – Ende mit `ende`.

Der Agent arbeitet **nur im Ordner `notizen/`** (erfundene Beispieldaten). Bevor er schreibt, löscht oder sich etwas
merkt, fragt er dich `[j/n]`. Vor jeder Änderung legt er eine Kopie in `sicherung/` ab.

Ohne Ollama prüfen, dass alles funktioniert: `python -m unittest test_harness.py -v` (8 Tests, falsches „Modell“).

## Die Schritte aus dem Video

| Datei | Was neu ist |
|---|---|
| [`schritt1_nur_modell.py`](schritt1_nur_modell.py) | Nur das Modell: es kann die Datei nicht lesen, es erklärt nur, wie *du* sie öffnest |
| [`schritt2_ein_werkzeug.py`](schritt2_ein_werkzeug.py) | Ein Werkzeug: das Modell *bestellt* `lies_datei`, **unser Code** liest die Datei |
| [`schritt3_schleife.py`](schritt3_schleife.py) | Die Schleife (`while True`) mit zwei Werkzeugen – und die Dateiliste von Anfang an im Kontext |
| [`schritt4_freigabe.py`](schritt4_freigabe.py) | Freigabe vor `schreibe_datei`/`loesche_datei` und ein Zaun um den Ordner |
| [`mini_harness.py`](mini_harness.py) | Alles zusammen + Gedächtnis (`GEDAECHTNIS.md`), Sicherung, Schrittgrenze, Zusammenfassen |
| [`zeige_schleife.py`](zeige_schleife.py) | Macht die echte Schleife von Claude Code sichtbar (siehe unten) |
| [`messung_schritt3.py`](messung_schritt3.py) | Unsere Messung: drei Reparaturen, je 10 Läufe |
| [`demo_laeufe.py`](demo_laeufe.py) | Alle Demo-Läufe aus dem Video auf einmal (Ausgaben in `outputs/`) |
| [`outputs/`](outputs) | Echte Ausgaben aller Läufe (ohne lokale Pfade, Benutzernamen und Sitzungs-IDs); Antworten schwanken von Lauf zu Lauf |

## Unsere Ergebnisse (echte Läufe, 01.11.2026)

- **Gleiches Modell, nur der Kontext ändert sich.** Aufgabe: „Wann ist mein Zahnarzttermin? Ich weiß nicht mehr, in
  welcher Datei er steht.“ Je 10 Läufe (temperature 0.7):
  Hinweis in der Werkzeug-Beschreibung **0/10** · Dateiliste in der Fehlermeldung **0/10** ·
  Dateiliste von Anfang an in der ersten Nachricht **10/10** (`outputs/messung_schritt3.jsonl`).
  Ohne Liste rät das Modell `Zahnarzttermin.txt`; einmal kündigt es „Ich werde termine.txt lesen“ an, ruft aber kein
  Werkzeug auf und **erfindet** einen Termin.
- **Freigabe:** „Mach aus allen Dateien eine einzige Datei alles.txt und lösch danach die alten.“ → das Modell will nur die
  *Dateinamen* in `alles.txt` schreiben und alle vier Dateien löschen; 5 × „n“ → nichts passiert (`5c_…`).
- **Blindes Ja ist gefährlich:** Im Test haben wir „j“ automatisch geschickt – das Modell überschrieb die Einkaufsliste mit
  einem Leerzeichen, ohne sie gelesen zu haben. Die Kopie in `sicherung/` hatte die alte Liste (`5b_…`).
- **Gedächtnis:** Sitzung 1 „Merk dir …“ → `GEDAECHTNIS.md`; neuer Start → „Gedächtnis geladen: 1 Notizen“.
  In einer früheren Version ohne Freigabe für `merke` füllte sich das Gedächtnis mit Müll („Gemerkt“) – deshalb fragt
  der Harness jetzt auch dort.
- **Schrittgrenze:** frühere Version, Grenze 3 – das Modell drehte sich im Kreis, der Harness stoppte (`5e_…`).
- **Claude Code, 4 Läufe mit `claude -p --output-format stream-json --verbose`:** Zahnarzt-Frage in 3 Runden
  (Grep → Read → Antwort); mit einer CLAUDE.md in 2 Runden. Löschen ohne Recht: **4 verschiedene Versuche, alle vom
  Harness verweigert**, Datei noch da. Mit `--max-turns 1`: `error_max_turns`.

Ehrlich: `llama3.2:3b` ist klein. Es wählt oft falsche Werkzeuge, schreibt Werkzeug-Wünsche manchmal als Text und
versucht es nach einem „Nein“ erneut. Zum Lernen ist das ideal (die Fehler sind sichtbar), für echte Arbeit mit
Schreibrechten nicht. Unsere Messung ist klein (3 × 10 Läufe, ein Modell, eine Aufgabe).

## Claude Codes echte Schleife sehen

```
claude -p "Wann ist mein Zahnarzttermin?" --model haiku --allowedTools "Read,Glob,Grep" --output-format stream-json --verbose | python zeige_schleife.py
```

Ausgabe (gekürzt):

```
[Start]  Modell: claude-haiku-5-5 | Werkzeuge: 29 | Rechte-Modus: default
[Runde 1] Claude will:  Grep(pattern=(?i)zahn|zahnarzt|dentist|arzt, path=., …)
[Runde 1] Harness gibt zurück: termine.txt:2:Donnerstag 14:30 Zahnarzt Dr. Berger
[Runde 2] Claude will:  Read(file_path=termine.txt)
[Runde 3] Claude sagt:  Dein Zahnarzttermin steht in termine.txt …
[Ende]   success | Runden: 3 | stop_reason: end_turn
```

Läuft nur mit deinem Claude-Code-Zugang (verbraucht etwas von deinem Kontingent). Führe es in einem Test-Ordner aus.

## Checkliste: Dein Harness ist gut, wenn …

- [ ] das Modell nur Werkzeuge **bestellt** und dein Code sie ausführt – nie umgekehrt
- [ ] die Schleife endet, wenn keine Bestellung mehr kommt, **und** eine Obergrenze hat (Schritte oder Budget)
- [ ] das Modell zu Beginn sieht, was es braucht (Dateiliste, Regeln, Gedächtnis) – nicht mehr
- [ ] Fehlermeldungen sagen, was als Nächstes zu tun ist
- [ ] alles Gefährliche (schreiben, löschen, merken, verschicken) eine Freigabe braucht – und du sie **liest**
- [ ] ein Zaun festlegt, wo der Agent arbeiten darf, und vor Änderungen eine Sicherung entsteht
- [ ] du dem Text des Modells nicht glaubst, sondern den echten Werkzeugaufrufen und Tests

Für Claude Code: kurze CLAUDE.md mit dem Test-Befehl · Freigaben lesen · deny-Regeln und Hooks für alles, was nie
passieren darf · `--max-turns` bei unbeaufsichtigten Läufen · `/clear` beim Themenwechsel.

## Quellen (gelesen am 01.11.2026)

- Claude Code Doku: [How Claude Code works](https://code.claude.com/docs/en/how-claude-code-works) („This surrounding layer is what the term agentic harness refers to“),
  [Agent loop (Agent SDK)](https://code.claude.com/docs/en/agent-sdk/agent-loop), [Headless / stream-json](https://code.claude.com/docs/en/headless),
  [Permissions](https://code.claude.com/docs/en/permissions), [Memory](https://code.claude.com/docs/en/memory),
  [Context window](https://code.claude.com/docs/en/context-window), [Features overview](https://code.claude.com/docs/en/features-overview)
- Anthropic Engineering: [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents),
  [Effective context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents),
  [Harness design for long-running apps](https://www.anthropic.com/engineering/harness-design-long-running-apps)
- [Ollama Tool Calling](https://docs.ollama.com/capabilities/tool-calling) · Mitchell Hashimoto,
  [My AI Adoption Journey](https://mitchellh.com/writing/my-ai-adoption-journey) · LangChain,
  [The Anatomy of an Agent Harness](https://www.langchain.com/blog/the-anatomy-of-an-agent-harness)

Kein offizielles Projekt von Anthropic oder Ollama. Lizenz: MIT (siehe [LICENSE](../LICENSE)).
