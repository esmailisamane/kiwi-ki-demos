from fastmcp import FastMCP

mcp = FastMCP("erster-server")


@mcp.tool
def begruessen(name: str) -> str:
    """Begrüßt eine Person mit ihrem Namen."""
    return f"Hallo {name}, willkommen im Kiwi-Laden!"


if __name__ == "__main__":
    mcp.run()
