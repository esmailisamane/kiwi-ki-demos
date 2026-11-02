"""Mini-Harness: macht aus einem lokalen Sprachmodell einen kleinen Agenten für deinen Notizen-Ordner.

Start:  python mini_harness.py        (vorher: Ollama starten und  ollama pull llama3.2:3b)
Ende:   "ende" eintippen

Alles, was hier steht, ist der Harness. Das Modell selbst liefert nur Text – oder den Wunsch, ein Werkzeug zu benutzen.
"""
import json
import shutil
import sys
import time
import urllib.request
from pathlib import Path

MODELL = "llama3.2:3b"
URL = "http://localhost:11434/api/chat"
ORDNER = Path("notizen").resolve()           # nur hier darf der Agent arbeiten
GEDAECHTNIS = Path("GEDAECHTNIS.md")          # Notizen, die eine Sitzung überleben (wie CLAUDE.md)
SICHERUNG = Path("sicherung")                 # Kopien vor jeder Änderung (wie Checkpoints)
FREIGABE_NOETIG = {"schreibe_datei", "loesche_datei", "merke"}   # diese Werkzeuge brauchen dein Ja
MAX_SCHRITTE = 8                              # Notbremse: höchstens 8 Modell-Aufrufe pro Aufgabe
KONTEXT_GRENZE = 6000                         # Zeichen; darüber fasst der Harness das Gespräch zusammen

REGELN = ("Du bist ein Assistent für den Notizen-Ordner des Nutzers. Du arbeitest in einer Schleife: "
          "Du kannst nacheinander mehrere Werkzeuge aufrufen und bekommst jedes Ergebnis zurück. "
          "Erfinde nie Dateiinhalte – lies sie. Wenn der Nutzer sagt, du sollst dir etwas merken, "
          "rufe merke auf. Wenn du fertig bist, antworte kurz auf Deutsch.")


# ---------- 1. Das Modell fragen ----------
def frage_modell(nachrichten, werkzeuge=None):
    daten = {"model": MODELL, "messages": nachrichten, "stream": False,
             "options": {"temperature": 0, "num_ctx": 8192}}
    if werkzeuge:
        daten["tools"] = werkzeuge
    anfrage = urllib.request.Request(URL, data=json.dumps(daten).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(anfrage, timeout=600) as antwort:
        return json.load(antwort)["message"]


# ---------- 2. Werkzeuge: Beschreibung für das Modell + echter Code ----------
def werkzeug(name, beschreibung, **parameter):
    return {"type": "function", "function": {
        "name": name, "description": beschreibung,
        "parameters": {"type": "object",
                       "properties": {p: {"type": "string", "description": t} for p, t in parameter.items()},
                       "required": list(parameter)}}}


WERKZEUGE = [
    werkzeug("liste_dateien", "Zeigt alle Dateinamen im Notizen-Ordner."),
    werkzeug("lies_datei", "Liest eine Datei aus dem Notizen-Ordner. Kennst du den genauen Namen nicht, "
             "rufe zuerst liste_dateien auf.", datei="Dateiname, z. B. einkauf.txt"),
    werkzeug("schreibe_datei", "Schreibt Text in eine Datei im Notizen-Ordner.",
             datei="Dateiname", inhalt="Der komplette neue Inhalt"),
    werkzeug("loesche_datei", "Löscht eine Datei im Notizen-Ordner.", datei="Dateiname"),
    werkzeug("merke", "Speichert eine kurze Notiz dauerhaft im Gedächtnis.", notiz="Was du dir merken sollst"),
]


def im_ordner(datei):
    """Der Zaun: Wohin zeigt der Pfad wirklich? Nur Ziele im Notizen-Ordner sind erlaubt."""
    pfad = (ORDNER / datei).resolve()
    if not pfad.is_relative_to(ORDNER):
        raise PermissionError(f"{datei} liegt außerhalb des Notizen-Ordners")
    return pfad


def liste_dateien():
    return ", ".join(sorted(p.name for p in ORDNER.iterdir()))


def lies_datei(datei):
    pfad = im_ordner(datei)
    if not pfad.is_file():
        return f"FEHLER: Datei {datei} gibt es nicht. Vorhandene Dateien: " + liste_dateien()
    return pfad.read_text(encoding="utf-8")


def sichern(pfad):
    """Wie ein Checkpoint: Bevor eine Datei geändert oder gelöscht wird, legen wir eine Kopie ab."""
    if pfad.exists():
        SICHERUNG.mkdir(exist_ok=True)
        shutil.copy2(pfad, SICHERUNG / f"{time.strftime('%H%M%S')}_{pfad.name}")


def schreibe_datei(datei, inhalt):
    sichern(im_ordner(datei))
    im_ordner(datei).write_text(inhalt, encoding="utf-8")
    return f"{datei} gespeichert."


def loesche_datei(datei):
    sichern(im_ordner(datei))
    im_ordner(datei).unlink()
    return f"{datei} gelöscht."


def merke(notiz):
    with GEDAECHTNIS.open("a", encoding="utf-8") as datei:
        datei.write(f"- {notiz}\n")
    return "Gemerkt."


AUSFUEHRBAR = {"liste_dateien": liste_dateien, "lies_datei": lies_datei, "schreibe_datei": schreibe_datei,
               "loesche_datei": loesche_datei, "merke": merke}


# ---------- 3. Freigabe: gefährliche Werkzeuge nur mit Ja ----------
def frage_nutzer(text):
    try:
        antwort = input(text)
    except EOFError:                # keine Eingabe mehr = Nein bzw. Ende
        antwort = "ende"
    if not sys.stdin.isatty():      # Antwort kam aus einer Datei: zur Kontrolle mit anzeigen
        print(antwort)
    return antwort.strip()


def fuehre_aus(name, argumente):
    if name not in AUSFUEHRBAR:
        return f"FEHLER: Werkzeug {name} gibt es nicht."
    if name in FREIGABE_NOETIG:
        ja = frage_nutzer(f"  ?  Darf der Agent {name}({json.dumps(argumente, ensure_ascii=False)})? [j/n] ")
        if ja.lower() != "j":
            return "ABGELEHNT: Der Nutzer hat das nicht erlaubt. Mach es nicht auf anderem Weg."
    try:
        return AUSFUEHRBAR[name](**argumente)
    except (PermissionError, TypeError, OSError) as fehler:
        return f"FEHLER: {fehler}"


# ---------- 4. Kontext: Gedächtnis laden, zu langes Gespräch zusammenfassen ----------
def system_nachricht():
    text = REGELN + "\nDateien im Ordner: " + liste_dateien()
    if GEDAECHTNIS.exists():
        text += "\nDein Gedächtnis aus früheren Sitzungen:\n" + GEDAECHTNIS.read_text(encoding="utf-8")
    return {"role": "system", "content": text}


def groesse(nachrichten):
    return len(json.dumps(nachrichten, ensure_ascii=False))


def zusammenfassen(nachrichten):
    """Ersetzt das bisherige Gespräch durch eine kurze Zusammenfassung (wie /compact)."""
    vorher = groesse(nachrichten)
    verlauf = "\n".join(f"{n['role']}: {n.get('content', '')}" for n in nachrichten[1:])
    bitte = [{"role": "user", "content": "Fasse dieses Gespräch in höchstens 5 Stichpunkten zusammen. "
              "Behalte Dateinamen, Daten, Uhrzeiten und Entscheidungen.\n\n" + verlauf}]
    kurz = frage_modell(bitte)["content"]
    neu = [system_nachricht(), {"role": "system", "content": "Zusammenfassung des bisherigen Gesprächs:\n" + kurz}]
    print(f"  [Harness] Kontext zu groß: {vorher} -> {groesse(neu)} Zeichen zusammengefasst")
    print("  [Harness] Zusammenfassung:", " ".join(kurz.split())[:160])
    return neu


# ---------- 5. Die Agenten-Schleife ----------
def agent(nachrichten):
    for schritt in range(1, MAX_SCHRITTE + 1):
        antwort = frage_modell(nachrichten, WERKZEUGE)
        nachrichten.append(antwort)
        if not antwort.get("tool_calls"):        # keine Werkzeug-Wünsche mehr = fertig
            return antwort["content"]
        for aufruf in antwort["tool_calls"]:
            name, argumente = aufruf["function"]["name"], aufruf["function"]["arguments"] or {}
            print(f"  -> Schritt {schritt}: {name}({json.dumps(argumente, ensure_ascii=False)})")
            ergebnis = fuehre_aus(name, argumente)
            print(f"  <- {ergebnis.strip()[:70]!r}")
            nachrichten.append({"role": "tool", "tool_name": name, "content": ergebnis})
    return f"[Harness] Stopp nach {MAX_SCHRITTE} Schritten – die Aufgabe ist nicht fertig."


def main():
    nachrichten = [system_nachricht()]
    if GEDAECHTNIS.exists():
        print(f"[Harness] Gedächtnis geladen: {len(GEDAECHTNIS.read_text(encoding='utf-8').splitlines())} Notizen")
    while True:
        aufgabe = frage_nutzer("Du: ")
        if aufgabe.lower() in ("ende", ""):
            break
        if groesse(nachrichten) > KONTEXT_GRENZE:
            nachrichten = zusammenfassen(nachrichten)
        nachrichten.append({"role": "user", "content": aufgabe})
        print("Agent:", agent(nachrichten))


if __name__ == "__main__":
    main()
