"""Commit-Check: sucht in den gestagten Änderungen nach Geheimnissen und privaten Daten.

    python pruefen.py --staged          prüft nur neue Zeilen aus `git diff --cached`
    python pruefen.py datei1 datei2     prüft ganze Dateien (z. B. vor dem ersten Commit)
    --nur-bericht                       Exit-Code immer 0 (für den Skill: sonst bricht Claude Code das Laden ab)

Exit-Code 0 = nichts gefunden, 1 = Funde, 2 = Fehler (z. B. kein Git-Repository).
Übersprungen werden der eigene Skill-Ordner (sonst meldet er seine eigenen Suchmuster) und Zeilen mit "commit-check: ok"
(für bewusst erlaubte Stellen, z. B. eine Beispiel-Adresse in der Doku).
Gefundene Werte werden nie vollständig ausgegeben, nur maskiert.
Findet nur bekannte Muster - kein Ersatz für einen Blick in den Diff.
"""
import re
import subprocess
import sys
from pathlib import Path

MUSTER = [
    ("Privater Schlüssel", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("API-Key/Token", re.compile(r"\b(sk-[A-Za-z0-9_-]{20,}|ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{40,}"
                                 r"|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{35}|xox[abprs]-[A-Za-z0-9-]{10,})")),
    ("Passwort/Secret", re.compile(r"(?i)\b\w*(passwor[dt]|secret|token|api_?key)\w*\s*[:=]\s*[\"'][^\"']{6,}[\"']")),
    ("E-Mail-Adresse", re.compile(r"\b[A-Za-z0-9._%+-]+@(?!users\.noreply\.github\.com)[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("Persönlicher Pfad", re.compile(r"(?i)\b[A-Z]:[\\/]{1,2}Users[\\/]{1,2}[^\\/\s\"']+|/home/[^/\s\"']+|/Users/[^/\s\"']+")),
]


def maskieren(wert: str) -> str:
    return wert if len(wert) <= 6 else wert[:4] + "…" + "*" * 4


SKILL_ORDNER = Path(__file__).resolve().parent.parent


def eigene_datei(name: str) -> bool:
    """Liegt die Datei im Ordner dieses Skills? Die Muster in pruefen.py würden sich sonst selbst finden."""
    wurzel = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8").stdout.strip()
    pfad = (Path(wurzel) / name) if wurzel else Path(name)
    try:
        pfad.resolve().relative_to(SKILL_ORDNER)
        return True
    except ValueError:
        return False


def neue_zeilen_aus_diff() -> list[tuple[str, int, str]]:
    p = subprocess.run(["git", "diff", "--cached", "-U0", "--no-color"], capture_output=True, text=True, encoding="utf-8")
    if p.returncode != 0:
        sys.exit(f"Fehler: git diff ging nicht ({p.stderr.strip()})")
    zeilen, datei, nr = [], "?", 0
    for z in p.stdout.splitlines():
        if z.startswith("+++ "):
            datei = z[6:] if z.startswith("+++ b/") else z[4:]
        elif z.startswith("@@"):
            nr = int(re.search(r"\+(\d+)", z).group(1))
        elif z.startswith("+"):
            zeilen.append((datei, nr, z[1:]))
            nr += 1
    return zeilen


def zeilen_aus_dateien(namen: list[str]) -> list[tuple[str, int, str]]:
    zeilen = []
    for name in namen:
        text = Path(name).read_text(encoding="utf-8", errors="replace")
        zeilen += [(name, i, z) for i, z in enumerate(text.splitlines(), 1)]
    return zeilen


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # sonst scheitert "…" an alten Konsolen-Zeichensätzen
    args = sys.argv[1:]
    nur_bericht = "--nur-bericht" in args
    args = [a for a in args if a != "--nur-bericht"]
    if not args:
        print(__doc__)
        return 2
    zeilen = neue_zeilen_aus_diff() if args == ["--staged"] else zeilen_aus_dateien(args)
    if args == ["--staged"] and not zeilen:
        print("Nichts gestagt. Erst `git add <datei>`, dann erneut prüfen.")
        return 0
    funde = []
    zeilen = [z for z in zeilen if "commit-check: ok" not in z[2] and not eigene_datei(z[0])]
    for datei, nr, text in zeilen:
        belegt = []  # eine Stelle nur einmal melden, das genaueste Muster zuerst
        for art, muster in MUSTER:
            for m in muster.finditer(text):
                if any(m.start() < ende and start < m.end() for start, ende in belegt):
                    continue
                belegt.append(m.span())
                funde.append((datei, nr, art, maskieren(m.group(0))))
    if not funde:
        print(f"Commit-Check: {len(zeilen)} Zeilen geprüft, nichts gefunden.")
        return 0
    print(f"Commit-Check: {len(funde)} Fund(e) in {len(zeilen)} Zeilen - NICHT committen:")
    for datei, nr, art, wert in funde:
        print(f"  {datei}:{nr}  {art}  {wert}")
    return 0 if nur_bericht else 1


if __name__ == "__main__":
    sys.exit(main())
