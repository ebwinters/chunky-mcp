from mcp import types
from mcp.server.fastmcp import FastMCP
import requests
from chunky_mcp_utils import handle_large_response, chunker

mcp = FastMCP("AsyncDemoServer")
_chunker = chunker.ResponseChunker()

@mcp.tool()
def get_employees() -> list[types.TextContent]:
    """
    Gets a list of all the employees in the system from the database
    When the user asks for a list of employees, this tool is called.
    """
    # Simulate a large response
    response = requests.get("https://microsoftedge.github.io/Demos/json-dummy-data/128KB.json")
    response.raise_for_status()
    response_data = response.json()
    
    return handle_large_response(
        response_data,
        get_employees.__name__,
        _chunker
    )