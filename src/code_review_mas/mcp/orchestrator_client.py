# type:ignore
import asyncio
import json
import os

from contextlib import asynccontextmanager

import click

from fastmcp.utilities.logging import get_logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.sse import sse_client
from mcp.types import CallToolResult, ReadResourceResult, Tool


logger = get_logger(__name__)

env = {
    'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
}

@asynccontextmanager
async def init_session(host, port):
    url = f'http://{host}:{port}/sse'
    async with sse_client(url) as (read_stream, write_stream):
        async with ClientSession(read_stream=read_stream, write_stream=write_stream) as session:
            logger.debug('SSE ClientSession created, initializing...')
            await session.initialize()
            logger.info('SSE ClientSession initialized successfully.')
            yield session

async def get_tool_detail(session: ClientSession, tool_name: str):
    result = await session.list_tools()
    tools: list[Tool] = result.tools
    logger.info(f"Call get_tool_detail for {tool_name}")
    logger.info(f"Total: {len(tools)} tools")
    for tool in tools:
        if tool.name == tool_name:
            logger.info(f"Found: ")
            logger.info(f"- Name: {tool.name}")
            logger.info(f"- Description: {tool.description}")
            logger.info(f"- inputSchema: \n {json.dumps(tool.inputSchema, indent=2)}")
            logger.info(f"- Annotations: {tool.annotations}")

# ======================== tools ==================
async def find_agent(session: ClientSession, query: str) -> CallToolResult:
    logger.info("Calling 'find_agent' tool'")
    return await session.call_tool(
        name='find_agent',
        arguments={
            'query': query
        },
    )

async def find_resource(session: ClientSession, resource) -> ReadResourceResult:
    """Reads a resource from the connected MCP server.

    Args:
        session: The active ClientSession.
        resource: The URI of the resource to read (e.g., 'resource://agent_cards/list').

    Returns:
        The result of the resource read operation.
    """
    logger.info(f'Reading resource: {resource}')
    return await session.read_resource(resource)

# =========================================================

def log_call_tool_result(result: CallToolResult):
    logger.info("============== RESULT ==============")
    logger.info(f"- meta: {result.meta}")
    logger.info(f"- isError: {result.isError}")
    for content in result.content:
        logger.info(f"- type: {content.type}")
        logger.info(f"- annotations: {content.annotations}")
        logger.info(f"- text: {content.text}")
        logger.info("-"*20)
    logger.info("==================================")

async def main(host, port):
    logger.info('Starting Client to connect to MCP')
    async with init_session(host, port) as session:
        # await get_tool_detail(session, 'find_agent')
        # result = await find_agent(session, "Cấu trúc project như thế nào?")
        # log_call_tool_result(result)
        
        result = await find_resource(session, "resource://agent_cards/list")
        logger.info(f"Found resource: \n {result}")
        # Output:
        # meta=None contents=[TextResourceContents(uri=AnyUrl('resource://agent_cards/list'), mimeType='application/json', text='{\n                                         
        #                      "agent_cards": [\n    "resource://agent_cards/serena_interactive_agent",\n    "resource://agent_cards/serena_planning_agent",\n                                     
        #                      "resource://agent_cards/serena_agent"\n  ]\n}')] 

        
        
@click.command()
@click.option('--host', default='0.0.0.0', help='SSE Host')
@click.option('--port', default='50050', help='SSE Port')
def cli(host, port):
    """A command-line client to interact with the Agent Cards MCP server."""
    asyncio.run(main(host, port))


if __name__ == '__main__':
    cli()