# Schritt 4: Freigabe – gefährliche Werkzeuge nur mit deinem Ja.
# Neu: schreibe_datei und loesche_datei. Bevor der Harness sie ausführt, fragt er dich.
# Dazu ein Zaun: Kein Werkzeug darf außerhalb des Notizen-Ordners arbeiten.
import json
import sys

import schritt3_schleife as s3
from schritt1_nur_modell import frage_modell

ORDNER = s3.ORDNER.resolve()
GEFAEHRLICH = {"schreibe_datei", "loesche_datei"}   # diese Werkzeuge brauchen dein Ja


def im_ordner(datei):
    """Der Zaun: Wohin zeigt der Pfad wirklich? Nur Ziele im Notizen-Ordner sind erlaubt."""
    pfad = (ORDNER / datei).resolve()
    if not pfad.is_relative_to(ORDNER):
        raise PermissionError(f"{datei} liegt außerhalb des Notizen-Ordners")
    return pfad


def lies_datei(datei):
    pfad = im_ordner(datei)
    if not pfad.is_file():
        return f"FEHLER: Datei {datei} gibt es nicht. Vorhandene Dateien: " + s3.liste_dateien()
    return pfad.read_text(encoding="utf-8")


def schreibe_datei(datei, inhalt):
    im_ordner(datei).write_text(inhalt, encoding="utf-8")
    return f"{datei} gespeichert."


def loesche_datei(datei):
    im_ordner(datei).unlink()
    return f"{datei} gelöscht."


WERKZEUGE = s3.WERKZEUGE + [
    s3.werkzeug("schreibe_datei", "Schreibt Text in eine Datei im Notizen-Ordner.",
                datei="Dateiname", inhalt="Der komplette neue Inhalt"),
    s3.werkzeug("loesche_datei", "Löscht eine Datei im Notizen-Ordner.", datei="Dateiname"),
]
AUSFUEHRBAR = {"liste_dateien": s3.liste_dateien, "lies_datei": lies_datei,
               "schreibe_datei": schreibe_datei, "loesche_datei": loesche_datei}


def frage_nutzer(text):
    try:
        antwort = input(text)
    except EOFError:                # keine Eingabe mehr = Nein
        antwort = "n"
    if not sys.stdin.isatty():      # Antwort kam aus einer Datei: zur Kontrolle mit anzeigen
        print(antwort)
    return antwort.strip().lower()


def fuehre_aus(name, argumente):
    if name not in AUSFUEHRBAR:
        return f"FEHLER: Werkzeug {name} gibt es nicht."
    if name in GEFAEHRLICH:
        ja = frage_nutzer(f"  ?  Darf der Agent {name}({json.dumps(argumente, ensure_ascii=False)})? [j/n] ")
        if ja != "j":
            return "ABGELEHNT: Der Nutzer hat das nicht erlaubt. Mach es nicht auf anderem Weg."
    try:
        return AUSFUEHRBAR[name](**argumente)
    except (PermissionError, TypeError, OSError) as fehler:
        return f"FEHLER: {fehler}"


def agent(aufgabe):
    nachrichten = [{"role": "system", "content": s3.SYSTEM}, {"role": "user", "content": aufgabe}]
    while True:
        antwort = frage_modell(nachrichten, WERKZEUGE)
        nachrichten.append(antwort)
        if not antwort.get("tool_calls"):
            return antwort["content"]
        for aufruf in antwort["tool_calls"]:
            name, argumente = aufruf["function"]["name"], aufruf["function"]["arguments"] or {}
            print(f"  -> {name}({json.dumps(argumente, ensure_ascii=False)})")
            ergebnis = fuehre_aus(name, argumente)
            print(f"  <- {ergebnis.strip()[:70]!r}")
            nachrichten.append({"role": "tool", "tool_name": name, "content": ergebnis})


if __name__ == "__main__":
    aufgabe = " ".join(sys.argv[1:]) or "Lösche bitte die Datei entwurf_alt.txt."
    print("Du:    ", aufgabe)
    print("Agent: ", agent(aufgabe))
