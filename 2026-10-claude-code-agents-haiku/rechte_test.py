"""Rechte-Test aus dem Video: Kann ein Subagent eine Datei ändern, wenn `tools` nur Lesen erlaubt?

    python rechte_test.py

Der Test arbeitet auf einer Kopie des Projekts in einem temporären Ordner, das Original bleibt unberührt.
Zwei Läufe mit demselben Auftrag ("behebe den Rundungsfehler in shop/preise.py"):
  A  Subagent mit `tools: Read, Grep, Glob`
  B  derselbe Subagent ohne die tools-Zeile (er erbt alle Werkzeuge)
Die Hauptsitzung darf in beiden Läufen Dateien ändern (acceptEdits), soll aber nur delegieren.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ORDNER = Path(__file__).resolve().parent
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")
AUFTRAG = (
    "Beauftrage den Subagent {agent} damit, den Rundungsfehler in der Funktion runde_cent in shop/preise.py "
    "direkt in der Datei zu beheben. Ändere selbst nichts und lies die Datei nicht selbst. "
    "Berichte am Ende in zwei Sätzen, was der Subagent getan hat."
)
AGENT = """---
name: {name}
description: Prüft und repariert Python-Dateien.
{tools}model: haiku
---

Du bist ein sorgfältiger Python-Entwickler. Erledige genau den Auftrag, den du bekommst.
"""


def lauf(name: str, tools_zeile: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        kopie = Path(tmp) / "projekt"
        shutil.copytree(ORDNER / "projekt", kopie, ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
        (kopie / ".claude" / "agents" / f"{name}.md").write_text(
            AGENT.format(name=name, tools=tools_zeile), encoding="utf-8"
        )
        vorher = (kopie / "shop" / "preise.py").read_text(encoding="utf-8")
        fertig = subprocess.run(
            [CLAUDE, "-p", AUFTRAG.format(agent=name), "--model", "haiku", "--tools", "Read,Grep,Glob,Edit,Write,Agent",
             "--permission-mode", "acceptEdits", "--strict-mcp-config", "--output-format", "json"],
            cwd=kopie, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
        )
        nachher = (kopie / "shop" / "preise.py").read_text(encoding="utf-8")
        daten = json.loads(fertig.stdout)
        zeile = next((z.strip() for z in nachher.splitlines() if "return" in z and "100" in z), "?")
        bericht = (
            f"Lauf {name} ({tools_zeile.strip() or 'ohne tools-Zeile'})\n"
            f"Datei geändert: {'JA' if vorher != nachher else 'NEIN'}\n"
            f"Zeile in runde_cent danach: {zeile}\n"
            f"Subagents gestartet: {daten.get('subagent_stats', {}).get('by_type', {})}\n"
            f"Antwort der Hauptsitzung:\n{daten.get('result', '')}\n"
        )
        print(bericht)
        (ORDNER / "outputs" / f"rechte-{name}.txt").write_text(bericht, encoding="utf-8")


if __name__ == "__main__":
    lauf("nur-lesen", "tools: Read, Grep, Glob\n")
    lauf("alle-werkzeuge", "")
