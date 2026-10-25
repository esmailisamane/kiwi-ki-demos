"""Spricht mit dem Kiwi-Laden über HTTP. Vorher in einem zweiten Terminal starten:
    uv run fastmcp run laden_server.py --transport http --port 8765
"""
import asyncio

from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:8765/mcp") as c:
        print("Protokoll:", c.protocol_version)
        print([t.name for t in await c.list_tools()])


asyncio.run(main())
