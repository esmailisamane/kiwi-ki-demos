# Checkliste: DeepSeek Harness selbst ausprobieren

Stand: offizielles Repo, Commit `fcc0ad46` (04.11.2026), Version `0.2.2-rc.1` – Developer Preview, es kann sich alles ändern.

1. **Node.js 24.9 oder neuer** – prüfen mit `node --version` (manche Webseiten nennen ältere Versionen; im Quellcode steht `>=24.9.0`).
2. **Im Projektordner starten:** `npx @deepseek-ai/dsh web` → `http://127.0.0.1:3080` (`--no-open` ohne Browser, `--port 8080` anderer Port).
3. **Modell anbinden:** Settings → Models → API key (von platform.deepseek.com) → Apply.
   Andere Anbieter: Add model provider (`anthropic`, `openai`, `moonshotai`, `zai`) oder Custom model API.
4. **Choose workspace** – ohne Workspace bleibt das Eingabefeld gesperrt.
5. **Erste Aufgabe im Standard mode** – jeden Befehl lesen, bevor du Allow once / Always allow klickst.
6. **PTC und Minimal** erscheinen erst mit **Coding Tools** an (Settings → General).
7. **Erstes Plugin:** im Creator mode („Let the agent create a plugin“) oder selbst – Pfad in `cordis.yml` **absolut**.

Extra:
- Konfiguration: `$DSH_HOME/profiles/web/cordis.patch.yml` (Settings → Open configuration file), ganzer Baum: `dsh --profile web --dump-config`.
- Ein Patch ersetzt die **ganze** `config` einer Zeile – alle Werte mitschreiben.
- Plugins von GitHub: `allowBuilds` = Code läuft beim Installieren außerhalb jeder Sandbox → nur geprüften Code, Commit pinnen (`#<sha>`).
- Sicherheit: wenig Rechte, Wegwerf-Umgebung, Backups, keine wichtigen Schlüssel.
