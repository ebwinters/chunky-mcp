from mcp.server.fastmcp import FastMCP, Context
import asyncio

# Create an MCP server instance
mcp = FastMCP("AsyncDemoServer")

# Define an asynchronous tool
@mcp.tool()
async def fetch_data_from_api(url: str, ctx: Context) -> str:
    """
    Fetches data from a given URL asynchronously.
    Simulates a network request with a delay.
    """
    ctx.info(f"Fetching data from: {url}")
    await asyncio.sleep(2)  # Simulate network delay
    return f"Data successfully fetched from {url}"

# Define another asynchronous tool that uses progress reporting
@mcp.tool()
async def process_items(items: list[str], ctx: Context) -> str:
    """
    Processes a list of items asynchronously with progress updates.
    """
    processed_count = 0
    total_items = len(items)
    for i, item in enumerate(items):
        ctx.info(f"Processing item: {item}")
        await asyncio.sleep(0.5)  # Simulate processing time
        processed_count += 1
        await ctx.report_progress(processed_count, total_items)
    return f"Finished processing {processed_count} items."

# Run the MCP server
if __name__ == "__main__":
    # You can choose the transport, e.g., "stdio" for standard I/O
    # or "sse" for Server-Sent Events if integrated with a web server like FastAPI
    mcp.run(transport="stdio")