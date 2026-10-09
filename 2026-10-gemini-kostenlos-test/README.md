# Gemini kostenlos ab 9. Oktober – drei Aufgaben, drei Gratis-KIs (+ Pro gratis in AI Studio)

Zum Video vom Kanal **KIwi – KI einfach erklärt** (Oktober 2026).

Ab dem 9. Oktober 2026 bekommen Nutzer der Gemini-App **ohne KI-Abo** (privates Google-Konto) nur noch das Modell
**Flash-Lite**; Flash und Pro gibt es dann nur mit Google AI Plus / Pro / Ultra
([offizielle Google-Hilfeseite](https://support.google.com/gemini/answer/17004136)).
Wir wollten wissen: Wie schlägt sich das kleinste Modell gegen andere kostenlose KIs?

## Die drei Aufgaben (`prompts/`)

| Aufgabe | Was sie prüft | Richtige Antwort |
|---|---|---|
| 1 – Code | Fehler finden + Ausgabe vorhersagen | gibt `4.666666666666667` aus; richtig wäre `6.0` – die Schleife startet bei 1 und überspringt die erste Zahl |
| 2 – Buchstaben zählen | Wie oft kommt „e" in „Erdbeermarmelade" vor? | `5` |
| 3 – Aktualität | Was ändert sich am 9.10.2026 für Gratis-Nutzer von Gemini? | nur noch Flash-Lite ohne Abo |

Jede Aufgabe wurde in einem **neuen Chat** mit **Standard-Einstellungen** gestellt.

## Teilnehmer

- **Gemini 3.5 Flash-Lite** – in der Gemini-App mit kostenlosem Konto, Modell im Menü ausgewählt (genau das Modell,
  das ab dem 9.10. ohne Abo übrig bleibt)
- **ChatGPT** – kostenloser Plan auf chatgpt.com
- **Llama 3.2 3B** – lokal mit [Ollama](https://ollama.com), Skript `test_lokal.py` (3 Durchläufe pro Aufgabe)
- **Bonus: Gemini 3.1 Pro Preview** – in [Google AI Studio](https://aistudio.google.com) mit kostenlosem Konto (Stand 8.10.2026;
  was dort kostenlos ist, kann Google ändern; im Gratis-Bereich dürfen Eingaben zur Produktverbesserung genutzt werden)

Die Web-Apps haben wir einmal pro Aufgabe gestellt und als Bildschirmaufnahme im Video gezeigt.

## Ergebnisse

| | Aufgabe 1 – Code | Aufgabe 2 – Zählen | Aufgabe 3 – Aktuell |
|---|---|---|---|
| Gemini 3.5 Flash-Lite (App) | ½ – Fehler + Korrektur richtig, Ausgabe falsch (4.0), erfindet 2. Fehler | ✓ 5 | ✗ „nichts Grundlegendes“ |
| ChatGPT (Gratis, Nachdenken aus) | ✓ alles richtig | ✓ 5 | ✓ mit Websuche |
| Llama 3.2 3B (lokal) | ½ – Fehler 3/3 gefunden, Ausgabe 0/3 | ✗ 2, 2, 3 | ✗ weiß es nicht / rät falsch |
| **Bonus:** Gemini 3.1 Pro in Google AI Studio (kostenloses Konto) | ✓ alles richtig | ✓ 5 | ✓ mit Google-Suche, 4 Quellen |

Wörtliche Antworten der Web-Apps: [`outputs/web-apps.md`](outputs/web-apps.md).

**Llama 3.2 3B (lokal, Q4_K_M, 07.10.2026)** – Rohantworten in `outputs/llama3.2_3b/`:

- Aufgabe 1: erkennt in 3/3 Läufen die übersprungene erste Zahl, nennt aber nie die tatsächliche Ausgabe.
  Lauf 2 „korrigiert" zu `sum(zahlen[1:]) / len(zahlen[1:])` – das ist immer noch falsch (ergibt `7.0`).
  Lauf 3 erfindet einen zweiten Fehler.
- Aufgabe 2: `2`, `2`, `3` – 0/3 richtig.
- Aufgabe 3: weiß es in 3/3 Läufen nicht (Wissensstand laut eigener Aussage Dezember 2023);
  Lauf 3 rät trotzdem, dass sich wahrscheinlich nichts ändert.

Modellantworten ändern sich von Lauf zu Lauf – das ist ein kleiner Test, kein Benchmark.

## Selbst ausprobieren

```bash
ollama pull llama3.2:3b
python test_lokal.py            # 3 Läufe pro Aufgabe
python test_lokal.py 5 qwen3:4b # anderes Modell, 5 Läufe
```

Nur Python-Standardbibliothek. Die automatische Prüfung ist bewusst einfach (Stichworte) – lies die Antworten selbst.

## Quellen (geprüft am 07.10.2026)

- Google: Modellverfügbarkeit Gemini-App – https://support.google.com/gemini/answer/17004136
- Google One Tarife Deutschland (AI Plus 9,99 € mit 2 TB, AI Pro 21,99 € pro Monat; eingeloggt zusätzlich AI Plus 400 GB für 4,99 €) – https://one.google.com/about/plans
- Gemini-API Modelle und Preise (AI Studio kostenlos) – https://ai.google.dev/gemini-api/docs/models ,
  https://ai.google.dev/gemini-api/docs/pricing

Kein offizielles Projekt von Google, OpenAI oder Meta.
