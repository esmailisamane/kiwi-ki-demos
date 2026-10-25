from fastmcp import FastMCP
mcp = FastMCP("print-test")

@mcp.tool
def hallo(name: str) -> str:
    print("DEBUG: hallo wurde aufgerufen")   # landet auf stdout = dem MCP-Kanal
    return f"Hallo {name}"
