"""Command parser for the StakingOptimizer.

This module handles parsing natural language commands into strongly-typed
command models using LangChain's function calling capabilities.
"""

import logging
import json
import os
from typing import Dict, Any, Optional, List
from decimal import Decimal

from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.callbacks import BaseCallbackHandler

from .models import (
    StakingCommand, StakeCommand, UnstakeCommand,
    CompoundCommand, ViewCommand, InformationalCommand
)

logger = logging.getLogger(__name__)

class CommandParseError(Exception):
    """Raised when command parsing fails."""
    pass

class CommandParserLoggingHandler(BaseCallbackHandler):
    """Callback handler for logging command parser interactions."""
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Log when LLM starts generating."""
        logger.info(f"\n{'='*80}\nCommand Parser LLM Request:")
        logger.info(f"Model: {serialized.get('name', 'unknown')}")
        logger.info(f"Input:")
        for i, prompt in enumerate(prompts):
            logger.info(f"\nPrompt {i}:")
            if hasattr(prompt, 'to_messages'):
                messages = prompt.to_messages()
                for msg in messages:
                    logger.info(f"{msg.type}: {msg.content}")
            else:
                logger.info(str(prompt))
        
        if 'invocation_params' in kwargs:
            logger.info(f"\nInvocation params: {json.dumps(kwargs['invocation_params'], indent=2)}")
        logger.info(f"\nTools:")
        for tool in kwargs.get('tools', []):
            logger.info(json.dumps(tool, indent=2))
        logger.info('='*80)
    
    def on_llm_end(self, response, **kwargs):
        """Log when LLM finishes generating."""
        logger.info(f"\n{'='*80}\nCommand Parser LLM Response:")
        try:
            # Log the complete response first
            if hasattr(response, 'model_dump'):
                logger.info(f"Full Response:\n{json.dumps(response.model_dump(), indent=2)}")
            else:
                logger.info(f"Full Response:\n{json.dumps(response.dict(), indent=2)}")

            # Try to get function call details
            if hasattr(response, 'additional_kwargs'):
                logger.info(f"\nAdditional kwargs:\n{json.dumps(response.additional_kwargs, indent=2)}")
                
                if 'tool_calls' in response.additional_kwargs:
                    tool_calls = response.additional_kwargs['tool_calls']
                    logger.info(f"\nTool calls found: {len(tool_calls)}")
                    for i, tool_call in enumerate(tool_calls):
                        logger.info(f"\nTool call {i}:")
                        logger.info(json.dumps(tool_call, indent=2))
                        if 'function' in tool_call:
                            func_call = tool_call['function']
                            logger.info(f"Function Call:\n  Name: {func_call.get('name')}\n  Arguments: {func_call.get('arguments')}")
                else:
                    logger.info("\nNo tool_calls found in additional_kwargs")
            else:
                logger.info("\nNo additional_kwargs found in response")
        except Exception as e:
            logger.error(f"Error logging response: {e}")
            logger.info(f"Raw Response: {response}")
        logger.info(f"{'='*80}\n")
    
    def on_llm_error(self, error, **kwargs):
        """Log when LLM errors."""
        logger.error(f"\nCommand Parser LLM Error: {str(error)}")

class CommandParser:
    """Parser for converting natural language into strongly-typed commands.
    
    This parser uses LangChain's function calling to extract command parameters
    and classify the command type. It handles both direct commands (stake, unstake)
    and informational queries.
    """

    def __init__(self, model_name: str = "openai/gpt-4o-2024-11-20", temperature: float = 0.0):
        """Initialize the command parser.
        
        Args:
            model_name: Name of the language model to use
            temperature: Temperature parameter for model output
        """
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            callbacks=[CommandParserLoggingHandler()],
            base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        )
        self._functions = self._get_command_functions()
        logger.info(f"Command functions: {json.dumps(self._functions, indent=2)}")

    def _get_command_functions(self) -> List[Dict[str, Any]]:
        """Get the list of command functions.
        
        Returns:
            List of function definitions
        """
        stake_fn = {
            "type": "function",
            "function": {
                "name": "stake",
                "description": "Stake ETH into the contract",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {
                            "type": "number",
                            "description": "Amount of ETH to stake"
                        },
                        "validator": {
                            "type": "string",
                            "description": "Optional validator address to stake with",
                        },
                        "address": {
                            "type": "string", 
                            "description": "Ethereum address to stake from",
                            "default": "user"
                        }
                    },
                    "required": ["amount"]
                }
            }
        }
        unstake_fn = {
            "type": "function",
            "function": {
                "name": "unstake",
                "description": "Unstake ETH from the contract. Use 'all' to unstake entire balance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Ethereum address to unstake from",
                            "default": "user"
                        },
                        "amount": {
                            "type": ["number", "string"],
                            "description": "Amount of ETH to unstake, or 'all' to unstake entire balance",
                            "examples": ["5.0", "all"]
                        }
                    },
                    "required": ["amount"]
                }
            }
        }
        compound_fn = {
            "type": "function",
            "function": {
                "name": "compound",
                "description": "Compound staking rewards",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Ethereum address to compound rewards for"
                        }
                    },
                    "required": ["address"]
                }
            }
        }
        view_fn = {
            "type": "function",
            "function": {
                "name": "view",
                "description": "View staking information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "address": {
                            "type": "string",
                            "description": "Ethereum address to view"
                        },
                        "view_type": {
                            "type": "string",
                            "description": "Type of information to view (stake, rewards, position, APR, compound_advice)",
                            "enum": ["stake", "rewards", "position", "APR", "compound_advice"]
                        }
                    },
                    "required": ["address", "view_type"]
                }
            }
        }
        info_fn = {
            "type": "function",
            "function": {
                "name": "info",
                "description": "Get information about staking",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic to get information about",
                            "enum": ["staking_overview", "help", "risks", "rewards", "requirements", "apr_strategy"]
                        }
                    },
                    "required": ["topic"]
                }
            }
        }
        functions = [stake_fn, unstake_fn, compound_fn, view_fn, info_fn]
        return functions

    def parse_request(self, request: str) -> StakingCommand:
        """Parse a natural language request into a staking command.
        
        Args:
            request: Natural language request to parse
            
        Returns:
            StakingCommand: Parsed command
            
        Raises:
            CommandParseError: If parsing fails
        """
        try:
            # Handle simple help requests directly
            request_lower = request.lower().strip()
            if request_lower in ["help", "what can you do", "what can you help with"]:
                return InformationalCommand(topic="help")
                
            logger.info(f"\n{'='*50}\nParsing request: {request}")
            
            # Create system message to help with function calling
            system_message = SystemMessage(
                content="""You are a command parser for a staking application.
Your task is to parse user requests into the appropriate command with parameters.
IMPORTANT: DO NOT ask for clarification - use default values when parameters are missing.

Guidelines:
1. For stake commands, extract the amount and validator address (if provided)
2. For unstake commands:
   - Questions like "How do I unstake?" should use info(topic="help")
   - Questions like "How do I unstake 5 ETH?" should use unstake(address="user", amount=5)
3. For compound commands, ALWAYS use "user" as the default address
4. For view commands, use "user" as default address and "position" as default view type
5. For info commands, extract the topic
6. For questions about whether to compound, use view command with type="compound_advice"
7. For questions about APR values or changes, use view command with type="APR"
   - This includes questions like "What is my current APR?"
   - This includes questions about APR changes, like "Has my APR changed?"
8. For questions about what to do about APR changes, use info command with topic="apr_strategy"
   - This includes questions like "What should I do about reduced APR?"
   - This includes any questions asking for advice about APR changes
9. For general questions about what the agent can do, use info(topic="help")
   - This includes questions like "help", "what can you do?", etc.

Example mappings:
- "I want to stake 5 ETH with validator 0x789" -> stake(amount=5, validator="0x789")
- "Stake 10 ETH" -> stake(amount=10)
- "Unstake all my ETH" -> unstake(address="user", amount="all")
- "How do I unstake?" -> info(topic="help")
- "What can you help me with?" -> info(topic="help")
- "Help" -> info(topic="help")
- "Compound my rewards" -> compound(address="user")
- "Show my position" -> view(address="user", view_type="position")
- "Tell me about staking risks" -> info(topic="risks")
- "Should I compound my rewards?" -> view(address="user", view_type="compound_advice")
- "What is the current APR?" -> view(address="user", view_type="APR")
- "What should I do about reduced APR?" -> info(topic="apr_strategy")
- "Help me understand APR changes" -> info(topic="apr_strategy")

DEFAULTS (use these when parameters are not specified):
- ALWAYS use "user" as the default address 
- Use "position" as the default view type
- Assume amounts are in ETH"""
            )

            # Call LLM to parse request
            messages = [
                system_message,
                HumanMessage(content=request)
            ]

            # Get response with function calling
            llm_with_tools = self.llm.bind_tools(self._functions)
            response = llm_with_tools.invoke(messages)
            
            # Debug log
            logger.info(f"Response type: {type(response)}")
            logger.info(f"Response dir: {dir(response)}")
            
            # Extract function call
            if isinstance(response, AIMessage):
                if not hasattr(response, 'additional_kwargs') or 'tool_calls' not in response.additional_kwargs:
                    # If no tool calls, default to help
                    return InformationalCommand(topic="help")

                tool_call = response.additional_kwargs['tool_calls'][0]
                
                # Get function name and arguments
                func_name = tool_call['function']['name']
                func_args = json.loads(tool_call['function']['arguments'])

                # Create command based on function name
                if func_name == "stake":
                    return StakeCommand(
                        address=func_args.get("address", "user"),
                        amount=func_args["amount"],
                        validator=func_args.get("validator")
                    )
                elif func_name == "unstake":
                    return UnstakeCommand(
                        address=func_args.get("address", "user"),
                        amount=func_args["amount"]
                    )
                elif func_name == "compound":
                    return CompoundCommand(
                        address=func_args.get("address", "user")
                    )
                elif func_name == "view":
                    cmd = ViewCommand(
                        address=func_args.get("address", "user"),
                        view_type=func_args.get("view_type", "position")
                    )
                    cmd.original_request = request
                    return cmd
                elif func_name == "info":
                    return InformationalCommand(
                        topic=func_args["topic"]
                    )
                else:
                    # Unknown function, default to help
                    return InformationalCommand(topic="help")
            else:
                # Unknown response type, default to help
                return InformationalCommand(topic="help")
        except Exception as e:
            logger.error(f"Error parsing request: {str(e)}", exc_info=True)
            # On any error, default to help
            return InformationalCommand(topic="help")
