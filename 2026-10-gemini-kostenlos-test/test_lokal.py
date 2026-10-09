"""Die drei Testaufgaben aus dem Video lokal mit Ollama ausführen und automatisch prüfen.

    ollama pull llama3.2:3b
    python test_lokal.py            # 3 Durchläufe pro Aufgabe
    python test_lokal.py 5 qwen3:4b # 5 Durchläufe, anderes Modell

Nur Standardbibliothek. Antworten landen in outputs/<modell>/aufgabeN_laufM.txt.
Die Prüfung ist bewusst einfach (Stichworte) - lies die Antworten trotzdem selbst.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

RUNS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
MODEL = sys.argv[2] if len(sys.argv) > 2 else "llama3.2:3b"
HERE = Path(__file__).parent


def ask(prompt: str) -> str:
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request("http://localhost:11434/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as resp:
        return json.load(resp)["response"].strip()


def check(task: int, answer: str) -> str:
    if task == 1:  # Fehler: Schleife startet bei 1 -> erste Zahl fehlt (richtig wäre range(len(zahlen)))
        return "Fehler gefunden" if re.search(r"range\(1|bei 1|mit 1|erste (Zahl|Element)", answer) else "Fehler NICHT gefunden"
    if task == 2:  # "Erdbeermarmelade".lower().count("e") == 5
        numbers = re.findall(r"\d+", answer)
        return "richtig (5)" if numbers[:1] == ["5"] else f"falsch ({numbers[0] if numbers else answer[:30]})"
    return "von Hand prüfen (Aktualität)"


out = HERE / "outputs" / MODEL.replace(":", "_")
out.mkdir(parents=True, exist_ok=True)
for task in (1, 2, 3):
    prompt = (HERE / "prompts" / f"aufgabe{task}.txt").read_text(encoding="utf-8")
    for run in range(1, RUNS + 1):
        answer = ask(prompt)
        (out / f"aufgabe{task}_lauf{run}.txt").write_text(answer + "\n", encoding="utf-8")
        print(f"Aufgabe {task}, Lauf {run}: {check(task, answer)}")
