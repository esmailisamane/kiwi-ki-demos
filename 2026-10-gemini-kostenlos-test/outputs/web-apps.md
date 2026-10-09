# Antworten der Web-Apps (abgeschrieben aus unseren Bildschirmaufnahmen, 07.10.2026)

Jede Aufgabe in einem neuen Chat, Standard-Einstellungen, kostenlose Konten.

## Gemini-App – Modell „3.5 Flash-Lite“ (Menü zeigte außerdem 3.6 Flash, 3.1 Pro, Extended thinking)

**Aufgabe 1:** „Ausgabe: 4.0“ · „Ist das Ergebnis richtig? Nein, das tatsächliche arithmetische Mittel von [4, 8, 6] ist 6.0.“ ·
„1. Falscher Startindex: range(1, len(zahlen)) beginnt bei Index 1 statt bei 0. Das erste Element (4 an Index 0) wird komplett
ignoriert.“ · „2. Falsche Division: Es wird durch die Gesamtlänge der Liste (3) geteilt, obwohl durch die Anzahl der addierten
Elemente (2) geteilt werden müsste.“ · Korrigierter Code: `return sum(zahlen) / len(zahlen)`
→ Fehler und Korrektur richtig; Ausgabe falsch (richtig: 4.666666666666667); Punkt 2 ist kein Fehler im Sinne der Aufgabe.

**Aufgabe 2:** „5“ → richtig.

**Aufgabe 3:** „Am 9. Oktober 2026 ändert sich für Nutzer der kostenlosen Version von Gemini im Rahmen der allgemeinen Tarif- und
Funktionsanpassungen nichts Grundlegendes an den bekannten Free-Nutzungsbedingungen. Der Zugang zu den Standard-Modellen und den
grundlegenden KI-Funktionen bleibt für kostenlose Anwender weiterhin im gewohnten Rahmen bestehen. Eventuelle Anpassungen betreffen
primär erweiterte Rechenkontingente oder Tarifstrukturen für optionale Bezahl-Abos.“
→ falsch (laut Google gibt es ab 9.10. ohne Abo nur noch Flash-Lite). Keine Websuche sichtbar.

## ChatGPT – kostenloses Konto, „Nachdenken“ aus

**Aufgabe 1:** „Die Ausgabe ist: 4.666666666666667“ · „Das Ergebnis ist falsch.“ · „Fehler: range(1, len(zahlen)) startet bei
Index 1 und überspringt damit die 4 an Index 0.“ · „Richtig wäre: for i in range(len(zahlen)):“ · „Dann ist der Durchschnitt 6.0.“
→ vollständig richtig.

Danach meldete ChatGPT: „Dateien, Bilder und Datenanalyse sind nicht verfügbar, bis dein Nutzungslimit morgen um 03:12
zurückgesetzt wird. Chatte nur mit Text weiter …“

**Aufgabe 2:** „5“ → richtig (Screenshot; ChatGPT hing vorher mehrmals).

**Aufgabe 3** (neuer Versuch am 8.10. morgens, nach Zurücksetzen des Limits): „Ab dem 9. Oktober 2026 können Nutzer von Gemini ohne
kostenpflichtiges Google-AI-Abo nur noch das Modell Flash-Lite verwenden. Flash und Pro fallen für kostenlose Privatkonten weg, sodass
anspruchsvollere Aufgaben künftig stärker eingeschränkt sind.“ + Quelle theverge.com (+1) → richtig, mit Websuche.
(Am Abend vorher hing ChatGPT nach dem Gratis-Limit für Datenanalyse mehrmals.)

## Google AI Studio – kostenloses Konto, Gemini 3.1 Pro Preview (8.10.2026)

In der Modell-Liste war „Gemini 3 Flash Preview“ als „Paid“ markiert; Gemini 3.8 Flash und 3.1 Pro Preview nicht – beide haben
geantwortet. Standard-Einstellungen: Denk-Stufe hoch, „Grounding with Google Search“ an, „Temporary chat“.

**Aufgabe 1:** „Ausgabe: 4.666666666666667“ · „Nein. Der korrekte Durchschnitt von 4, 8 und 6 wäre 6.0.“ · „Die Schleife beginnt bei
range(1, ...), wodurch das allererste Element der Liste (Index 0, hier die 4) übersprungen wird.“ · „Korrektur: Es muss
range(0, len(zahlen)) oder noch besser einfach for zahl in zahlen: heißen.“ → richtig.

**Aufgabe 2:** „5“ → richtig.

**Aufgabe 3:** „Ab dem 9. Oktober 2026 können Nutzer der kostenlosen Gemini-Version nur noch auf das Basismodell „Flash-Lite“
zugreifen. Der bisherige Gratis-Zugang zu den deutlich leistungsstärkeren Modellen „Flash“ und „Pro“ entfällt an diesem Datum für
private Konten vollständig. Um diese fortschrittlicheren KI-Modelle weiterhin nutzen zu können, ist künftig der Abschluss eines
kostenpflichtigen Abonnements wie AI Plus oder AI Pro erforderlich.“ + 4 Quellen (borncity.com, lukashackbarth.de, schmidtsblog.de,
futurezone.at) → richtig (für die App).
