# DeepSeek Harness: eigenes Plugin `commit_message` + Checkliste

Code zum Video **„DeepSeek Harness Deutsch: Installation, Modi & eigenes Plugin – komplettes Tutorial“** vom Kanal
**KIwi – KI einfach erklärt**. Kein offizielles Material von DeepSeek.

> **Ehrlicher Hinweis:** Dieses Video ist ein *nachgestelltes* Tutorial. Wir haben DeepSeek Harness **nicht** installiert
> und den Code hier **nicht** ausgeführt. Jede Zeile folgt der offiziellen Doku und dem Quellcode
> ([github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness), Commit `fcc0ad46`,
> 04.11.2026, Version `0.2.2-rc.1`, Developer Preview). Wenn sich die API ändert, kann der Code angepasst werden müssen.

## Was das Plugin macht

Ein Werkzeug `commit_message`: Das Modell schickt `type` (z. B. `fix`) und `summary`, das Werkzeug gibt eine kurze
Commit-Nachricht zurück, z. B. `fix: keep results on double submit`. Die maximale Länge ist konfigurierbar
(`maxLength`, Standard 72).

## Dateien

| Datei | Wofür |
|---|---|
| `scratch-plugin/src/commit-message.ts` | das Plugin (TypeScript): `apply(ctx)`, `inject = ['tools']`, `defineTool`, `Config` |
| `scratch-plugin/cordis.yml` | lädt das Plugin über `--patch` (Pfad **absolut** eintragen!) |
| `dsh-commit-message/` | dasselbe Plugin als installierbares Bundle (`package.json` mit `dsh.bundle`, `cordis.patch.yml`, `index.js`) |
| `CHECKLISTE.md` | die Checkliste aus dem Video |

## Weg 1: Entwickeln mit `--patch` (wie in der offiziellen Anleitung, aus dem Quellcode)

```sh
git clone https://github.com/deepseek-ai/deepseek-harness.git
cd deepseek-harness
pnpm install          # pnpm fehlt? -> corepack enable
pnpm run build
mkdir -p scratch-plugin/src
# commit-message.ts nach scratch-plugin/src/ kopieren, cordis.yml nach scratch-plugin/
# in cordis.yml den Pfad durch den absoluten Pfad ersetzen (pwd im Repo-Ordner)
pnpm dsh web --patch ./scratch-plugin/cordis.yml
```

Im Browser (`http://127.0.0.1:3080`): `Use the commit_message tool for a fix.`

## Weg 2: Als Bundle installieren

```sh
dsh plugin --profile demo add ./dsh-commit-message      # im Quellcode-Ordner: pnpm dsh plugin …
dsh --profile demo --dump-config                         # zeigt eine Schicht "# == dsh-commit-message"
dsh --profile demo
dsh plugin --profile demo remove dsh-commit-message
```

Laut Doku sollen dsh-Pakete, die das Plugin mit dem Host teilt, unter `peerDependencies` **und** `devDependencies`
stehen (siehe „Package and install a plugin“). Für dieses kleine Beispiel haben wir das nicht ausprobiert.

## Quellen (offizielles Repo)

- `README.md`, `SAFETY.md`, `BRAND_GUIDELINES.md`
- `docs/user/guide/index.md`, `docs/user/guide/providers.md`
- `docs/user/develop/basic/index.md`, `tool.md`, `config.md`, `publish.md`
- `docs/cli-help.md`, `apps/cli/README.md`, `packages/bundle/headless/README.md`
- `packages/client/ui-agent-preset/` (vier Modi), `packages/subagent/subagent-claude-code/README.md`

## Sicherheit

DeepSeek Harness ist laut `SAFETY.md` nicht sicherheitsgeprüft und nicht produktionsreif. Wenig Rechte, Wegwerf-Umgebung
(VM/Container), Backups, keine wichtigen Schlüssel – und Plugins nur installieren, deren Code du gelesen hast.
