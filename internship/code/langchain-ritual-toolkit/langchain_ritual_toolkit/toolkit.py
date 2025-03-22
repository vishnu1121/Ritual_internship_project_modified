"""Ritual toolkit for LangChain.

This module provides the main toolkit class for interacting with the Ritual
network through LangChain.

Example:
    >>> from langchain_ritual_toolkit import RitualToolkit
    >>> toolkit = RitualToolkit(
    ...     private_key="0x...",
    ...     rpc_url="https://...",
    ...     ritual_config="ritual_config.json"
    ... )
    >>> tools = toolkit.get_tools()
"""

from typing import List, Optional, Union

from pydantic import PrivateAttr

from langchain_ritual_toolkit.api import RitualAPI
from langchain_ritual_toolkit.configuration import RitualConfig, load_ritual_config
from langchain_ritual_toolkit.mock import MockRitualAPI, MockConfig
from langchain_ritual_toolkit.tool import RitualTool
from langchain_ritual_toolkit.tools import generate_tools


class RitualToolkit:
    """Toolkit for Ritual network operations.
    
    This toolkit provides tools for interacting with the Ritual network,
    including transaction scheduling and management. It supports both real
    blockchain interactions and mock mode for testing.
    
    Attributes:
        mock_mode: Whether to use mock mode instead of real blockchain
        private_key: Ethereum private key (only required if not in mock mode)
        rpc_url: Ethereum RPC URL (only required if not in mock mode)
        _tools: List of LangChain tools for Ritual operations
        _ritual_api: API instance for blockchain interactions
        _ritual_config: Ritual network configuration
    """
    
    _tools: List[RitualTool] = PrivateAttr(default=[])
    _ritual_api: Union[RitualAPI, MockRitualAPI] = PrivateAttr(default=None)
    _ritual_config: RitualConfig = PrivateAttr(default=None)

    def __init__(
        self,
        private_key: Optional[str] = None,
        rpc_url: Optional[str] = None,
        ritual_config: Optional[Union[str, dict]] = None,
        mock_mode: bool = False,
    ) -> None:
        """Initialize the toolkit.
        
        Args:
            private_key: Ethereum private key, required if not in mock mode
            rpc_url: Ethereum RPC URL, required if not in mock mode
            ritual_config: Path to ritual config file or config dict
            mock_mode: Whether to use mock mode instead of real blockchain
            
        Raises:
            ValueError: If private_key or rpc_url are missing in non-mock mode
        """
        super().__init__()
        
        if not mock_mode:
            if not private_key or not rpc_url:
                raise ValueError(
                    "private_key and rpc_url required when mock_mode=False"
                )
                
            self._ritual_config = load_ritual_config(ritual_config)
            self._ritual_api = RitualAPI(private_key, rpc_url, self._ritual_config)
        
        else:
            self._ritual_config = load_ritual_config(MockConfig)  # type: ignore[arg-type] # MockConfig
            self._ritual_api = MockRitualAPI()
            
        self._tools = [
            RitualTool(
                name=tool["method"],
                description=tool["description"],
                method=tool["method"],
                ritual_api=self._ritual_api,
                args_schema=tool.get("args_schema", None),
            )
            for tool in generate_tools(self._ritual_config)
        ]

    def get_tools(self) -> List[RitualTool]:
        """Get toolkit tools.
        
        Returns:
            List of LangChain tools configured for Ritual operations
        """
        return self._tools