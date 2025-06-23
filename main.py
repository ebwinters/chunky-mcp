import hashlib
import json
import types
import uuid
from mcp.server.fastmcp import FastMCP, Context
from mcp import types
import asyncio
from chunker import ResponseChunker

mcp = FastMCP("AsyncDemoServer")
chunker = ResponseChunker()

MAX_RESPONSE_SIZE = 50000
MAX_CHUNK_SIZE = 30000

@mcp.tool()
async def read_response_chunk(file_id: str, chunk_number: int = 0) -> list[types.TextContent]:
    """Read a chunk of a previously saved large response"""
    
    if file_id not in chunker.temp_files:
        return [types.TextContent(
            type="text",
            text=f"Error: file_id '{file_id}' not found or expired"
        )]
    
    file_info = chunker.temp_files[file_id]
    
    try:
        with open(file_info['file_path'], 'r') as f:
            # Read the entire file (for JSON parsing)
            content = f.read()
            
        # Calculate chunk boundaries
        start_pos = chunk_number * MAX_CHUNK_SIZE
        end_pos = min(start_pos + MAX_CHUNK_SIZE, len(content))
        
        if start_pos >= len(content):
            return [types.TextContent(
                type="text",
                text=f"Chunk {chunk_number} is beyond end of file. Total chunks available: {(len(content) + MAX_CHUNK_SIZE - 1) // MAX_CHUNK_SIZE}"
            )]
        
        chunk_content = content[start_pos:end_pos]
        total_chunks = (len(content) + MAX_CHUNK_SIZE - 1) // MAX_CHUNK_SIZE
        
        return [types.TextContent(
            type="text",
            text=f"Chunk {chunk_number + 1}/{total_chunks} of {file_id}:\n\n{chunk_content}"
        )]
        
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error reading chunk: {str(e)}"
        )]

@mcp.tool()
def some_existing_tool() -> list[types.TextContent]:
    """Gets a list of all the employees in the system"""
    def is_response_too_large(response_data):
        return len(json.dumps(response_data)) > MAX_RESPONSE_SIZE
    
    # Simulate a large response
    with open("large.json", "r", encoding="utf-8") as f:
        response_data = json.load(f)
    
    # Check if response is too large
    if is_response_too_large(response_data):
        # Create a hash of the parameters for unique identification
        unique_hash = str(uuid.uuid4())[:8]  # Take first 8 chars of the UUID        
        # Save to file and return metadata
        chunk_info = chunker.save_large_response(response_data, "your_tool_name", unique_hash)

        return [types.TextContent(
            type="text",
            text=json.dumps(chunk_info, indent=2)
        )]
    
    # Return normally if response is small enough
    return [types.TextContent(
        type="text",
        text=json.dumps(response_data, indent=2)
    )]

if __name__ == "__main__":
    mcp.run(transport="stdio")