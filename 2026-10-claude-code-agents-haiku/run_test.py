"""Subagent-Test aus dem Video: dieselbe Prüf-Aufgabe in vier Varianten, jeweils ohne Oberfläche (claude -p).

    python run_test.py klein allein-sonnet      # 6 Dateien, eine Sitzung mit Sonnet, keine Subagents
    python run_test.py klein allein-haiku       # 6 Dateien, eine Sitzung mit Haiku, keine Subagents
    python run_test.py klein sub-haiku          # 6 Dateien, Sonnet verteilt an 3 Haiku-Subagents
    python run_test.py klein sub-sonnet         # 6 Dateien, Sonnet verteilt an 3 Sonnet-Subagents
    python run_test.py klein team-haiku         # 6 Dateien, Haiku verteilt an 3 Haiku-Subagents
    python run_test.py gross sub-haiku          # 18 Dateien, 6 Subagents
    python run_test.py gross sub-haiku 3        # dreimal hintereinander

Jeder Lauf verbraucht etwas von deinem Claude-Kontingent. Ergebnisse landen in outputs/.
Wenn `claude` nicht im PATH liegt: Umgebungsvariable CLAUDE_BIN auf die claude-Datei setzen.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ORDNER = Path(__file__).resolve().parent
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")

DATEIEN = {
    "klein": ["preise", "lager", "gutscheine", "bestellung", "kunden", "export"],
    "gross": [
        "preise", "lager", "gutscheine", "bestellung", "kunden", "export",
        "versand", "rechnung", "newsletter", "bewertungen", "sitzung", "passwort",
        "zahlung", "suche", "warenkorb", "retoure", "steuer", "benachrichtigung",
    ],
}
PRO_AGENT = {"klein": 2, "gross": 3}
MODELL = {  # Variante -> Modell der Hauptsitzung
    "allein-sonnet": "sonnet", "allein-haiku": "haiku",
    "sub-haiku": "sonnet", "sub-sonnet": "sonnet", "team-haiku": "haiku",
}
FORMAT = (
    "Antworte am Ende nur mit einer Liste, pro Fehler eine Zeile in genau diesem Format:\n"
    "DATEI:ZEILE | kurze Beschreibung des Fehlers"
)


def prompt(groesse: str, variante: str) -> str:
    pfade = [f"shop/{name}.py" for name in DATEIEN[groesse]]
    if variante.startswith("allein"):
        return (
            f"Prüfe diese {len(pfade)} Python-Dateien auf echte Fehler: falsche Logik, Widersprüche zwischen "
            "Docstring und Code, Abstürze, Sicherheitslücken. Keine Stilfragen. Ändere nichts.\n"
            f"Dateien: {', '.join(pfade)}\n" + FORMAT
        )
    schritt = PRO_AGENT[groesse]
    gruppen = [pfade[i:i + schritt] for i in range(0, len(pfade), schritt)]
    agent = "pruefer-sonnet" if variante == "sub-sonnet" else "pruefer-haiku"
    aufteilung = "\n".join(f"- Subagent {i}: {', '.join(g)}" for i, g in enumerate(gruppen, 1))
    return (
        f"Lass diese {len(pfade)} Python-Dateien auf echte Fehler prüfen. Starte dafür {len(gruppen)} {agent}-Subagents "
        f"gleichzeitig, mit dieser Aufteilung:\n{aufteilung}\n"
        "Lies die Dateien nicht selbst, sondern fasse nur die Ergebnisse der Subagents zusammen.\n" + FORMAT
    )


def lauf(groesse: str, variante: str, nummer: int) -> None:
    werkzeuge = "Read,Grep,Glob" if variante.startswith("allein") else "Read,Grep,Glob,Agent"
    befehl = [
        CLAUDE, "-p", prompt(groesse, variante),
        "--model", MODELL[variante],
        "--tools", werkzeuge,
        "--strict-mcp-config",
        "--output-format", "json",
    ]
    start = time.time()
    fertig = subprocess.run(
        befehl, cwd=ORDNER / "projekt", capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL
    )
    sekunden = time.time() - start
    ziel = ORDNER / "outputs" / f"{groesse}-{variante}-{nummer}.json"
    ziel.parent.mkdir(exist_ok=True)
    try:
        daten = json.loads(fertig.stdout)
    except json.JSONDecodeError:
        ziel.with_suffix(".fehler.txt").write_text(fertig.stdout + "\n" + fertig.stderr, encoding="utf-8")
        print(f"{ziel.stem}: keine JSON-Ausgabe, siehe {ziel.with_suffix('.fehler.txt').name}")
        return
    daten["wanduhr_sekunden"] = round(sekunden, 1)
    ziel.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
    ziel.with_suffix(".txt").write_text(str(daten.get("result", "")), encoding="utf-8")
    agenten = daten.get("subagent_stats", {}).get("spawned", 0)
    print(
        f"{ziel.stem}: {sekunden:5.1f} s | {daten.get('total_cost_usd', 0):.4f} $ rechnerisch | "
        f"{agenten} Subagents | Fehler-Flag: {daten.get('is_error')}"
    )


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in DATEIEN or sys.argv[2] not in MODELL:
        sys.exit(__doc__)
    erster = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    for i in range(erster, erster + (int(sys.argv[3]) if len(sys.argv) > 3 else 1)):
        lauf(sys.argv[1], sys.argv[2], i)
