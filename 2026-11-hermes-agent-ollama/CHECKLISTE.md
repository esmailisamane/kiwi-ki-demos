# Checkliste: Hermes Agent lokal mit Ollama

## 1. Ollama installieren
- Windows (PowerShell): `irm https://ollama.com/install.ps1 | iex` (oder Installer von ollama.com)
- macOS / Linux: `curl -fsSL https://ollama.com/install.sh | sh`
- Prüfen: `ollama --version` und `curl http://localhost:11434/api/tags`

## 2. Modell mit Tool Calling laden
- `ollama pull gemma4:31b` (stark, ≈ 20 GB, Faustregel 16 GB Grafikspeicher)
- Alternative: `ollama pull qwen3.8:27b` (≈ 18 GB)
- Normaler Laptop: `ollama pull gemma4:e4b`
- Keine Namen mit `-cloud` nehmen, wenn alles lokal bleiben soll.

## 3. Kontext auf mindestens 64K
- Ollama-App → Settings → **Context length** → 64k
- oder: `OLLAMA_CONTEXT_LENGTH=64000 ollama serve`
- Prüfen: `ollama ps` → Spalte CONTEXT ≥ 64000, Spalte PROCESSOR = GPU oder CPU

## 4. Hermes starten
- Einfach: `ollama launch hermes` (installiert Hermes bei Bedarf, Modell wählen, Messenger überspringen)
- Ohne Ollama-Assistent:
  - Windows: `iex (irm https://hermes-agent.nousresearch.com/install.ps1)`
  - macOS / Linux: `curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash`
  - `hermes model` → Custom Endpoint → `http://localhost:11434/v1`, API-Key leer, Modell `gemma4:31b`
- Oberfläche: `hermes --tui` (modern) oder `hermes` (klassisch); fortsetzen mit `hermes --continue`

## 5. Erste Aufgaben
- „Fasse dieses Projekt in fünf Punkten zusammen und sag mir, welche Datei der Einstiegspunkt ist.“
- Freigabe-Abfrage: `[o]nce | [s]ession | [a]lways | [d]eny` – ohne Antwort in 300 s abgelehnt
- Erste Antwort langsam? Normal (Anweisungen + Werkzeug-Beschreibungen). `hermes tools` → Unnötiges abschalten.

## 6. Memory und Skills
- Vorliebe sagen: „Antworte mir immer kurz und auf Deutsch.“ → landet in `~/.hermes/memories/USER.md`
- Speichern nur mit Freigabe: `memory.write_approval: true`, dann `/memory pending`
- Skill aus einem Ablauf: `/learn wie wir gerade einen Test angelegt und ausgeführt haben`
- Skill nutzen: `/name-des-skills …`; fremde Skills: `hermes skills browse`, `hermes skills install` (mit Sicherheitsscan)

## 7. Telegram
- @BotFather → `/newbot` → Anzeigename → Nutzername auf `bot` → Token (geheim halten, sonst `/revoke`)
- Eigene Nutzer-ID (Zahl) z. B. über @userinfobot
- `hermes gateway setup` → Telegram → Token + Nutzer-ID; Start: `hermes gateway`
- Fremde Nutzer: `hermes pairing approve telegram CODE`; **nie** `GATEWAY_ALLOW_ALL_USERS=true`
- WhatsApp geht nur über eine inoffizielle Brücke (Sperrrisiko laut Doku, eigene Nummer verwenden).

## 8. Sicherheit
- `approvals.mode: manual` und eine Sperrliste unter `approvals.deny`
- Checkpoints: `hermes chat --checkpoints`, zurück mit `/rollback`
- Echte Trennung: `terminal.backend: docker`
- Bei Problemen: `hermes doctor`; „Connection refused“ → `ollama serve`

## 9. Lokal + Cloud
- Wechseln: `hermes model` (z. B. Anthropic mit API-Key)
- Reserve: `fallback_providers` in `config.yaml` – nur wenn das lokale Modell scheitert
