# KI-Agent erstellen mit Python: der Rechnungs-Agent (Claude Agent SDK)

Code zum Video **„KI-Agent erstellen mit Python: Claude Agent SDK Tutorial für Anfänger“** (November 2026).

Der Agent räumt einen Ordner mit Rechnungen auf:

1. liest jede Rechnung im Ordner `rechnungen/` (PDF und Fotos),
2. holt Lieferant, Datum, Brutto-Betrag und MwSt heraus,
3. schreibt alles in `rechnungen/rechnungen.csv` (öffnet sich in deutschem Excel mit richtigen Spalten und Umlauten),
4. benennt die Dateien um, z. B. `2026-11-03_Stadtwerke-Kiwistadt_84,20.pdf` – **aber nur, wenn du `j` tippst**,
5. rät nicht: Was nicht lesbar ist, wird `unklar`, und die Datei bleibt, wie sie ist.

> **Ehrlicher Hinweis:** Die Bildschirme im Video sind nachgestellt. Der Code hier ist nach der offiziellen Doku geschrieben und
> mit `claude-agent-sdk` **0.2.179** geprüft (Importe, Optionen, 8 Offline-Tests der Werkzeuge und der Freigabe). Gegen das
> echte Modell haben wir ihn für das Video nicht laufen lassen. Modelle antworten nicht immer gleich – prüfe die Ergebnisse.

## Dateien

| Datei | Was drin ist |
|---|---|
| `schritte/schritt1_erster_agent.py` | der kleinste Agent: liest **eine** Rechnung (nur das eingebaute Werkzeug `Read`) |
| `schritte/schritt2_werkzeug.py` | eigene Werkzeuge `list_invoices` und `save_invoice` → CSV |
| `rechnungs_agent.py` | der fertige Agent: + `rename_file` mit Zaun, Freigabe per `can_use_tool`, Regeln im `system_prompt`, Notbremsen |
| `test_werkzeuge.py` | 8 Offline-Tests (ohne API-Key): CSV, Umbenennen, Zaun, Freigabe |
| `beispiele_erzeugen.py` | erzeugt die erfundenen Beispiel-Rechnungen (alle Firmen sind ausgedacht) |
| `rechnungen/` | 5 Beispiel-PDFs + 1 verwischtes Foto, bei dem der Betrag nicht lesbar ist |
| `CHECKLISTE.md` | Installation je System + 5 Punkte für deinen eigenen Agenten |

## Loslegen

```bash
python -m venv .venv
# .venv aktivieren – Befehl je System siehe CHECKLISTE.md
pip install claude-agent-sdk
```

Du brauchst einen **API-Key aus der Claude Console** in der Umgebungsvariable `ANTHROPIC_API_KEY`. Laut Doku nutzen
Programme mit dem Agent SDK einen API-Key, nicht den Login eines Claude-Abos. Das SDK lädt eine `.env`-Datei **nicht** von
allein – dafür z. B. `pip install python-dotenv` und `load_dotenv()`.

**Jeder Lauf kostet API-Guthaben.** Setz dir in der Console ein Limit. Im Code begrenzen `max_turns=40` und
`max_budget_usd` einen Lauf (den Wert wählst du selbst).

```bash
python schritte/schritt1_erster_agent.py
python schritte/schritt2_werkzeug.py
python rechnungs_agent.py
```

Teste zuerst mit **Kopien** deiner Dateien, nie mit den Originalen. Zurücksetzen der Beispiele:
`pip install reportlab pillow` und `python beispiele_erzeugen.py`.

Offline-Tests (ohne API-Key): `pip install pytest` und `python -m pytest test_werkzeuge.py`

## Wichtig zu wissen

- **Werkzeugnamen:** Eigene Werkzeuge heißen für Claude `mcp__<schlüssel>__<name>`, z. B. `mcp__rechnungen__save_invoice`.
  Steht in `allowed_tools` nur `save_invoice`, gilt das Werkzeug als nicht freigegeben und wird im Standard-Modus abgelehnt.
- **Freigabe:** `can_use_tool` wird nur gefragt, wenn vorher nichts entschieden hat (Reihenfolge laut Doku: Hooks → Verbots- und
  Nachfrage-Regeln → Modus → `allowed_tools` → `can_use_tool`). Darum steht `rename_file` absichtlich **nicht** in `allowed_tools`.
- **Zaun im Werkzeug:** `rename_file` arbeitet nur direkt im Ordner `rechnungen` und überschreibt nie eine Datei – auch wenn
  du müde „j“ tippst.
- **`setting_sources=[]`:** Sonst lädt das SDK dieselben Einstellungen wie Claude Code auf deinem Rechner (inkl. `CLAUDE.md`).
- **Lange PDFs:** Über 10 Seiten liest `Read` in Abschnitten und braucht dafür `pdftoppm` aus poppler.
- **Datenschutz:** Jede gelesene Datei geht zur Verarbeitung an die API von Anthropic. Nur eigene Daten verwenden; in der Firma
  vorher fragen. Der Agent ersetzt keine Buchhaltung oder Steuerberatung.

## Quellen (Stand 08.11.2026)

- Agent SDK Überblick: https://code.claude.com/docs/en/agent-sdk/overview
- Quickstart: https://code.claude.com/docs/en/agent-sdk/quickstart
- Python-Referenz: https://code.claude.com/docs/en/agent-sdk/python
- Eigene Werkzeuge: https://code.claude.com/docs/en/agent-sdk/custom-tools
- Rechte und Freigaben: https://code.claude.com/docs/en/agent-sdk/permissions
- Werkzeuge (Read, PDFs, Bilder): https://code.claude.com/docs/en/tools-reference
- Paket: https://pypi.org/project/claude-agent-sdk/ (0.2.179, MIT, Python ≥ 3.10)

Dieses Projekt ist unabhängig und kein offizielles Material von Anthropic.
