"""Alle Demo-Läufe aus dem Video nacheinander – in einer frischen Kopie des Ordners; Ausgaben landen in outputs/.

Start (im Ordner 2026-11-agent-harness):  python demo_laeufe.py
Die Antworten (j/n, nächste Frage) kommen hier aus dem Skript statt von der Tastatur.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

QUELLE = Path(__file__).resolve().parent
LABOR = Path(tempfile.gettempdir()) / "harness-labor"
AUSGABE = QUELLE / "outputs"


def lauf(name, argumente, eingabe=""):
    print("==", name, flush=True)
    umgebung = dict(os.environ, PYTHONIOENCODING="utf-8")
    ergebnis = subprocess.run([sys.executable, *argumente], cwd=LABOR, input=eingabe.encode("utf-8"),
                              capture_output=True, env=umgebung, timeout=1800)
    text = (ergebnis.stdout + ergebnis.stderr).decode("utf-8")
    (AUSGABE / f"{name}.txt").write_text(text, encoding="utf-8")
    print(text, flush=True)


def main():
    shutil.rmtree(LABOR, ignore_errors=True)
    shutil.copytree(QUELLE / "notizen", LABOR / "notizen")
    for datei in QUELLE.glob("*.py"):
        shutil.copy2(datei, LABOR)
    (LABOR / "geheim.txt").write_text("PASSWORT=nur-ein-Beispiel\n", encoding="utf-8")   # AUSSERHALB von notizen/
    AUSGABE.mkdir(exist_ok=True)

    lauf("1_nur_modell", ["schritt1_nur_modell.py"])
    lauf("2_ein_werkzeug", ["schritt2_ein_werkzeug.py"])
    lauf("3_schleife", ["schritt3_schleife.py"])
    lauf("4a_loeschen_nein", ["schritt4_freigabe.py", "Lösche bitte die Datei entwurf_alt.txt."], "n\n")
    lauf("4b_loeschen_ja", ["schritt4_freigabe.py", "Lösche bitte die Datei entwurf_alt.txt."], "j\n")
    lauf("4c_zaun", ["schritt4_freigabe.py", "Lies die Datei ../geheim.txt"])
    shutil.copy2(QUELLE / "notizen" / "entwurf_alt.txt", LABOR / "notizen")      # wieder da für die nächsten Läufe

    lauf("5a_sitzung1_merken", ["mini_harness.py"],
         "Merk dir: Meine Einkaufsliste soll immer alphabetisch sortiert sein.\nj\nende\n")
    lauf("5b_sitzung2_blind_ja", ["mini_harness.py"], "Sortiere meine Einkaufsliste so, wie ich es mag.\nj\nj\nj\nende\n")
    danach = (LABOR / "notizen" / "einkauf.txt").read_text(encoding="utf-8")
    sicherungen = [f"{p.name}: {p.read_text(encoding='utf-8')!r}" for p in sorted((LABOR / "sicherung").glob("*"))]
    (AUSGABE / "5b_einkauf_danach_und_sicherung.txt").write_text(
        f"einkauf.txt danach: {danach!r}\nSicherungen:\n" + "\n".join(sicherungen) + "\n", encoding="utf-8")
    shutil.copy2(QUELLE / "notizen" / "einkauf.txt", LABOR / "notizen")          # Liste aus der Sicherung zurück

    lauf("5c_alles_zusammenlegen", ["mini_harness.py"],
         "Mach aus allen Dateien eine einzige Datei alles.txt und lösch danach die alten.\n" + "n\n" * 6 + "ende\n")
    lauf("5d_zusammenfassen", ["-c", "import mini_harness as m; m.KONTEXT_GRENZE = 1500; m.main()"],
         "Was steht in termine.txt?\nWas steht in ideen.txt?\nWas steht in einkauf.txt?\nWann war nochmal der Zahnarzt?\nende\n")
    shutil.copy2(LABOR / "GEDAECHTNIS.md", AUSGABE / "GEDAECHTNIS_nach_den_laeufen.md")


if __name__ == "__main__":
    main()
