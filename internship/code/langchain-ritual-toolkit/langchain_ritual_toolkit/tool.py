"""
This tool allows agents to interact with the Ritual network.
"""

from __future__ import annotations

from typing import Any, Optional, Type, Union

from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from langchain_ritual_toolkit.api import RitualAPI
from langchain_ritual_toolkit.mock import MockRitualAPI


class RitualTool(BaseTool):
    """Tool for interacting with Ritual network.
    
    This tool provides an interface for LangChain agents to interact with
    the Ritual network through either the real RitualAPI or MockRitualAPI.
    
    Attributes:
        name: Name of the tool
        description: Description of what the tool does
        method: Method to call on the ritual API
        ritual_api: API instance for blockchain interactions
        args_schema: Optional schema for tool arguments
    """
    
    name: str = ""
    description: str = ""
    method: str
    ritual_api: Union[RitualAPI, MockRitualAPI] = Field(
        ..., description="API instance for blockchain interactions"
    )
    args_schema: Optional[Type[BaseModel]] = None

    def _run(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> str:
        """Run the tool.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            str: Result of the operation
            
        Raises:
            Exception: If the operation fails
        """
        return self.ritual_api.run(self.method, *args, **kwargs)