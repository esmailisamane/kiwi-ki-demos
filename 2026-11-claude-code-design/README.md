# Claude Code Design: `/design` Schritt für Schritt

Material zum Video **„Claude Code Design Tutorial Deutsch: /design Schritt für Schritt“** (November 2026).

Mit `/design` entwirft Claude Code Oberflächen als **Artboards** auf einem **Canvas** (einer privaten Webseite auf claude.ai).
Du wählst einen Entwurf aus, passt ihn an und lässt ihn von Claude in deinen Code umsetzen.

> **Ehrlicher Hinweis:** Die Bildschirme im Video sind nachgestellt – nach der offiziellen Doku (Stand 14.11.2026).
> `/design` ist laut Doku eine **Research Preview** und kann sich ändern. Dies ist kein offizielles Projekt von Anthropic.

## Dateien

| Datei | Was drin ist |
|---|---|
| `BRIEF_VORLAGE.md` | Vorlage für einen guten Brief (was, für wen, Regeln, Dateien, Anzahl Varianten) + das Beispiel aus dem Video |
| `CHECKLISTE.md` | alle Befehle aus dem Video, Voraussetzungen und der Umzug von claude.ai/design vor dem 14.12.2026 |
| `app/` | die kleine Beispiel-App „Kiwi Rezepte“ (React + Vite) im **Startzustand**: die Startseite ist nur eine graue Liste – zum Selbst-Ausprobieren von `/design` |

## Loslegen

```bash
cd app
npm install
npm run dev          # Startseite unter http://localhost:5173
claude               # in einem zweiten Terminal, im Ordner app
```

Dann in Claude Code den Brief aus `BRIEF_VORLAGE.md` mit `/design` davor eintippen.

## Quellen

- Claude Code – What's new, Woche 34 (17.–21.08.2026): https://code.claude.com/docs/en/whats-new/2026-w34
- Claude Code – Artifacts: https://code.claude.com/docs/en/artifacts
- Get started with Claude Design: https://support.claude.com/en/articles/14604416-get-started-with-claude-design
- Move from standalone Claude Design to Claude: https://support.claude.com/en/articles/17440474
