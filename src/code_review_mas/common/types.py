
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class ServerConfig(BaseModel):
    """Server Confgiguration."""

    host: str
    port: int
    transport: str
    url: str
    
