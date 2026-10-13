"""Kontext-Messung aus dem Video: Wie viele Tokens kostet ein MCP-Server, bevor wir irgendetwas gefragt haben?

    python messen.py                 # alle Kombinationen, je ein Lauf
    python messen.py memory          # nur diese Kombination

Jeder Lauf ist ein einziger kurzer Aufruf ohne Oberfläche (claude -p "Antworte nur mit: ok", Modell Haiku) und
verbraucht ein wenig von deinem Claude-Kontingent. Die Server werden nur für diesen Aufruf geladen
(--mcp-config + --strict-mcp-config), an deiner Claude-Code-Konfiguration ändert sich nichts.
Gemessen wird die Eingabe der ersten Anfrage: input + cache_creation + cache_read aus der echten Ausgabe.
Wenn `claude` nicht im PATH liegt: Umgebungsvariable CLAUDE_BIN auf die claude-Datei setzen.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ORDNER = Path(__file__).resolve().parent
PROJEKT = ORDNER / "projekt"
AUSGABEN = ORDNER / "outputs"
CLAUDE = os.environ.get("CLAUDE_BIN", "claude")

SERVER = {
    "time": {"command": "uvx", "args": ["mcp-server-time"]},
    "memory": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-memory"]},
    "filesystem": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", str(PROJEKT)]},
    "git": {"command": "uvx", "args": ["mcp-server-git"]},
    # derselbe Server, aber so gestartet, wie es das README der Referenz-Server für Windows verlangt
    "memory-cmd": {"command": "cmd", "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-memory"]},
}
KOMBINATIONEN = {
    "ohne": [],
    "time": ["time"],
    "memory": ["memory"],
    "filesystem": ["filesystem"],
    "git": ["git"],
    "alle-vier": ["time", "memory", "filesystem", "git"],
    "memory-cmd": ["memory-cmd"],
}
SUCHE = {"standard": None, "aus": "false"}  # Wert von ENABLE_TOOL_SEARCH; None = nicht gesetzt


def lauf(name: str, suche: str) -> dict:
    config = AUSGABEN / "configs" / f"{name}.json"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text(json.dumps({"mcpServers": {s: SERVER[s] for s in KOMBINATIONEN[name]}}, indent=2), encoding="utf-8")
    umgebung = dict(os.environ)
    umgebung.pop("ENABLE_TOOL_SEARCH", None)
    if SUCHE[suche]:
        umgebung["ENABLE_TOOL_SEARCH"] = SUCHE[suche]
    befehl = [
        CLAUDE, "-p", "Antworte nur mit: ok", "--model", "haiku",
        "--mcp-config", str(config), "--strict-mcp-config",
        "--output-format", "stream-json", "--verbose",
    ]
    fertig = subprocess.run(befehl, cwd=PROJEKT, env=umgebung, capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL)
    (AUSGABEN / f"kontext-{name}-{suche}.jsonl").write_text(fertig.stdout, encoding="utf-8")
    zeile = {"kombination": name, "tool_search": suche}
    for roh in fertig.stdout.splitlines():
        try:
            daten = json.loads(roh)
        except json.JSONDecodeError:
            continue
        if daten.get("type") == "system" and daten.get("subtype") == "init":
            zeile["server"] = {s["name"]: s["status"] for s in daten.get("mcp_servers", [])}
            zeile["mcp_werkzeuge"] = sum(1 for t in daten.get("tools", []) if t.startswith("mcp__"))
        if daten.get("type") == "result":
            u = daten["usage"]
            zeile["eingabe_tokens"] = u["input_tokens"] + u["cache_creation_input_tokens"] + u["cache_read_input_tokens"]
            zeile["fehler"] = daten.get("is_error")
    return zeile


if __name__ == "__main__":
    namen = sys.argv[1:] or list(KOMBINATIONEN)
    ergebnisse = []
    for name in namen:
        for suche in SUCHE:
            zeile = lauf(name, suche)
            ergebnisse.append(zeile)
            print(zeile, flush=True)
    ziel = AUSGABEN / "kontext.json"
    alt = json.loads(ziel.read_text(encoding="utf-8")) if ziel.exists() else []
    neu = {(z["kombination"], z["tool_search"]): z for z in alt + ergebnisse}
    ziel.write_text(json.dumps(list(neu.values()), ensure_ascii=False, indent=2), encoding="utf-8")
