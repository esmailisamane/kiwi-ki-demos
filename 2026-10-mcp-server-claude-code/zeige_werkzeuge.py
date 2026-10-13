# /// script
# requires-python = ">=3.11"
# dependencies = ["mcp>=2,<3"]
# ///
"""Zeigt, was ein MCP-Server dem Modell über seine Werkzeuge erzählt - ohne Claude, ohne Kontingent.

    uv run zeige_werkzeuge.py uv run wetter_server.py manipuliert
    uv run zeige_werkzeuge.py cmd /c npx -y @modelcontextprotocol/server-memory

Alles nach dem Skriptnamen ist der Startbefehl des Servers. Ausgabe: Name, Beschreibung und Größe jeder
Werkzeug-Definition. Genau diesen Text liest das Modell; du siehst ihn in Claude Code normalerweise nicht.
"""
import asyncio
import io
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


async def main(befehl: list[str]) -> None:
    start = StdioServerParameters(command=befehl[0], args=befehl[1:])
    async with stdio_client(start) as (lesen, schreiben):
        async with ClientSession(lesen, schreiben) as sitzung:
            await sitzung.initialize()
            werkzeuge = (await sitzung.list_tools()).tools
            gesamt = 0
            for w in werkzeuge:
                definition = json.dumps(w.model_dump(exclude_none=True), ensure_ascii=False)
                gesamt += len(definition)
                print(f"== {w.name}  ({len(definition)} Zeichen)")
                print(w.description or "(keine Beschreibung)")
                print()
            print(f"{len(werkzeuge)} Werkzeug{'e' if len(werkzeuge) != 1 else ''}, {gesamt} Zeichen Definition insgesamt")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    asyncio.run(main(sys.argv[1:]))
