"""Wertet alle Läufe in outputs/ aus: Zeit, Verbrauch, gefundene der eingebauten Fehler.

Start (im Ordner des Videos): python auswertung/auswerten.py [-v]

Ein Treffer zählt, wenn eine gemeldete Zeile in der richtigen Datei innerhalb der Funktion des Fehlers liegt
(Zeilen der Funktion werden mit ast bestimmt; wo zwei Fehler in einer Funktion stecken, entscheidet ein Stichwort).
Läufe mit "klein" werden gegen die Fehler 1-12 gezählt, Läufe mit "gross" gegen alle 36.
Mit -v werden alle Meldungen gezeigt, die zu keinem eingebauten Fehler passen (zum Nachlesen von Hand).
"""
import ast
import io
import json
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
ORDNER = Path(__file__).resolve().parent.parent
LOESUNG = json.loads((ORDNER / "auswertung" / "loesung.json").read_text(encoding="utf-8"))
ZEILE = re.compile(r"([a-z_]+\.py)`?\s*:\s*(\d+)(?:\s*[-–]\s*\d+)?`?\s*\|\s*(.+)")


def funktionszeilen(datei: str) -> dict:
    baum = ast.parse((ORDNER / "projekt" / "shop" / datei).read_text(encoding="utf-8"))
    return {
        k.name: (k.lineno, k.end_lineno)
        for k in ast.walk(baum)
        if isinstance(k, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


SPANNEN = {d: funktionszeilen(d) for d in {f["datei"] for f in LOESUNG}}


def passender_fehler(datei: str, zeile: int, text: str, erlaubt: set):
    for fehler in LOESUNG:
        if fehler["nr"] not in erlaubt or fehler["datei"] != datei:
            continue
        in_funktion = any(
            SPANNEN[datei][f][0] - 1 <= zeile <= SPANNEN[datei][f][1] + 1 for f in fehler["funktionen"]
        )
        if in_funktion and re.search(fehler.get("muster", ""), text, re.I):
            return fehler["nr"]
    return None


def main() -> None:
    print(f"{'Lauf':<22}{'Zeit':>8}{'Kosten*':>10}{'Agents':>8}{'gefunden':>10}{'sonstige':>10}   Ausgabe-Tokens je Modell")
    for datei in sorted((ORDNER / "outputs").glob("*.json")):
        daten = json.loads(datei.read_text(encoding="utf-8"))
        erlaubt = set(range(1, 13)) if "klein" in datei.stem else {f["nr"] for f in LOESUNG}
        gefunden, sonstige = set(), []
        for name, zeile, text in ZEILE.findall(str(daten.get("result", ""))):
            nr = passender_fehler(name, int(zeile), text, erlaubt)
            if nr:
                gefunden.add(nr)
            else:
                sonstige.append(f"{name}:{zeile} | {text.strip()}")
        modelle = ", ".join(
            f"{m.replace('claude-', '')}: {u.get('outputTokens', 0)}" for m, u in daten.get("modelUsage", {}).items()
        )
        print(
            f"{datei.stem:<22}{daten.get('wanduhr_sekunden', 0):>7.1f}s{daten.get('total_cost_usd', 0):>9.4f}$"
            f"{daten.get('subagent_stats', {}).get('spawned', 0):>8}{len(gefunden):>7}/{len(erlaubt)}"
            f"{len(sonstige):>10}   {modelle}"
        )
        fehlend = sorted(erlaubt - gefunden)
        if fehlend:
            print(f"{'':<22}nicht gefunden: {', '.join(f'F{n:02d}' for n in fehlend)}")
        if "-v" in sys.argv:
            for s in sonstige:
                print(f"{'':<22}+ {s}")
    print("\n* rechnerische API-Listenpreise laut Claude Code; im Abo wird das nicht einzeln berechnet, es zeigt den Verbrauch.")


if __name__ == "__main__":
    main()
