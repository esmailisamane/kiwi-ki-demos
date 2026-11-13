"""Rechnungs-Agent: sortiert Rechnungen mit dem Claude Agent SDK.

Was er macht:
  1. alle Rechnungen im Ordner rechnungen/ lesen (PDF und Fotos)
  2. Lieferant, Datum, Brutto-Betrag und MwSt herauslesen
  3. alles in rechnungen/rechnungen.csv schreiben (öffnet sich in Excel)
  4. die Dateien sauber umbenennen - aber nur, wenn du "j" tippst
  5. nichts raten: Unlesbares wird "unklar"

Start:   python rechnungs_agent.py
Braucht: pip install claude-agent-sdk   und einen ANTHROPIC_API_KEY
"""

import asyncio
import csv
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)
from claude_agent_sdk.types import (
    PermissionResultAllow,
    PermissionResultDeny,
    ToolPermissionContext,
)

ORDNER = Path("rechnungen").resolve()
TABELLE = ORDNER / "rechnungen.csv"
SPALTEN = ["datei", "lieferant", "datum", "brutto", "mwst"]
ENDUNGEN = {".pdf", ".png", ".jpg", ".jpeg"}


# ---------- Werkzeuge: das sind die Hände des Agenten ----------

@tool("list_invoices", "Listet alle Rechnungs-Dateien (PDF, PNG, JPG) im Ordner rechnungen auf.", {})
async def list_invoices(args):
    dateien = sorted(d.name for d in ORDNER.iterdir() if d.suffix.lower() in ENDUNGEN)
    return {"content": [{"type": "text", "text": "\n".join(dateien) or "Keine Rechnungen gefunden."}]}


@tool(
    "save_invoice",
    "Speichert eine gelesene Rechnung als neue Zeile in rechnungen.csv. "
    "Datum als JJJJ-MM-TT, Beträge wie 39,90. Was nicht lesbar ist: 'unklar'.",
    {"datei": str, "lieferant": str, "datum": str, "brutto": str, "mwst": str},
)
async def save_invoice(args):
    neu = not TABELLE.exists()
    # utf-8-sig und ";" -> deutsches Excel zeigt Umlaute und Spalten richtig
    with TABELLE.open("a", newline="", encoding="utf-8-sig") as f:
        schreiber = csv.DictWriter(f, fieldnames=SPALTEN, delimiter=";")
        if neu:
            schreiber.writeheader()
        schreiber.writerow({spalte: args[spalte] for spalte in SPALTEN})
    return {"content": [{"type": "text", "text": f"Gespeichert: {args['datei']}"}]}


@tool("rename_file", "Benennt eine Rechnung im Ordner rechnungen um.", {"alt": str, "neu": str})
async def rename_file(args):
    alt = (ORDNER / args["alt"]).resolve()
    neu = (ORDNER / args["neu"]).resolve()
    # Zaun: nur Dateien direkt im Ordner rechnungen, nichts überschreiben
    if alt.parent != ORDNER or neu.parent != ORDNER:
        return fehler("Abgelehnt: nur Dateien direkt im Ordner rechnungen.")
    if not alt.exists():
        return fehler(f"Datei nicht gefunden: {args['alt']}")
    if neu.exists():
        return fehler(f"Gibt es schon: {args['neu']}")
    alt.rename(neu)
    return {"content": [{"type": "text", "text": f"Umbenannt: {args['alt']} -> {args['neu']}"}]}


def fehler(text):
    return {"content": [{"type": "text", "text": text}], "is_error": True}


werkzeugkasten = create_sdk_mcp_server(
    name="rechnungen",
    version="1.0.0",
    tools=[list_invoices, save_invoice, rename_file],
)


# ---------- Freigabe: du entscheidest ----------

async def frage_mich(tool_name: str, eingabe: dict, kontext: ToolPermissionContext):
    if tool_name == "mcp__rechnungen__rename_file":
        antwort = await asyncio.to_thread(
            input, f"Umbenennen? {eingabe['alt']} -> {eingabe['neu']} [j/n] "
        )
        if antwort.strip().lower() == "j":
            return PermissionResultAllow()
        return PermissionResultDeny(message="Der Nutzer hat das Umbenennen abgelehnt.")
    # alles andere, was eine Freigabe braucht (Bash, Write, Edit, ...): nein
    return PermissionResultDeny(message=f"{tool_name} ist für diesen Agenten nicht erlaubt.")


# ---------- Regeln: die Stellenbeschreibung ----------

REGELN = """Du bist ein Rechnungs-Agent. Du arbeitest nur im Ordner rechnungen.

So gehst du vor:
1. Hol dir mit list_invoices die Liste der Dateien.
2. Lies jede Datei mit dem Read-Werkzeug (Pfad: rechnungen/<datei>).
3. Lies heraus: Lieferant, Rechnungsdatum, Brutto-Betrag, MwSt-Betrag.
4. Speichere jede Rechnung mit save_invoice.
5. Benenne die Datei danach mit rename_file um: JJJJ-MM-TT_Lieferant_Betrag.<endung>,
   zum Beispiel 2026-11-03_Stadtwerke-Kiwistadt_84,20.pdf

Wichtig:
- Rate nie. Steht ein Wert nicht klar auf der Rechnung, schreib "unklar".
- Eine Datei mit einem unklaren Wert benennst du NICHT um.
- Wird ein Umbenennen abgelehnt, mach mit der nächsten Datei weiter.
- Am Ende: kurze Liste, was erledigt ist und was unklar blieb."""


optionen = ClaudeAgentOptions(
    system_prompt=REGELN,
    cwd=str(ORDNER.parent),
    mcp_servers={"rechnungen": werkzeugkasten},
    # laufen ohne Nachfrage:
    allowed_tools=["Read", "mcp__rechnungen__list_invoices", "mcp__rechnungen__save_invoice"],
    # alles andere, was Freigabe braucht, landet hier:
    can_use_tool=frage_mich,
    setting_sources=[],  # keine CLAUDE.md und Einstellungen von deinem Rechner mischen
    max_turns=40,  # Notbremse: höchstens 40 Runden
    max_budget_usd=1.0,  # Geld-Notbremse pro Lauf in Dollar - Wert selbst wählen
)


async def main():
    auftrag = "Sortiere bitte alle Rechnungen im Ordner rechnungen."
    print("Auftrag:", auftrag)
    async for nachricht in query(prompt=auftrag, options=optionen):
        if isinstance(nachricht, AssistantMessage):
            for block in nachricht.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    print(f"  -> {block.name}")
        elif isinstance(nachricht, ResultMessage):
            print(f"\nFertig: {nachricht.subtype}")


if __name__ == "__main__":
    asyncio.run(main())
