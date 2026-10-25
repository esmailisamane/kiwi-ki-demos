"""Zeigt die menschliche Freigabe (Elicitation) in beiden Protokoll-Varianten.

    uv run python beispiele/freigabe_demo.py

Der Python-Client von FastMCP spielt hier den Menschen: Er beantwortet die Frage des Servers mit "ja".
Das Protokoll unten zeigt, wie oft der Server das Werkzeug dabei wirklich ausführt.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ["KIWI_DB"] = str(Path(tempfile.gettempdir()) / "kiwi_freigabe_demo.db")

from fastmcp import Client  # noqa: E402
from mcp.types import ElicitResult  # noqa: E402

import datenbank  # noqa: E402
import regeln  # noqa: E402
from laden_server import mcp  # noqa: E402

aufrufe = []


class Zaehler(regeln.Middleware):
    async def on_call_tool(self, context, call_next):
        aufrufe.append(context.message.name)
        return await call_next(context)


mcp.add_middleware(Zaehler())


async def mensch(message, response_type, params, context):
    feld = next(iter(params.requested_schema["properties"]))
    print(f"   Frage an den Menschen: {message}")
    print(f"   Antwort: ja  (Feld '{feld}')")
    return ElicitResult(action="accept", content={feld: True})


async def main():
    for modus in ["legacy", "auto"]:
        datenbank.neu_anlegen()
        aufrufe.clear()
        async with Client(mcp, mode=modus, elicitation_handler=mensch) as c:
            print(f"Modus {modus}: Protokoll {c.protocol_version}")
            r = await c.call_tool("ruecksendung_anlegen",
                                  {"bestellnummer": "B-1050", "sku": "K-200", "grund": "gefaellt_nicht", "menge": 4})
            aufrufe.clear()
            g = await c.call_tool("gutschrift_ausstellen", {"ruecksendung_id": r.data.ruecksendung_id})
            print(f"   Ergebnis: {g.data.gutschrift_id} über {g.data.betrag:.2f} Euro")
            print(f"   gutschrift_ausstellen lief {len(aufrufe)}-mal auf dem Server\n")


asyncio.run(main())
