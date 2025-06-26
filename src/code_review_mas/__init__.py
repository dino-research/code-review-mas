import click
from code_review_mas.mcp import orchestrator_server

@click.command()
@click.option('--run', 'command', default='orchestrator-server', help='Command to run')
@click.option(
    '--host',
    'host',
    default='localhost',
    help='Host on which the server is started or the client connects to',
)
@click.option(
    '--port',
    'port',
    default=50050,
    help='Port on which the server is started or the client connects to',
)
@click.option(
    '--transport',
    'transport',
    default='stdio',
    help='MCP Transport',
)
def main(command, host, port, transport) -> None:
    # TODO: Add other servers, perhaps dynamic port allocation
    if command == 'orchestrator-server':
        orchestrator_server.serve(host, port, transport)
    else:
        raise ValueError(f'Unknown run option: {command}')