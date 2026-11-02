# Schritt 1: nur das Modell – kein Harness.
# Wir schicken eine Frage an das lokale Modell und drucken die Antwort. Mehr nicht.
import json
import urllib.request

MODELL = "llama3.2:3b"
URL = "http://localhost:11434/api/chat"   # Ollama läuft lokal auf diesem Port


def frage_modell(nachrichten, werkzeuge=None):
    daten = {
        "model": MODELL,
        "messages": nachrichten,   # das ganze Gespräch – das Modell selbst merkt sich nichts
        "stream": False,           # eine fertige Antwort statt Wort für Wort
        "options": {"temperature": 0, "num_ctx": 8192},   # ruhig antworten, 8.192 Tokens Platz
    }
    if werkzeuge:
        daten["tools"] = werkzeuge
    anfrage = urllib.request.Request(URL, data=json.dumps(daten).encode("utf-8"),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(anfrage, timeout=600) as antwort:
        return json.load(antwort)["message"]


if __name__ == "__main__":
    frage = "Was steht in meiner Datei termine.txt?"
    print("Du:    ", frage)
    antwort = frage_modell([{"role": "user", "content": frage}])
    print("Modell:", antwort["content"])
