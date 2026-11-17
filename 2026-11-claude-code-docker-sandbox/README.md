# Claude Code Docker Sandbox: Agenten sicher laufen lassen

Begleitmaterial zum Video **„Claude Code Docker Sandbox: Agenten sicher laufen lassen (Tutorial Deutsch)“** vom Kanal
KIwi – KI einfach erklärt.

> **Hinweis:** Das Video ist ein **nachgestelltes Tutorial**. Alle Befehle stammen aus der offiziellen Doku von Docker
> (docs.docker.com/ai/sandboxes, gelesen am 17.11.2026) und Anthropic (code.claude.com/docs). Wir haben sie für das Video
> nicht ausgeführt. Ausgaben, die die Doku nicht zeigt, sind im Video als „Ausgabe sinngemäß“ markiert. Kein offizielles
> Video von Docker oder Anthropic.

## Inhalt

- `CHECKLISTE.md` – alle Befehle aus dem Video in der richtigen Reihenfolge
- `kiwi-kurse/` – das kleine Beispielprojekt aus dem Video (Node, rechnet Euro in andere Währungen um)

## Kurz erklärt

Eine Docker Sandbox ist eine **Micro-VM mit eigenem Linux-Kernel**. Claude Code läuft darin mit
`--dangerously-skip-permissions` (Standard in der Sandbox), sieht aber nur deinen Projektordner. Ins Netz geht es nur
über einen Proxy mit Regeln (`allow-all`, `balanced`, `deny-all`). API-Keys bleiben im Schlüsselbund deines Systems und
werden erst unterwegs vom Proxy eingesetzt.

**Was die Sandbox nicht schützt:** Dein Projektordner ist lesend und schreibend eingehängt. Prüfe jede Änderung
(Git-Hooks, Makefile, `.claude/`-Einstellungen!) oder nutze den Clone-Modus `sbx run --clone claude .`.
Lokale MCP-Server laufen auf deinem Rechner, außerhalb der Sandbox.

## Quellen

- Docker Sandboxes: https://docs.docker.com/ai/sandboxes/
- Installation: https://docs.docker.com/ai/sandboxes/install/
- Claude Code in der Sandbox: https://docs.docker.com/ai/sandboxes/agents/claude-code/
- Isolation: https://docs.docker.com/ai/sandboxes/security/isolation/
- Netzwerk-Regeln: https://docs.docker.com/ai/governance/local/network-rules/
- Zugangsdaten: https://docs.docker.com/ai/sandboxes/configuration/credentials/
- Anthropic, Sandbox-Umgebungen: https://code.claude.com/docs/en/sandbox-environments
- Anthropic, Permission Modes: https://code.claude.com/docs/en/permission-modes
- Anthropic, /sandbox: https://code.claude.com/docs/en/sandboxing

Stand: 17.11.2026. `sbx` ist neu und ändert sich schnell – prüfe immer die aktuelle Doku.
