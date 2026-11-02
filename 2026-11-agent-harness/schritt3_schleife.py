# Schritt 3: die Schleife – jetzt ist es ein Agent.
# Zwei Werkzeuge. Der Harness fragt das Modell so lange, bis es keine Werkzeuge mehr verlangt.
import json
from pathlib import Path

from schritt1_nur_modell import frage_modell

ORDNER = Path("notizen")

REGELN = ("Du bist ein Assistent für den Notizen-Ordner des Nutzers. Du arbeitest in einer Schleife: "
          "Du kannst nacheinander mehrere Werkzeuge aufrufen und bekommst jedes Ergebnis zurück. "
          "Erfinde nie Dateiinhalte – lies sie. Wenn du fertig bist, antworte kurz auf Deutsch.")


def werkzeug(name, beschreibung, **parameter):
    """Baut die Beschreibung eines Werkzeugs, so wie das Modell sie lesen kann."""
    return {"type": "function", "function": {
        "name": name, "description": beschreibung,
        "parameters": {"type": "object",
                       "properties": {p: {"type": "string", "description": t} for p, t in parameter.items()},
                       "required": list(parameter)}}}


WERKZEUGE = [
    werkzeug("liste_dateien", "Zeigt alle Dateinamen im Notizen-Ordner."),
    werkzeug("lies_datei", "Liest eine Datei aus dem Notizen-Ordner. Kennst du den genauen Namen nicht, "
             "rufe zuerst liste_dateien auf.", datei="Dateiname, z. B. einkauf.txt"),
]


def liste_dateien():
    return ", ".join(sorted(p.name for p in ORDNER.iterdir()))


def lies_datei(datei):
    pfad = ORDNER / datei
    if not pfad.is_file():
        # Fehler als Text zurück – mit einem Hinweis, was das Modell jetzt tun kann
        return f"FEHLER: Datei {datei} gibt es nicht. Vorhandene Dateien: " + liste_dateien()
    return pfad.read_text(encoding="utf-8")


AUSFUEHRBAR = {"liste_dateien": liste_dateien, "lies_datei": lies_datei}

# Die Lösung aus unserem Test: Der Harness legt die Dateiliste gleich zu Beginn in den Kontext.
SYSTEM = REGELN + " Dateien im Ordner: " + liste_dateien() + "."


def agent(aufgabe):
    nachrichten = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": aufgabe}]
    while True:                                      # <- die Agenten-Schleife
        antwort = frage_modell(nachrichten, WERKZEUGE)
        nachrichten.append(antwort)
        aufrufe = antwort.get("tool_calls")
        if not aufrufe:                              # keine Werkzeug-Wünsche mehr = fertig
            return antwort["content"]
        for aufruf in aufrufe:
            name = aufruf["function"]["name"]
            argumente = aufruf["function"]["arguments"] or {}
            print(f"  -> {name}({json.dumps(argumente, ensure_ascii=False)})")
            funktion = AUSFUEHRBAR.get(name)
            ergebnis = funktion(**argumente) if funktion else f"FEHLER: Werkzeug {name} gibt es nicht."
            print(f"  <- {ergebnis.strip()[:70]!r}")
            nachrichten.append({"role": "tool", "tool_name": name, "content": ergebnis})


if __name__ == "__main__":
    aufgabe = "Wann ist mein Zahnarzttermin? Ich weiß nicht mehr, in welcher Datei er steht."
    print("Du:    ", aufgabe)
    print("Agent: ", agent(aufgabe))
