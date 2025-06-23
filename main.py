import json
import types
import uuid
from mcp.server.fastmcp import FastMCP, Context
from mcp import types
from chunky_mcp_utils import handle_large_response, chunker

mcp = FastMCP("AsyncDemoServer")
_chunker = chunker.ResponseChunker()

@mcp.tool()
async def read_response_chunk(file_id: str, chunk_number: int = 0) -> list[types.TextContent]:
    """Read a chunk of a previously saved large response"""

    if file_id not in _chunker.temp_files:
        return [types.TextContent(
            type="text",
            text=f"Error: file_id '{file_id}' not found or expired"
        )]

    file_info = _chunker.temp_files[file_id]

    try:
        with open(file_info['file_path'], 'r') as f:
            # Read the entire file (for JSON parsing)
            content = f.read()
            
        # Calculate chunk boundaries
        start_pos = chunk_number * _chunker.MAX_CHUNK_SIZE
        end_pos = min(start_pos + _chunker.MAX_CHUNK_SIZE, len(content))

        if start_pos >= len(content):
            return [types.TextContent(
                type="text",
                text=f"Chunk {chunk_number} is beyond end of file. Total chunks available: {(len(content) + _chunker.MAX_CHUNK_SIZE - 1) // _chunker.MAX_CHUNK_SIZE}"
            )]
        
        chunk_content = content[start_pos:end_pos]
        total_chunks = (len(content) + _chunker.MAX_CHUNK_SIZE - 1) // _chunker.MAX_CHUNK_SIZE

        return [types.TextContent(
            type="text",
            text=f"Chunk {chunk_number + 1}/{total_chunks} of {file_id}:\n\n{chunk_content}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error reading chunk: {str(e)}"
        )]

if __name__ == "__main__":
    mcp.run(transport="stdio")