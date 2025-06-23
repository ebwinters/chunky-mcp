import json
import types
import uuid
from mcp.server.fastmcp import FastMCP, Context
from mcp import types
from chunker import ResponseChunker
import requests

mcp = FastMCP("AsyncDemoServer")
chunker = ResponseChunker()

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
        start_pos = chunk_number * chunker.MAX_CHUNK_SIZE
        end_pos = min(start_pos + chunker.MAX_CHUNK_SIZE, len(content))

        if start_pos >= len(content):
            return [types.TextContent(
                type="text",
                text=f"Chunk {chunk_number} is beyond end of file. Total chunks available: {(len(content) + chunker.MAX_CHUNK_SIZE - 1) // chunker.MAX_CHUNK_SIZE}"
            )]
        
        chunk_content = content[start_pos:end_pos]
        total_chunks = (len(content) + chunker.MAX_CHUNK_SIZE - 1) // chunker.MAX_CHUNK_SIZE

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
def get_employees() -> list[types.TextContent]:
    """
    Gets a list of all the employees in the system from the database
    When the user asks for a list of employees, this tool is called.
    """
    def is_response_too_large(response_data):
        return len(json.dumps(response_data)) > chunker.MAX_RESPONSE_SIZE

    # Simulate a large response
    response = requests.get("https://microsoftedge.github.io/Demos/json-dummy-data/128KB.json")
    response.raise_for_status()
    response_data = response.json()
    
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