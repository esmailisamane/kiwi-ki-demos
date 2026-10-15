# Claude Code Remote Control: Push aufs Handy und Notification Hook unter Windows im Test

Code und echte Ergebnisse zum Video **„Claude Code Remote Control: Push aufs Handy + Notification Hook unter Windows“**
(Kanal KIwi – KI einfach erklärt). Kein offizielles Projekt von Anthropic.

Die Frage: **Wie meldet sich Claude Code, wenn es dich braucht – auf dem Handy und auf dem Windows-PC?**
Alles kostenlos mit dem vorhandenen Abo (Remote Control gibt es ab Claude Pro) und der kostenlosen Claude-App.

Getestet am 15.10.2026 mit Claude Code 2.1.300 unter Windows 11, Claude Pro, Android-Handy (Xiaomi), Modell Haiku 5.5.

## Was hier liegt

| Datei | Wozu |
|---|---|
| `tests.py` | kleine Test-Suite (8 Tests, ca. 20 s), damit Claude etwas tun muss, das eine Freigabe braucht |
| `.claude/settings.json` | Projekt-Einstellungen: Haiku, beide Push-Schalter, Hooks für Notification, PermissionRequest und Stop |
| `.claude/hooks/log_event.ps1` | schreibt jedes Ereignis mit Millisekunden in `hooks.log` und zeigt bei Notification eine Windows-Benachrichtigung (Toast) – ohne Zusatzmodul |
| `.claude/hooks/messagebox-offiziell.json` | das offizielle Windows-Beispiel aus der Doku (Dialogfenster statt Toast) |
| `outputs/` | echte Ausgaben: `hooks.log`, Server-Ausgabe, Bildschirme aus Claude Code |

## So richtest du es ein (Windows)

1. Claude Code aktuell halten: `claude update` (mindestens 2.1.299 – ältere Versionen haben die Push-Schalter in
   `/config` falsch gespeichert).
2. Claude-App aufs Handy (kostenlos), mit demselben Konto anmelden, Benachrichtigungen erlauben.
3. Im Projektordner: `claude remote-control` (Server) – oder in einer laufenden Sitzung `/rc`.
4. Im Handy: Claude-App → **Code** → Sitzung mit grünem Punkt öffnen.
5. Push einschalten: in `/config` nach „push“ suchen, **Push when actions required** und **Push when Claude decides**
   auf `true`. Vom Handy aus geht es auch als Nachricht: `/config inputNeededNotifEnabled=true` und
   `/config agentPushNotifEnabled=true`.
6. Windows-Hook: Inhalt von `.claude/settings.json` (Abschnitt `hooks`) und `.claude/hooks/log_event.ps1` in dein
   Projekt kopieren – oder das offizielle Beispiel in `~/.claude/settings.json`.

## Ergebnisse

**Push aufs Handy**
- Push angefordert (`Mobile push requested`, im Protokoll `pushSent: true`) heißt noch nicht angekommen: Bei uns kam
  zuerst nichts an. Erst nachdem wir in der Claude-App unter Einstellungen → Benachrichtigungen alles eingeschaltet,
  bei Xiaomi die Benachrichtigungen der App erlaubt und die App einmal ganz geschlossen und neu geöffnet hatten, kamen
  die Pushs an.
- Danach kam der Push innerhalb weniger Sekunden. Bei uns erschien die Benachrichtigung erst, nachdem wir die
  Claude-App verlassen hatten (im Handy-Video ca. 4 s nach dem Wechsel zum Startbildschirm). Welcher der drei Schritte
  das Problem gelöst hat, wissen wir nicht – wir haben alle drei auf einmal gemacht.

**Freigabe vom Handy** (Zeit von der Frage bis die Freigabe am PC ankommt, gemessen am PC):

| Durchgang | Anfrage → Freigabe | Bemerkung |
|---|---|---|
| 1 | 3,1 s | App war noch offen |
| 2 | 35,3 s | Handy auf dem Startbildschirm: Push, antippen, App lädt, „Allow“ |
| 3 | 38,0 s | wie 2 |

Alle drei Freigaben kamen an, der Befehl lief danach auf dem PC. Die Zeit enthält unsere eigene Reaktion.

**Windows Notification Hook** (`hooks.log`):
- `permission_prompt`: 6,0 s / 5,9 s (Remote-Control-Sitzung) und 6,1 s (normale Terminal-Sitzung) nach der Frage –
  passt zur Doku („about six seconds“). Antwortet man schneller, kommt keine Meldung.
- `idle_prompt`: 60,6 s nach der letzten Antwort in der Terminal-Sitzung. In der Remote-Control-Server-Sitzung kam bei
  uns kein `idle_prompt`.
- Das offizielle MessageBox-Beispiel funktioniert, öffnet aber ein Dialogfenster (kann hinter dem Terminal landen). Unser
  Skript zeigt stattdessen eine normale Windows-Benachrichtigung.

**Was wir nicht getestet haben:** Anruf-Plugins wie [call-me](https://github.com/ZeframLou/call-me) – die brauchen
Twilio oder Telnyx (Telefonnummer + Minutenpreis) und einen OpenAI-Schlüssel, also kostenpflichtig.

## Sicherheit

Während Remote Control verbunden ist, wird das Sitzungsprotokoll (deine Nachrichten, Claudes Antworten, Werkzeug-
Aufrufe) auf Servern von Anthropic gespeichert; ausgeführt wird weiter nur auf deinem PC
([Doku](https://code.claude.com/docs/en/remote-control)). Eine Freigabe auf dem Handy ist eine echte Freigabe – lies den
Befehl, bevor du tippst, und wähle nicht vorschnell „don't ask again“.

## Quellen

- https://code.claude.com/docs/en/remote-control
- https://code.claude.com/docs/en/hooks-guide und https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/changelog (2.1.299, 2.1.300)
