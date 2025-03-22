"""Configuration handling for Ritual toolkit.

This module provides functionality for loading and managing Ritual network
configuration, including contract addresses and ABIs.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class ABIInput(BaseModel):
    """ABI input parameter.
    
    Attributes:
        name: Parameter name
        type: Parameter type
        internal_type: Internal type (optional)
    """
    name: str
    type: str
    internal_type: Optional[str] = Field(None, alias="internalType")


class ABIOutput(BaseModel):
    """ABI output parameter.
    
    Attributes:
        name: Parameter name
        type: Parameter type
        internal_type: Internal type (optional)
    """
    name: str
    type: str
    internal_type: Optional[str] = Field(None, alias="internalType")


class ABIItem(BaseModel):
    """ABI item.
    
    Attributes:
        type: Item type (function, event, etc.)
        name: Item name (optional)
        inputs: Input parameters (optional)
        outputs: Output parameters (optional)
        stateMutability: State mutability (optional)
    """
    type: str
    name: Optional[str] = None
    inputs: Optional[List[ABIInput]] = None
    outputs: Optional[List[ABIOutput]] = None
    stateMutability: Optional[str] = None


class RitualConfig(BaseModel):
    """Configuration for Ritual network.
    
    Attributes:
        contract_address: Address of the Ritual contract
        raw_abi: Raw ABI data for the contract
        schedule_fn: Name of function to schedule transactions
        cancel_fn: Name of function to cancel transactions
    """
    contract_address: str
    raw_abi: List[Dict]
    schedule_fn: str
    cancel_fn: str
    
    @property
    def abi(self) -> List[ABIItem]:
        """Get the contract ABI.
        
        For backward compatibility with code that expects the abi attribute.
        
        Returns:
            List[ABIItem]: Contract ABI
        """
        return [ABIItem(**item) for item in self.raw_abi]


def find_config_file(name: str = "ritual_config.json") -> Optional[Path]:
    """Find the ritual config file by searching common locations.
    
    Args:
        name: Name of the config file to find
        
    Returns:
        Path to config file if found, None otherwise
    """
    # Check current directory first
    if (current_dir := Path.cwd() / name).exists():
        return current_dir
        
    # Check package examples directory
    if (pkg_dir := Path(__file__).parent.parent / "examples" / name).exists():
        return pkg_dir
        
    # Check environment variable
    if config_path := os.getenv("RITUAL_CONFIG_PATH"):
        if (env_path := Path(config_path)).exists():
            return env_path
            
    return None


def load_ritual_config(config: Optional[Union[str, dict, Path]] = None) -> RitualConfig:
    """Load Ritual network configuration.
    
    Args:
        config: Path to config file, config dict, or None to use default
        
    Returns:
        RitualConfig object with loaded configuration
        
    Raises:
        FileNotFoundError: If config file does not exist
        ValueError: If config is invalid
    """
    # If config is None or empty string, try to find config file
    if not config:
        if config_path := find_config_file():
            config = config_path
        else:
            raise FileNotFoundError(
                "Could not find ritual_config.json in any of these locations:\n"
                "- Current directory\n"
                "- Package examples directory\n"
                "- RITUAL_CONFIG_PATH environment variable"
            )
        
    # If config is a string or Path, load from file
    if isinstance(config, (str, Path)):
        config_path = Path(config)
        if not config_path.is_absolute():
            # If path is relative, make it absolute from current working directory
            config_path = Path.cwd() / config_path
        try:
            with open(config_path) as f:
                config = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Config file not found: {config_path}. "
                "Please provide a valid path to ritual_config.json"
            )
            
    # Validate config
    if not isinstance(config, dict):
        raise ValueError("Config must be a dictionary")
        
    required_fields = {"contract_address", "abi", "schedule_fn", "cancel_fn"}
    if missing := required_fields - set(config.keys()):
        raise ValueError(f"Missing required fields in config: {missing}")
        
    return RitualConfig(
        contract_address=config["contract_address"],
        raw_abi=config["abi"],
        schedule_fn=config["schedule_fn"],
        cancel_fn=config["cancel_fn"]
    )
