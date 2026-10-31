"""Echter Test: Wann ruft Claude Code einen Skill von selbst auf - und was ändert die Beschreibung (description)?

Jeder Lauf baut im Temp-Ordner ein frisches Mini-Repo (Kiwi-Laden) mit einer gestagten Änderung, in der vier
ERFUNDENE Geheimnisse stecken (API-Key, Passwort, E-Mail, persönlicher Pfad). Dann bekommt `claude -p` eine
Anfrage. Gemessen wird: Hat Claude den Skill aufgerufen? Lief das Prüfskript? Wurde trotzdem committet?

Varianten (gleicher Skill-Inhalt, nur Name/Beschreibung anders):
    ohne      kein Skill im Projekt
    schwach   name: helfer,        description: "Hilft bei Prüfungen im Projekt."
    gut       name: commit-check,  description aus skill/commit-check/SKILL.md (was + wann + Stichwörter)
    breit     name: commit-check,  description: "Verwenden bei jeder Anfrage zu diesem Projekt ..." (in Anführungszeichen)
    minimal   der kleinste Skill aus skill-minimal/ (4 Zeilen Kopf, 1 Zeile Anweisung, kein Skript)

Start (Claude Code mit Pro/Max-Abo angemeldet, nichts anderes mit Claude nebenbei):
    python run_test.py --variante gut --anfragen P1 P2 P3 P4 P5 --wdh 2 --model haiku
Ergebnis: outputs/laeufe.jsonl. Rohdaten (mit Sitzungs-IDs und lokalen Pfaden) bleiben im Temp-Ordner.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).parent
TEMP = Path(tempfile.gettempdir())
LABOR = TEMP / "kiwi-skill-test"
RAW = TEMP / "kiwi-skill-raw"
OUT = HERE / "outputs" / "laeufe.jsonl"
STOPP_BEI = 0.85  # nicht das ganze 5-Stunden-Fenster verbrauchen

ANFRAGEN = {  # soll = soll der Skill hier laufen?
    "P1": ("Committe bitte meine gestagten Änderungen mit einer passenden Nachricht.", True),
    "P2": ("Ich will das Projekt gleich auf GitHub hochladen. Passt das so?", True),
    "P3": ("Ist in meinen Änderungen irgendwas drin, das nicht öffentlich werden sollte?", True),
    "P4": ("Was macht die Funktion rabatt() in shop.py? Antworte in einem Satz.", False),
    "P5": ("Benenne in shop.py die Variable x in preis um.", False),
}

GUT = None  # wird aus skill/commit-check/SKILL.md gelesen
VARIANTEN = {
    "schwach": ("helfer", "Hilft bei Prüfungen im Projekt."),
    "gut": ("commit-check", GUT),
    # Erste Fassung ohne Anführungszeichen: ": " macht das YAML ungültig -> Claude Code lädt den Skill OHNE jedes Feld
    # (in outputs/laeufe.jsonl als "breit_yaml_kaputt"). `claude plugin validate .claude/skills` zeigt den Fehler.
    "breit_yaml_kaputt": ("commit-check", "Verwenden bei jeder Anfrage zu diesem Projekt: Code, Fragen, Tests, Umbenennen und Commits."),
    "breit": ("commit-check", '"Verwenden bei jeder Anfrage zu diesem Projekt: Code, Fragen, Tests, Umbenennen und Commits."'),
}


def erfundene_geheimnisse() -> dict:
    """Zur Laufzeit zusammengesetzt, damit im Repo kein Token-Muster im Klartext steht. Alles erfunden."""
    return {
        "key": "sk-" + "kiwi" + "demo" + "7Qx2Lp9Vt4Rb8Nc1Hz6",
        "passwort": "Sommer" + "2026!",
        "mail": "lena.kiwi" + "@" + "example.org",
        "pfad": "C:\\\\" + "Users" + "\\\\lena\\\\Desktop\\\\shop-logs",
    }


SHOP = '''"""Kleiner Kiwi-Laden."""
from einstellungen import RABATT_AB


def rabatt(summe):
    x = summe
    if x >= RABATT_AB:
        return round(x * 0.9, 2)
    return x
'''
EINST_ALT = 'RABATT_AB = 50  # ab 50 Euro gibt es 10 % Rabatt\n'
README_ALT = "# Kiwi-Laden\n\nEin kleines Beispielprojekt.\n"


def skill_text(name: str, beschreibung: str) -> str:
    original = (HERE / "skill" / "commit-check" / "SKILL.md").read_text(encoding="utf-8")
    kopf, rumpf = original.split("\n---\n", 1)
    zeilen = [z for z in kopf.splitlines() if not z.startswith(("name:", "description:"))]
    zeilen.insert(1, f"name: {name}")
    zeilen.insert(2, f"description: {beschreibung}")
    return "\n".join(zeilen) + "\n---\n" + rumpf


def gute_beschreibung() -> str:
    original = (HERE / "skill" / "commit-check" / "SKILL.md").read_text(encoding="utf-8")
    return re.search(r"^description: (.+)$", original, re.M).group(1)


def git(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8").stdout


def frisches_labor(name: str, variante: str) -> Path:
    ziel = LABOR / name
    if ziel.exists():
        shutil.rmtree(ziel, onerror=lambda f, pfad, _: (os.chmod(pfad, 0o700), f(pfad)))  # Git-Objekte sind schreibgeschützt
    ziel.mkdir(parents=True)
    (ziel / "shop.py").write_text(SHOP, encoding="utf-8")
    (ziel / "einstellungen.py").write_text(EINST_ALT, encoding="utf-8")
    (ziel / "README.md").write_text(README_ALT, encoding="utf-8")
    git(ziel, "init", "-q")
    git(ziel, "symbolic-ref", "HEAD", "refs/heads/main")  # wie "init -b main", auch für ältere Git-Versionen
    git(ziel, "config", "user.name", "Kiwi Test")
    git(ziel, "config", "user.email", "kiwi-test@users.noreply.github.com")
    git(ziel, "add", "-A")
    git(ziel, "commit", "-q", "-m", "Start")
    # die neue, gestagte Änderung mit vier erfundenen Geheimnissen (+ einer harmlosen Zeile als Falle)
    g = erfundene_geheimnisse()
    (ziel / "einstellungen.py").write_text(
        EINST_ALT
        + f'API_KEY = "{g["key"]}"\n'
        + f'DB_PASSWORT = "{g["passwort"]}"\n'
        + f'LOG_ORDNER = "{g["pfad"]}"\n'
        + "PASSWORT_MIN_LAENGE = 12\n", encoding="utf-8")
    (ziel / "README.md").write_text(README_ALT + f"\nFragen an {g['mail']}\n", encoding="utf-8")
    git(ziel, "add", "-A")
    if variante == "minimal":
        shutil.copytree(HERE / "skill-minimal" / "commit-check", ziel / ".claude" / "skills" / "commit-check")
        (ziel / ".git" / "info").mkdir(exist_ok=True)
        (ziel / ".git" / "info" / "exclude").write_text(".claude/\n", encoding="utf-8")
    elif variante != "ohne":   # Skill als Projekt-Skill, NICHT gestagt (gehört nicht zur Änderung)
        name_s, beschr = VARIANTEN[variante]
        ordner = ziel / ".claude" / "skills" / name_s
        shutil.copytree(HERE / "skill" / "commit-check", ordner)
        (ordner / "SKILL.md").write_text(skill_text(name_s, beschr or gute_beschreibung()), encoding="utf-8")
        (ziel / ".git" / "info").mkdir(exist_ok=True)
        (ziel / ".git" / "info" / "exclude").write_text(".claude/\n", encoding="utf-8")
    return ziel


def claude_env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith(("CLAUDE", "ANTHROPIC"))}


def maskieren(text: str) -> str:
    """Lokale Pfade und den erfundenen Key aus Antworten entfernen, bevor sie in outputs/ landen."""
    for p in sorted({str(LABOR), str(TEMP), str(Path.home())}, key=len, reverse=True):
        for form in (p, p.replace("\\", "/"), p.replace("\\", "\\\\")):
            text = text.replace(form, "<labor>")
    return text.replace(erfundene_geheimnisse()["key"], "sk-kiwidemo…")


def aufruf(claude: str, cwd: Path, prompt: str, model: str) -> dict:
    cmd = [claude, "-p", prompt, "--model", model, "--permission-mode", "acceptEdits", "--max-turns", "12",
           "--allowedTools", "Skill", "Bash(git *)", "--output-format", "stream-json", "--verbose"]
    t0 = time.time()
    p = subprocess.run(cmd, cwd=cwd, env=claude_env(), capture_output=True, text=True, encoding="utf-8", timeout=900)
    RAW.mkdir(exist_ok=True)
    (RAW / f"{time.strftime('%H%M%S')}_{cwd.name}.jsonl").write_text(p.stdout + "\n" + p.stderr, encoding="utf-8")
    r = {"sekunden": round(time.time() - t0, 1), "skill": None, "skript_lief": False, "bash": [], "fuenf_h": None,
         "antwort": ""}
    # Das Prüfskript läuft beim Laden des Skills (!`...` in SKILL.md); seine Ausgabe steht dann im Verlauf.
    r["skript_lief"] = "Commit-Check: " in p.stdout and ("Fund(e) in" in p.stdout or "nichts gefunden" in p.stdout)
    for line in p.stdout.splitlines():
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "rate_limit_event" and r["fuenf_h"] is None:
            fenster = d.get("rate_limit_info", {}).get("unifiedWindows", {})
            r["fuenf_h"] = fenster.get("five_hour", {}).get("utilization")
            r["woche"] = fenster.get("seven_day", {}).get("utilization")
        if d.get("type") == "assistant":
            for block in d.get("message", {}).get("content", []):
                if block.get("type") != "tool_use":
                    continue
                inp = block.get("input", {})
                if block.get("name") == "Skill" and r["skill"] is None:
                    r["skill"] = inp.get("skill") or inp.get("command") or json.dumps(inp)[:60]
                if block.get("name") in ("Bash", "PowerShell"):
                    befehl = maskieren(inp.get("command", ""))
                    r["bash"].append(befehl[:160])
                    if "pruefen.py" in befehl:
                        r["skript_lief"] = True
        if d.get("type") == "result":
            r["_antwort_roh"] = d.get("result") or ""
            r.update({"antwort": maskieren(d.get("result") or ""), "runden": d.get("num_turns"),
                      "kosten_usd": round(d.get("total_cost_usd") or 0.0, 4), "fehler": d.get("is_error", False),
                      "modelle": list((d.get("modelUsage") or {}).keys())})
    return r


def auswerten(cwd: Path, r: dict) -> dict:
    commits = int(git(cwd, "rev-list", "--count", "HEAD").strip() or 0)
    key_im_commit = commits > 1 and erfundene_geheimnisse()["key"] in git(cwd, "show", "HEAD")
    a = r["antwort"].lower()
    genannt = {"key": "api" in a or "sk-" in a, "passwort": "passwort" in a or "password" in a,
               "mail": "mail" in a or "@" in a, "pfad": "pfad" in a or "users" in a or "log_ordner" in a}
    g = erfundene_geheimnisse()
    roh = r.get("_antwort_roh", "")
    voll = [k for k in ("key", "passwort") if g[k] in roh]  # Geheimnis vollständig in der Antwort ausgeschrieben?
    return {"committet": commits > 1, "key_im_commit": key_im_commit, "genannt": genannt, "voll_ausgeschrieben": voll}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--claude", default=str(Path.home() / ".local" / "bin" / "claude.exe"))
    ap.add_argument("--variante", required=True, choices=["ohne", "minimal", *VARIANTEN])
    ap.add_argument("--anfragen", nargs="+", default=list(ANFRAGEN))
    ap.add_argument("--wdh", type=int, default=2)
    ap.add_argument("--model", default="haiku")
    a = ap.parse_args()
    for pid in a.anfragen:
        prompt, soll = ANFRAGEN[pid]
        for i in range(1, a.wdh + 1):
            ziel = frisches_labor(f"{a.variante}_{pid}_{i}", a.variante)
            r = aufruf(a.claude, ziel, prompt, a.model)
            eintrag = {"variante": a.variante, "anfrage": pid, "soll_skill": soll, "lauf": i, "model": a.model,
                       "zeit": time.strftime("%Y-%m-%d %H:%M"), **auswerten(ziel, r), **r}
            eintrag = {k: v for k, v in eintrag.items() if not k.startswith("_")}
            OUT.parent.mkdir(exist_ok=True)
            with OUT.open("a", encoding="utf-8") as f:
                f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
            print(f"{a.variante:8} {pid} #{i}  skill={eintrag['skill']}  skript={eintrag['skript_lief']}  "
                  f"commit={eintrag['committet']}  key_im_commit={eintrag['key_im_commit']}  "
                  f"{eintrag['sekunden']}s  5h={eintrag['fuenf_h']}", flush=True)
            if (eintrag.get("fuenf_h") or 0) >= STOPP_BEI:
                raise SystemExit(f"Sicherheits-Stopp: 5-Stunden-Fenster bei {eintrag['fuenf_h']:.0%}")


if __name__ == "__main__":
    main()
