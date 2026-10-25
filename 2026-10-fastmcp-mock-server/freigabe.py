"""Menschliche Freigabe per Elicitation: Der Server fragt den Menschen am Client, nicht das Modell.

MCP kennt dafür zwei Wege, je nach Protokoll-Version, die Client und Server aushandeln:
- bis 2025-11-25: Der Server schickt mitten im Aufruf eine Anfrage zurück (ctx.elicit) und wartet.
- ab 2026-07-28: Der Server antwortet "ich brauche erst eine Eingabe" (InputRequiredResult).
  Der Client fragt den Menschen und ruft das Werkzeug mit der Antwort noch einmal auf.
"""
from fastmcp import Context
from mcp.types import ElicitRequest, ElicitRequestFormParams, InputRequiredResult
from mcp_types.version import MODERN_PROTOCOL_VERSIONS

SCHEMA = {
    "type": "object",
    "properties": {"freigeben": {"type": "boolean", "title": "Freigeben?"}},
    "required": ["freigeben"],
}


async def frage_mensch(ctx: Context, frage: str) -> str | InputRequiredResult:
    """Gibt zurück, was am Client passiert ist:
    "freigegeben", "nein" (Haken nicht gesetzt), "decline" (abgelehnt) oder "cancel" (weggeklickt / niemand da).
    Im neuen Protokoll kommt in Runde 1 stattdessen ein InputRequiredResult - das muss das Werkzeug zurückgeben."""
    if ctx.request_context.protocol_version in MODERN_PROTOCOL_VERSIONS:
        antworten = ctx.input_responses
        if antworten is None:  # Runde 1: noch nichts gefragt -> Frage zurückgeben
            return InputRequiredResult(input_requests={
                "freigabe": ElicitRequest(params=ElicitRequestFormParams(message=frage, requested_schema=SCHEMA))
            })
        antwort = antworten.get("freigabe")  # Runde 2: die Antwort des Menschen
        if antwort is None or antwort.action != "accept":
            return antwort.action if antwort else "cancel"
        return "freigegeben" if (antwort.content or {}).get("freigeben") is True else "nein"

    ergebnis = await ctx.elicit(frage, response_type=bool)
    if ergebnis.action != "accept":
        return ergebnis.action
    return "freigegeben" if ergebnis.data is True else "nein"
