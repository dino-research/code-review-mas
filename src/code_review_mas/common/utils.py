# type: ignore
import logging
import os

import google.generativeai as genai

from code_review_mas.common.types import ServerConfig


logger = logging.getLogger(__name__)


def init_api_key():
    """Initialize the API key for Google Generative AI."""
    if not os.getenv('GOOGLE_API_KEY'):
        logger.error('GOOGLE_API_KEY is not set')
        raise ValueError('GOOGLE_API_KEY is not set')

    genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))


def config_logger(logger):
    """Logger specific config, avoiding clutter in enabling all loggging."""
    # TODO: replace with env
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

def get_mcp_server_config(server_name: str) -> ServerConfig:
    """Get the MCP server configuration."""
    if server_name=="serena":
        return ServerConfig(
            host='0.0.0.0',
            port=50051,
            transport='sse',
            url='http://0.0.0.0:50051/sse')
    elif server_name=="semgrep":
        return ServerConfig(
            host='0.0.0.0',
            port=50052,
            transport='sse',
            url='http://0.0.0.0:50052/sse')
    else:
        raise(f"Not Found: {server_name}")
