"""Schritt 2: eigene Werkzeuge - Dateien auflisten und in eine CSV-Tabelle schreiben."""

import asyncio
import csv
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)

ORDNER = Path("rechnungen").resolve()
TABELLE = ORDNER / "rechnungen.csv"
SPALTEN = ["datei", "lieferant", "datum", "brutto", "mwst"]


@tool("list_invoices", "Listet alle Rechnungs-Dateien im Ordner rechnungen auf.", {})
async def list_invoices(args):
    dateien = sorted(d.name for d in ORDNER.iterdir() if d.suffix.lower() in {".pdf", ".png", ".jpg"})
    return {"content": [{"type": "text", "text": "\n".join(dateien)}]}


@tool(
    "save_invoice",
    "Speichert eine gelesene Rechnung als neue Zeile in rechnungen.csv.",
    {"datei": str, "lieferant": str, "datum": str, "brutto": str, "mwst": str},
)
async def save_invoice(args):
    neu = not TABELLE.exists()
    with TABELLE.open("a", newline="", encoding="utf-8-sig") as f:
        schreiber = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";")
        if neu:
            schreiber.writeheader()
        schreiber.writerow({spalte: args[spalte] for spalte in SPALTEN})
    return {"content": [{"type": "text", "text": f"Gespeichert: {args['datei']}"}]}


werkzeugkasten = create_sdk_mcp_server(name="rechnungen", tools=[list_invoices, save_invoice])


async def main():
    optionen = ClaudeAgentOptions(
        mcp_servers={"rechnungen": werkzeugkasten},
        allowed_tools=["Read", "mcp__rechnungen__list_invoices", "mcp__rechnungen__save_invoice"],
    )
    auftrag = "Lies alle Rechnungen im Ordner rechnungen und speichere jede mit save_invoice."
    async for nachricht in query(prompt=auftrag, options=optionen):
        if isinstance(nachricht, AssistantMessage):
            for block in nachricht.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"  -> {block.name}")


asyncio.run(main())
