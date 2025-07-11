# chunky-mcp
An MCP server to handle chunking and reading large responses

Before:

![before](images/before.png)

After:

![after](images/after1.png)![](images/after2.png)

## Quick Install
### Using Pip

### Cloning 
1. `git clone https://github.com/ebwinters/chunky-mcp.git`
2. `cd chunky-mcp`
3. `pip install -e .`

## Usage

Import the helper in your tool:

```python
from chunky_mcp_utils import handle_large_response

@mcp.tool()
def my_tool() -> list[types.TextContent]:
    """
    Gets a list of all the employees in the system from the database
    """
    # Call might give a large JSON response
    response = requests.get("https://someblob.com")
    response_data = response.json()
    
    # Chunker handles the large response and calls following read chunk tools
    return handle_large_response(
        response_data,
        my_tool.__name__,
        _chunker
    )
```

Add MCP entry
```json
"chunky": {
    "type": "stdio",
    "command": "chunky-mcp",
    "args": []
}
```


## Dev Setup
1. Install `uv`
2. `uv venv`
3. `.\.venv\Scripts\activate`
4. `uv sync`
