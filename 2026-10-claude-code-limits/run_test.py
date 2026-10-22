"""Echter Test: Was kostet dieselbe Aufgabe in Claude Code vom Pro-Limit – je nach Modell, Effort, CLAUDE.md und Resume?

Jeder Lauf startet eine frische Kopie von projekt/ (kleiner Laden mit zwei versteckten Fehlern) im Temp-Ordner und ruft
`claude -p` mit derselben Aufgabe auf. Gemessen werden:
- Tokens und der geschätzte Listenpreis (`total_cost_usd`, von Claude Code lokal berechnet – bei Pro keine Rechnung),
- die Auslastung des 5-Stunden-Fensters und der Woche aus dem `rate_limit_event` (ganze Prozent, gilt für das ganze Konto),
- ob danach alle Tests grün sind.

Start (Windows, Claude Code mit Pro/Max-Abo angemeldet, sonst nichts mit Claude nebenbei laufen lassen):
    python run_test.py --gruppe opus_medium --wdh 3
    python run_test.py --gruppe resume_start      # zwei große Sitzungen + warmes Resume
    python run_test.py --gruppe resume_kalt       # frühestens 65 Minuten später
Ergebnis: outputs/laeufe.jsonl. Rohdaten (mit Sitzungs-IDs) bleiben lokal im Temp-Ordner.
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).parent
TEMP = Path(tempfile.gettempdir())
LABOR = TEMP / "kiwi-limits-test"
RAW = TEMP / "kiwi-limits-raw"
OUT = HERE / "outputs" / "laeufe.jsonl"
STOPP_BEI = 0.85  # nicht das ganze Limit verbrauchen

AUFGABE = ("Einige Tests in tests/ schlagen fehl. Finde die Fehler im Code unter laden/ und repariere sie, "
           "ohne die Tests zu ändern. Führe danach die Tests mit `python -m unittest` aus.")
GROSS = ("Lies die Datei logs/app.log vollständig, auch wenn du sie in mehreren Teilen lesen musst, "
         "und fasse zusammen, welche Fehlerarten vorkommen und wie oft.")
FRAGE = "Ab welchem Warenwert ist der Versand gratis? Antworte in einem Satz."
FRAGE2 = "Was kostet Express-Versand? Antworte in einem Satz."
# Achtung: Bei --resume zählt total_cost_usd die ganze Sitzung (kumuliert). Den Preis eines einzelnen Aufrufs
# rechnet auswertung.py als Differenz zum vorherigen Aufruf derselben Sitzung aus.

GRUPPEN = {
    "opus_medium": {"model": "opus", "effort": "medium"},      # Standard bei Pro: Opus 5.5, Effort medium
    "sonnet_medium": {"model": "sonnet", "effort": "medium"},
    "haiku_medium": {"model": "haiku", "effort": "medium"},
    "opus_low": {"model": "opus", "effort": "low"},
    "opus_max": {"model": "opus", "effort": "max"},
    "opus_claudemd": {"model": "opus", "effort": "medium", "claude_md": True},
}


def claude_md_gross() -> str:
    """Eine aufgeblähte CLAUDE.md (~1.500 Zeilen), wie sie entsteht, wenn man Doku und Notizen hineinkopiert."""
    themen = ["Benennung", "Fehlerbehandlung", "Logging", "Tests", "Datenbank", "API", "Sicherheit", "Deployment",
              "Code-Review", "Dokumentation", "Performance", "Abhängigkeiten"]
    zeilen = ["# Projekt-Handbuch Kiwi-Laden", ""]
    for i in range(1, 126):
        thema = themen[i % len(themen)]
        zeilen += [f"## Regel {i}: {thema}", "",
                   f"- Bei {thema.lower()} gilt im Modul {i % 7 + 1}: Änderungen erst nach Rücksprache im Team-Kanal.",
                   f"- Beispiel {i}: Funktionen zu {thema.lower()} bekommen einen Docstring mit Parametern und Rückgabe.",
                   f"- Ausnahme {i}: Prototypen im Ordner experimente/ dürfen kürzer dokumentiert sein.",
                   f"- Hintergrund: Diese Regel stammt aus der Besprechung Nummer {i * 3} und gilt bis auf Widerruf.",
                   f"- Prüfung: Vor jedem Commit kurz gegen Regel {i} lesen und im Commit-Text erwähnen.",
                   f"- Notiz: Alte Fassung der Regel {i} siehe Wiki-Seite {thema}-{i}, nicht mehr gültig.",
                   "", "---", "", ""]
    return "\n".join(zeilen)


def log_datei() -> str:
    """Eine große, erfundene Log-Datei (~3.000 Zeilen) für den Resume-Test."""
    arten = ["Zahlung abgelehnt", "Lager leer", "Zeitüberschreitung Versanddienst", "Gutschein ungültig"]
    zeilen = []
    for i in range(3000):
        stunde, minute, sekunde = 8 + i // 360, (i // 6) % 60, (i * 7) % 60
        if i % 9 == 0:
            text = f"ERROR {arten[i % 4]} – Bestellung K-{10000 + i}"
        else:
            text = f"INFO Bestellung K-{10000 + i} bearbeitet, {i % 5 + 1} Artikel, Lieferzone {i % 3 + 1}"
        zeilen.append(f"2026-10-21 {stunde:02d}:{minute:02d}:{sekunde:02d} {text}")
    return "\n".join(zeilen) + "\n"


def frisches_labor(name: str, claude_md: bool = False) -> Path:
    ziel = LABOR / name
    if ziel.exists():
        shutil.rmtree(ziel)
    shutil.copytree(HERE / "projekt", ziel)
    (ziel / "logs").mkdir()
    (ziel / "logs" / "app.log").write_text(log_datei(), encoding="utf-8")
    if claude_md:
        (ziel / "CLAUDE.md").write_text(claude_md_gross(), encoding="utf-8")
    return ziel


def claude_env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}


def aufruf(claude: str, cwd: Path, prompt: str, model: str, effort: str, resume: str = "") -> dict:
    cmd = [claude, "-p", prompt, "--model", model, "--effort", effort, "--permission-mode", "acceptEdits",
           "--allowedTools", "Bash(python:*)", "--output-format", "stream-json", "--verbose"]
    if resume:
        cmd += ["--resume", resume]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, env=claude_env(), capture_output=True, text=True, encoding="utf-8", timeout=1800)
    dauer = round(time.time() - t0, 1)
    RAW.mkdir(exist_ok=True)
    (RAW / f"{time.strftime('%H%M%S')}_{cwd.name}.jsonl").write_text(p.stdout, encoding="utf-8")
    r = {"sekunden": dauer, "fuenf_h_vorher": None, "woche_vorher": None, "reset_fuenf_h": None}
    for line in p.stdout.splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "rate_limit_event" and r["fuenf_h_vorher"] is None:
            fenster = d.get("rate_limit_info", {}).get("unifiedWindows", {})
            r["fuenf_h_vorher"] = fenster.get("five_hour", {}).get("utilization")
            r["woche_vorher"] = fenster.get("seven_day", {}).get("utilization")
            r["reset_fuenf_h"] = fenster.get("five_hour", {}).get("resetsAt")
        if d.get("type") == "system" and d.get("subtype") == "init":
            r["_session"] = d.get("session_id")
        if d.get("type") == "result":
            u = d.get("usage", {})
            r.update({
                "kosten_usd": round(d.get("total_cost_usd") or 0.0, 4),
                "runden": d.get("num_turns"),
                "input": u.get("input_tokens", 0),
                "cache_schreiben": u.get("cache_creation_input_tokens", 0),
                "cache_lesen": u.get("cache_read_input_tokens", 0),
                "output": u.get("output_tokens", 0),
                "denk_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
                "modelle": {m: round(v.get("costUSD", 0), 4) for m, v in (d.get("modelUsage") or {}).items()},
                "fehler": d.get("is_error", False),
            })
    return r


def tests_gruen(cwd: Path) -> bool:
    p = subprocess.run(["python", "-m", "unittest"], cwd=cwd, capture_output=True, text=True)
    return p.returncode == 0


def speichern(eintrag: dict) -> None:
    oeffentlich = {k: v for k, v in eintrag.items() if not k.startswith("_")}
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(oeffentlich, ensure_ascii=False) + "\n")
    print(json.dumps(oeffentlich, ensure_ascii=False), flush=True)
    if (eintrag.get("fuenf_h_vorher") or 0) >= STOPP_BEI:
        raise SystemExit(f"Sicherheits-Stopp: 5-Stunden-Fenster bei {eintrag['fuenf_h_vorher']:.0%}")


def stand(claude: str) -> None:
    """Kleiner Haiku-Lauf, nur um die aktuelle Auslastung abzulesen (kostet selbst ein bisschen)."""
    ziel = frisches_labor("stand")
    r = aufruf(claude, ziel, "Antworte nur mit: ok", "haiku", "low")
    speichern({"gruppe": "stand", "zeit": time.strftime("%H:%M"), **r})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude", default=str(Path.home() / ".local" / "bin" / "claude.exe"))
    ap.add_argument("--gruppe", required=True)
    ap.add_argument("--wdh", type=int, default=3)
    a = ap.parse_args()
    LABOR.mkdir(exist_ok=True)
    sitzungen = LABOR / "sitzungen.json"   # bleibt lokal (Sitzungs-IDs)

    if a.gruppe == "stand":
        stand(a.claude)
    elif a.gruppe in GRUPPEN:
        g = GRUPPEN[a.gruppe]
        for i in range(1, a.wdh + 1):
            ziel = frisches_labor(a.gruppe, g.get("claude_md", False))
            r = aufruf(a.claude, ziel, AUFGABE, g["model"], g["effort"])
            speichern({"gruppe": a.gruppe, "lauf": i, "zeit": time.strftime("%H:%M"), "tests_gruen": tests_gruen(ziel), **r})
        stand(a.claude)
    elif a.gruppe == "resume_start":
        ids = {}
        for name in ["gross_warm", "gross_kalt"]:
            ziel = frisches_labor(name)
            r = aufruf(a.claude, ziel, GROSS, "opus", "medium")
            ids[name] = r.get("_session")
            speichern({"gruppe": "resume_gross", "lauf": name, "zeit": time.strftime("%H:%M"), **r})
        sitzungen.write_text(json.dumps({**ids, "start": time.time()}), encoding="utf-8")
        r = aufruf(a.claude, LABOR / "gross_warm", FRAGE, "opus", "medium", resume=ids["gross_warm"])
        speichern({"gruppe": "resume_warm", "zeit": time.strftime("%H:%M"), **r})
        r = aufruf(a.claude, frisches_labor("frisch"), FRAGE, "opus", "medium")
        speichern({"gruppe": "frage_frisch", "zeit": time.strftime("%H:%M"), **r})
        stand(a.claude)
    elif a.gruppe == "resume_kalt":
        ids = json.loads(sitzungen.read_text(encoding="utf-8"))
        minuten = round((time.time() - ids["start"]) / 60)
        r = aufruf(a.claude, LABOR / "gross_kalt", FRAGE, "opus", "medium", resume=ids["gross_kalt"])
        speichern({"gruppe": "resume_kalt", "pause_min": minuten, "zeit": time.strftime("%H:%M"), **r})
        # direkt danach dieselbe Sitzung noch einmal: jetzt ist der Cache wieder warm (fairer Vergleich, gleiche Größe)
        r = aufruf(a.claude, LABOR / "gross_kalt", FRAGE2, "opus", "medium", resume=ids["gross_kalt"])
        speichern({"gruppe": "resume_kalt_danach_warm", "zeit": time.strftime("%H:%M"), **r})
        stand(a.claude)
    else:
        raise SystemExit(f"Unbekannte Gruppe: {a.gruppe}")


if __name__ == "__main__":
    main()
