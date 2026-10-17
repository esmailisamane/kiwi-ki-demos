"""Testet den Hook ohne Modell: schickt typische Werkzeug-Aufrufe als JSON an schutz_env.ps1 und zeigt den Exit-Code.

Start (Windows): python hook_offline_test.py
Exit-Code 2 = blockiert, 0 = erlaubt.
"""
import json
import subprocess
from pathlib import Path

HOOK = Path(__file__).parent / "einstellungen" / "schutz_env.ps1"
CASES = [
    ("Read", {"file_path": r"C:\projekt\.env"}),
    ("Bash", {"command": "cat .env"}),
    ("PowerShell", {"command": "Get-Content .env"}),
    ("Bash", {"command": "python -c \"print(open('.env').read())\""}),
    ("Bash", {"command": "grep -r ZAHLUNG ."}),
    ("Read", {"file_path": r"C:\projekt\.env.example"}),
    ("Read", {"file_path": r"C:\projekt\app.py"}),
]


def run(stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(HOOK)],
                          input=stdin, capture_output=True, text=True)


for tool, tool_input in CASES:
    p = run(json.dumps({"tool_name": tool, "tool_input": tool_input}))
    print(f"exit {p.returncode}  {tool:10} {json.dumps(tool_input, ensure_ascii=False):55} {p.stderr.strip()[:50]}")
p = run("kaputt{")
print(f"exit {p.returncode}  kaputte Eingabe {p.stderr.strip()[:60]}")
