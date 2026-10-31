---
name: commit-check
description: Prüft gestagte Änderungen vor einem Commit auf API-Keys, Passwörter und private Daten. Verwenden, wenn der Nutzer committen oder pushen will.
---

Lies vor jedem Commit `git diff --cached`. Findest du einen Key, ein Passwort, eine E-Mail-Adresse oder einen persönlichen Pfad: nicht committen, sondern die Stellen zeigen.
