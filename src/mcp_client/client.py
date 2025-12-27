
from contextlib import asynccontextmanager
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession
import os
from typing import Optional, Dict

@asynccontextmanager
async def connect_mcp_sse(url: str):
    """
    Connect to an MCP server via SSE.
    """
    async with sse_client(url) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session

@asynccontextmanager
async def connect_mcp_stdio(command: str, args: list[str], env: Optional[Dict[str, str]] = None):
    """
    Connect to an MCP server via Stdio.
    """
    server_params = StdioServerParameters(
        command=command,
        args=args,
        env=env
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session
