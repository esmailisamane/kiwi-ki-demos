# Checkliste: Rechnungs-Agent einrichten + eigener Agent

## 1. Einrichten

- [ ] Python 3.10 oder neuer: `python --version`
- [ ] Ordner anlegen: `mkdir rechnungs-agent` und `cd rechnungs-agent`
- [ ] Virtuelle Umgebung: `python -m venv .venv`
- [ ] Aktivieren:
  - macOS / Linux: `source .venv/bin/activate`
  - Windows PowerShell: `.venv\Scripts\Activate.ps1`
    (blockiert? zuerst `Set-ExecutionPolicy -Scope Process RemoteSigned`)
  - Windows cmd: `.venv\Scripts\activate.bat`
- [ ] SDK: `pip install claude-agent-sdk` (bringt Claude Code schon mit)
- [ ] API-Key aus der Claude Console als `ANTHROPIC_API_KEY` setzen
  - macOS / Linux: `export ANTHROPIC_API_KEY=...`
  - PowerShell: `$env:ANTHROPIC_API_KEY = "..."`
  - oder `.env` + `python-dotenv` (`load_dotenv()` – wird **nicht** automatisch geladen)
- [ ] Ausgaben-Limit in der Console setzen
- [ ] Zuerst mit **Kopien** testen

## 2. Fünf Punkte für deinen eigenen Agenten

1. [ ] **Aufgabe als Schritte aufschreiben** – wie für einen neuen Praktikanten (kommt in den `system_prompt`).
2. [ ] **Nur nötige Werkzeuge** – eigene Werkzeuge mit `@tool`, klare `description`, Rückgabe `content` / `is_error`.
3. [ ] **Ändern & Löschen → Freigabe** – nicht in `allowed_tools`, sondern über `can_use_tool` fragen; dazu ein Zaun im Werkzeug.
4. [ ] **Regel gegen das Raten** – genau sagen, was bei Unklarheit passiert („unklar“, nicht umbenennen).
5. [ ] **Notbremsen** – `max_turns` und `max_budget_usd`; `setting_sources=[]`, wenn nur deine Regeln gelten sollen.

## 3. Typische Fehler

- Werkzeug wird abgelehnt → vollen Namen `mcp__<schlüssel>__<werkzeug>` in `allowed_tools` eintragen.
- Excel zeigt alles in einer Spalte / kaputte Umlaute → `encoding="utf-8-sig"` und `delimiter=";"`.
- Agent fragt nie → das Werkzeug steht in `allowed_tools` oder ein lockerer `permission_mode` ist gesetzt.
- PDF über 10 Seiten klappt nicht → `pdftoppm` (poppler) installieren.
