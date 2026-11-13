"""Schritt 1: der kleinste Agent - liest EINE Rechnung und sagt, was drinsteht."""

import asyncio

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query


async def main():
    optionen = ClaudeAgentOptions(allowed_tools=["Read"])
    auftrag = "Lies rechnungen/scan_0012.pdf. Wer ist der Lieferant, welches Datum, welcher Betrag?"
    async for nachricht in query(prompt=auftrag, options=optionen):
        if isinstance(nachricht, AssistantMessage):
            for block in nachricht.content:
                if isinstance(block, TextBlock):
                    print(block.text)


asyncio.run(main())
