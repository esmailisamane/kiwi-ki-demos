# Checkliste: `/design` in Claude Code

Stand 14.11.2026, nach der offiziellen Doku. `/design` ist eine Research Preview – Details können sich ändern.

## Voraussetzungen

- [ ] Bezahlter Plan: Pro, Max, Team oder Enterprise
- [ ] Aktuelle Version: `claude --version` zeigt sie, `claude update` aktualisiert
      (laut Artifacts-Doku mindestens 2.1.281)
- [ ] Mit dem claude.ai-Konto angemeldet: `/login`
      (mit API-Key, Gateway-Token oder über einen Cloud-Anbieter kann Claude Code keine Artifacts veröffentlichen)
- [ ] Team/Enterprise: Artifacts und das Design-Template sind in den Organization settings eingeschaltet

## Arbeitsablauf

1. Brief schreiben (siehe `BRIEF_VORLAGE.md`) und mit `/design` davor eintippen
2. Link zum Canvas öffnen (normalerweise öffnet sich der Browser von selbst) – am besten im Desktop-Browser
3. Element anklicken und direkt ändern (speichert automatisch) oder einen Kommentar dranschreiben
4. Mehr Ideen im Terminal anfragen – Claude veröffentlicht neu unter derselben Adresse
5. Artboard bei Bedarf als PNG oder PDF exportieren
6. „Setz Variante X um“ – Claude ändert deinen Code
7. Diff ansehen, dann übernehmen; App starten (`npm run dev`) und prüfen

## Wenn die Entwürfe nicht zu deiner App passen

- `/design-sync` holt dein Design-System (Komponenten, Farben) in Claude Design –
  aus einem GitHub-Repo, aus Design-Dateien oder aus deinem lokalen Code
- Im Brief die Dateien nennen, die Claude benutzen soll (z. B. `RecipeCard`, `colors.ts`)

## Entwürfe wiederfinden

- `/artifacts` listet deine Artifacts: `o` öffnen, `c` Link kopieren, `d` löschen (endgültig – der Link geht für alle kaputt)
- Ctrl+] öffnet das letzte Artifact der Sitzung wieder
- In einer neuen Sitzung die Adresse angeben, sonst entsteht ein neues Artifact
- Browser soll sich nicht automatisch öffnen: Umgebungsvariable `CLAUDE_CODE_ARTIFACT_AUTO_OPEN=0`

## Umzug von claude.ai/design (schließt am 14.12.2026)

- [ ] Sicherung: im Projekt **Share → Project HTML → Project archive → Export** (zip, kostenlos, zählt nicht zum Limit)
- [ ] Design-Systeme: in Claude die Seite **Artifacts** öffnen → Banner „Claude Design lives here now“ →
      **Move team design systems** → **Move**
- [ ] Projekte einzeln (nur der Besitzer): Prüfung im Banner des Projekts starten → bestätigen → Tab offen lassen
      (danach ist die alte Kopie schreibgeschützt, nicht rückgängig zu machen; der Projekt-Umzug kommt nach und nach)
- [ ] Wissen: Chats und Kommentare ziehen **nicht** mit um; öffentliche Links auf alte Projekte gehen nach der Schließung nicht mehr

## Grenzen

- Alles zählt zum selben Nutzungs-Limit wie Claude Code
- Ein Artifact ist eine einzelne Seite ohne Backend
- Kommentare erscheinen manchmal nicht; sehr große Projekte können langsam werden; gemeinsames Bearbeiten ist noch einfach
