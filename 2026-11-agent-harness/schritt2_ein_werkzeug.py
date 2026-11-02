# Schritt 2: ein Werkzeug.
# Das Modell darf "lies_datei" verlangen. Es führt nichts aus – es schreibt nur einen Wunsch (JSON).
# Unser Code führt den Wunsch aus und schickt das Ergebnis zurück.
import json
from pathlib import Path

from schritt1_nur_modell import frage_modell

ORDNER = Path("notizen")

WERKZEUGE = [{
    "type": "function",
    "function": {
        "name": "lies_datei",
        "description": "Liest eine Textdatei aus dem Notizen-Ordner und gibt ihren Inhalt zurück.",
        "parameters": {
            "type": "object",
            "properties": {"datei": {"type": "string", "description": "Dateiname, z. B. einkauf.txt"}},
            "required": ["datei"],
        },
    },
}]


def lies_datei(datei):
    return (ORDNER / datei).read_text(encoding="utf-8")


if __name__ == "__main__":
    frage = "Was steht in meiner Datei termine.txt?"
    print("Du:    ", frage)
    nachrichten = [{"role": "user", "content": frage}]

    antwort = frage_modell(nachrichten, WERKZEUGE)
    nachrichten.append(antwort)
    for aufruf in antwort.get("tool_calls", []):
        name = aufruf["function"]["name"]
        argumente = aufruf["function"]["arguments"]
        print("Modell möchte:", name, json.dumps(argumente, ensure_ascii=False))
        ergebnis = lies_datei(**argumente)            # HIER passiert die echte Arbeit – in unserem Code
        print("Harness führt aus, Ergebnis:", repr(ergebnis))
        nachrichten.append({"role": "tool", "tool_name": name, "content": ergebnis})

    antwort = frage_modell(nachrichten, WERKZEUGE)     # zweiter Aufruf: jetzt mit dem Ergebnis
    print("Modell:", antwort["content"])
