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
        logger.info(f"tool: - {tool.name}")
        if tool.name == tool_name:
            logger.info(f"Found: ")
            logger.info(f"- Name: {tool.name}")
            logger.info(f"- Description: {tool.description}")
            logger.info(f"- inputSchema: \n {json.dumps(tool.inputSchema, indent=2)}")
            logger.info(f"- Annotations: {tool.annotations}")

# ======================== serena tools ==================
async def semgrep_rule_schema(session: ClientSession) -> CallToolResult:
    return await session.call_tool(
        name='semgrep_rule_schema'
    )


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

async def main(host, port, project_path):
    logger.info('Starting Client to connect to MCP')
    async with init_session(host, port) as session:
        await get_tool_detail(session, 'semgrep_scan')
        
        # result = await semgrep_rule_schema(session)
        # log_call_tool_result(result)

        
        
@click.command()
@click.option('--host', default='0.0.0.0', help='SSE Host')
@click.option('--port', default='50052', help='SSE Port')
@click.option('--project', help='Project path')
def cli(host, port, project):
    """A command-line client to interact with the Agent Cards MCP server."""
    asyncio.run(main(host, port, project,))


if __name__ == '__main__':
    cli()