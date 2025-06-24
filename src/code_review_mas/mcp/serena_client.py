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

# ======================== serena tools ==================
async def active_project(session: ClientSession, project_path: str) -> CallToolResult:
    logger.info("Calling 'active_project' tool'")
    return await session.call_tool(
        name='activate_project',
        arguments={
            'project': project_path
        },
    )
    
async def list_dir(session: ClientSession, relative_path: str) -> CallToolResult:
    return await session.call_tool(
        name='list_dir',
        arguments={
            'relative_path': relative_path,
            'recursive': True,
            'max_answer_chars': 200000
        },
    )

async def onboarding(session: ClientSession) -> CallToolResult:
    return await session.call_tool(
        name='onboarding'
    )

async def check_onboarding_performed(session: ClientSession) -> CallToolResult:
    return await session.call_tool(
        name='check_onboarding_performed'
    )

async def get_symbols_overview(session: ClientSession, relative_path: str) -> CallToolResult:
    return await session.call_tool(
        name="get_symbols_overview",
        arguments={
            'relative_path': relative_path,
            'max_answer_chars': 200000
        },
    )

async def execute_shell_command(session: ClientSession) -> CallToolResult:
    return await session.call_tool(
        name='execute_shell_command',
        arguments={
            'command': "/home/dino/Documents/dino-research/code-review-mas/.venv/bin/semgrep scan --config=auto --json ."
        }
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
        await get_tool_detail(session, 'execute_shell_command')
        
        # result = await active_project(session, project_path)
        # result = await list_dir(session, ".")
        # result = await onboarding(session)
        # result = await check_onboarding_performed(session)
        # result = await get_symbols_overview(session, relative_path=".")
        result = await execute_shell_command(session)
        
        log_call_tool_result(result)

        
        
@click.command()
@click.option('--host', default='0.0.0.0', help='SSE Host')
@click.option('--port', default='50051', help='SSE Port')
@click.option('--project', help='Project path')
def cli(host, port, project):
    """A command-line client to interact with the Agent Cards MCP server."""
    asyncio.run(main(host, port, project,))


if __name__ == '__main__':
    cli()