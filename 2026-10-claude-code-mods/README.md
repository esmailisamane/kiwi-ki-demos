# KI-News: Claude Code Mods – der Mod aus dem Video

Ein kleiner Claude-Code-Mod (`push-guard`), der Force-Pushes und `rm -r`/`rm -rf` ablehnt, bevor sie laufen.
Getestet am 3. Oktober 2026 mit Claude Code **2.1.288** unter Windows 11. Mods brauchen **2.1.287 oder neuer**.

## Ausprobieren

```bash
# 1. Prüfen, was der Mod tut – ohne ihn auszuführen
claude plugin validate ./push-guard

# 2. Automatische Tests – ohne Modell, ohne Kosten
cd push-guard && claude plugin test

# 3. In einer Sitzung laden (am besten in einem Spiel-Repository)
claude --plugin-dir ./push-guard
```

## Was wir gelernt haben (echte Ergebnisse in `outputs/`)

| Lauf | Ergebnis |
|---|---|
| `validate` | `hooks: tool.call{tool=Bash\|PowerShell}` · `calls: nothing on $` – der Mod liest keine Dateien und sendet nichts |
| `plugin test` | 6 pass, 0 fail – inklusive eines bewusst ehrlichen Grenztests (Force-Push in einem Skript läuft durch) |
| Version 1 (nur `Bash`) unter Windows | Claude nutzte das Werkzeug **PowerShell** → der Mod sah den Befehl nicht → Commit B auf dem Remote weg |
| Version 2 (`Bash` + `PowerShell`) | `push-guard: blocked "git push --force origin main"` → Commit B bleibt |

**Wichtig:** Der Mod vergleicht nur den Text des Befehls. Für harte Regeln: Branch-Schutz bei deinem Git-Hoster.
Mods laufen mit deinen Rechten und ohne Sandbox – installiere nur Mods aus Quellen, denen du vertraust.

## Quellen
- Anthropic: https://claude.com/blog/claude-code-mods
- Doku: https://code.claude.com/docs/en/plugins/mods/overview
- Events (tool.call, deny, $.ui.ask, .catch): https://code.claude.com/docs/en/plugins/mods/events
- Admins (sec-default, allowManagedModsOnly): https://code.claude.com/docs/en/plugins/mods/admin

Lizenz: MIT (siehe LICENSE im Hauptordner).
