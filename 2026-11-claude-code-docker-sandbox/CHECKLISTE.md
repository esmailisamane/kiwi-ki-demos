# Checkliste: Claude Code in der Docker Sandbox

Alle Befehle aus dem Video, nach der offiziellen Doku (Stand 17.11.2026).

## 1. Installieren

**Windows 11** (Windows Hypervisor Platform muss eingeschaltet sein):

```powershell
# einmalig, in einer PowerShell als Administrator:
Enable-WindowsOptionalFeature -Online -FeatureName HypervisorPlatform -All
winget install -h Docker.sbx
```

**macOS** (ab macOS 14 Sonoma, Apple-Chip):

```bash
brew trust docker/tap
brew install docker/tap/sbx
```

**Ubuntu** (ab 24.04, KVM an, Benutzer in der Gruppe `kvm`):

```bash
sudo usermod -aG kvm $USER
curl -fsSL https://get.docker.com | sudo SBX=1 sh
```

Docker Desktop ist nicht nötig. Lokal ist `sbx` laut Docker kostenlos, auch für kommerzielle Arbeit.

## 2. Anmelden

```bash
sbx login
```

## 3. Erste Sandbox

```bash
cd kiwi-kurse
sbx run --name kiwi claude
```

- Beim ersten Start: Netzwerk-Regel wählen → für den Anfang **balanced**
  (ohne Nachfrage: `sbx policy init balanced`).
- In Claude Code anmelden: `/login` (das Token bleibt auf deinem Rechner).
- Claude läuft in der Sandbox mit `--dangerously-skip-permissions`. Rückfragen wieder an: `/permissions`.

## 4. Netzwerk gezielt freigeben

```bash
sbx policy log                                        # was wurde blockiert?
sbx policy allow network api.frankfurter.app          # genau eine Adresse erlauben
sbx policy allow network --sandbox kiwi api.example.com
sbx policy allow network api.github.com --method GET --path '/repos/org/project/**'
sbx policy ls                                         # alle Regeln (Grundliste prüfen!)
sbx policy rm network --resource api.example.com
```

## 5. API-Keys

```bash
sbx secret set anthropic                  # nie den Key in der Sandbox eintragen
sbx secret set github --command 'gh auth token'
sbx secret ls
sbx secret rm anthropic
```

## 6. Änderungen prüfen

- [ ] Jede Änderung im Diff ansehen, bevor du committest oder baust
- [ ] Besonders: `.git/hooks/`, `Makefile`, `.claude/settings.json`, CI-Dateien
- [ ] Noch sicherer: Clone-Modus

```bash
sbx run --clone claude .     # Ordner nur lesbar, Claude arbeitet in einer Kopie
# Ergebnisse über das Git-Remote "sandbox-kiwi" holen und prüfen
```

## 7. Verwalten und aufräumen

```bash
sbx ls
sbx stop kiwi
sbx start kiwi
sbx            # Dashboard
sbx rm kiwi    # löscht die Sandbox, nicht deine Projektdateien
sbx reset      # alle Sandboxes zurücksetzen
```
