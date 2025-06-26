# type: ignore

import json
import logging
import sys

from pathlib import Path

import click
import httpx
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import AgentCard
from code_review_mas.common import prompts
from code_review_mas.common.agent_executor import GenericAgentExecutor
from serena_agent import SerenaAgent
from dotenv import load_dotenv
load_dotenv()


logger = logging.getLogger(__name__)

def get_agent(agent_card: AgentCard):
    """Get the agent, given an agent card."""
    try:
        if agent_card.name == 'Serena Planning Agent':
            return SerenaAgent(
                agent_name=agent_card.name,
                description=agent_card.description,
                instructions=prompts.SERENA_PLANNING_INSTRUCTION,
            )
        if agent_card.name == 'Serena Code Q&A Agent':
            return SerenaAgent(
                agent_name=agent_card.name,
                description=agent_card.description,
                instructions=prompts.SERENA_INTERACTIVE_INSTRUCTION,
            )
        
            # return LangraphCarRentalAgent()
    except Exception as e:
        raise e

@click.command()
@click.option('--host', 'host', default='0.0.0.0')
@click.option('--port', 'port')
@click.option('--agent-card', 'agent_card')
def main(host, port, agent_card):
    """Starts an Agent server."""
    try:
        if not agent_card:
            raise ValueError('Agent card is required')
        with Path.open(agent_card) as file:
            data = json.load(file)
        agent_card = AgentCard(**data)

        client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=GenericAgentExecutor(agent=get_agent(agent_card)),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(client),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card, http_handler=request_handler
        )

        logger.info(f'Starting server on {host}:{port}')

        uvicorn.run(server.build(), host=host, port=port)
    except FileNotFoundError:
        logger.error(f"Error: File '{agent_card}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Error: File '{agent_card}' contains invalid JSON.")
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
