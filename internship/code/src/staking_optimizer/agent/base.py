"""StakingOptimizer agent implementation."""
import os
from typing import Dict, List, Optional, Union
from dotenv import load_dotenv
import uuid
import logging
import json
from decimal import Decimal

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.callbacks import BaseCallbackHandler
from pydantic import BaseModel

from langchain_ritual_toolkit import RitualToolkit
from langchain_ritual_toolkit.mock import MockRitualAPI
from .tools import get_staking_tools
from .character import StakeMateCharacter
from ..safety.validator import SafetyValidator
from ..operations.staking import StakingOperations
from ..operations.view import get_staking_position
from ..commands.parser import CommandParser
from ..commands.models import (
    StakingCommand, StakeCommand, UnstakeCommand,
    CompoundCommand, ViewCommand, InformationalCommand
)
from .models import AgentResponse

logger = logging.getLogger(__name__)

class OpenAILoggingHandler(BaseCallbackHandler):
    """Callback handler for logging OpenAI interactions."""
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        """Log when LLM starts generating."""
        logger.info(f"\n{'='*50}\nLLM Request:")
        for i, prompt in enumerate(prompts):
            logger.info(f"Prompt {i}:\n{prompt}\n")
    
    def on_llm_end(self, response, **kwargs):
        """Log when LLM finishes generating."""
        logger.info(f"\nLLM Response:")
        try:
            # Try to get function call details
            if hasattr(response, 'additional_kwargs') and 'function_call' in response.additional_kwargs:
                func_call = response.additional_kwargs['function_call']
                logger.info(f"Function Call:\n  Name: {func_call.get('name')}\n  Arguments: {func_call.get('arguments')}")
            # Log the full response
            if hasattr(response, 'model_dump'):
                logger.info(f"Full Response:\n{json.dumps(response.model_dump(), indent=2)}")
            else:
                logger.info(f"Full Response:\n{json.dumps(response.dict(), indent=2)}")
        except Exception as e:
            logger.error(f"Error logging response: {e}")
            logger.info(f"Raw Response: {response}")
        logger.info(f"{'='*50}\n")
    
    def on_llm_error(self, error, **kwargs):
        """Log when LLM errors."""
        logger.error(f"\nLLM Error: {str(error)}")
        
    def on_tool_start(self, serialized, input_str, **kwargs):
        """Log when a tool starts."""
        logger.info(f"\nTool Start: {serialized.get('name', 'Unknown Tool')}")
        logger.info(f"Input: {input_str}")
        
    def on_tool_end(self, output, **kwargs):
        """Log when a tool ends."""
        logger.info(f"\nTool Output: {output}")
        
    def on_tool_error(self, error, **kwargs):
        """Log when a tool errors."""
        logger.error(f"\nTool Error: {str(error)}")

    def on_chain_start(self, serialized, inputs, **kwargs):
        """Log when a chain starts."""
        logger.info(f"\nChain Start: {serialized.get('name', 'Unknown Chain')}")
        logger.info(f"Inputs: {json.dumps(inputs, indent=2)}")

    def on_chain_end(self, outputs, **kwargs):
        """Log when a chain ends."""
        logger.info(f"\nChain Output:")
        logger.info(f"Outputs: {json.dumps(outputs, indent=2)}")

    def on_agent_action(self, action, **kwargs):
        """Log agent actions."""
        logger.info(f"\nAgent Action:")
        logger.info(f"Tool: {action.tool}")
        logger.info(f"Input: {action.tool_input}")
        logger.info(f"Thought: {action.log}")

    def on_agent_finish(self, finish, **kwargs):
        """Log agent finish."""
        logger.info(f"\nAgent Finish:")
        logger.info(f"Output: {finish.return_values}")
        logger.info(f"Log: {finish.log}")


# Create prompt template for the agent
AGENT_PROMPT = PromptTemplate.from_template(
    """You are StakeMate, a helpful staking assistant. You help users optimize their staking positions by:
    - Monitoring APR changes
    - Suggesting optimal stake amounts
    - Automating staking transactions
    - Managing rewards
    
    When users ask informational questions about staking, provide detailed explanations that include:
    1. Key concepts and terminology
    2. Step-by-step instructions if applicable
    3. Best practices and recommendations
    4. Any relevant risks or considerations
    
    For staking operations, always:
    1. Verify the user has sufficient balance
    2. Check that the address is valid
    3. Confirm the operation parameters
    4. Execute the transaction
    5. Verify the transaction succeeded
    
    You have access to the following tools:
    
    {tools}
    
    Use the following format:
    
    Question: the input question you must answer
    Thought: you should always think about what to do
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question
    
    Begin!
    
    Question: {input}
    Thought:{agent_scratchpad}"""
)


class AgentState(BaseModel):
    """State of the agent.
    
    Attributes:
        messages: List of message dictionaries
        thread_id: Unique identifier for the conversation
        output: Optional output from the agent
    """
    messages: List[Dict[str, str]]
    thread_id: str
    output: Optional[str] = None


class StakingOptimizerAgent:
    """StakingOptimizer agent for optimizing staking rewards.
    
    This agent uses LangChain's function calling and React framework to handle
    staking operations. It processes natural language commands into strongly-typed
    command models and executes them using appropriate tools.
    
    Attributes:
        llm: Language model for agent
        toolkit: RitualToolkit for blockchain interactions
        character: Agent character definition
        validator: Safety validator
        operations: Staking operations handler
        command_parser: Command parser for natural language input
        tools: List of available tools
        agent: React agent instance
        agent_executor: Agent executor instance
        compound_strategy: Compound strategy instance
    """

    def __init__(
        self,
        private_key: str,
        rpc_url: str,
        config_path: str,
        model_name: str = "openai/gpt-4o-2024-11-20",
        temperature: float = 0.7,
        command_parser: Optional[CommandParser] = None,
        safety_validator: Optional[SafetyValidator] = None,
        compound_strategy: Optional["ThresholdStrategy"] = None,
        mock_blockchain: Optional["MockBlockchainState"] = None,
        mock_contract: Optional["MockStakingContract"] = None,
    ):
        """Initialize the StakingOptimizer agent.

        Args:
            private_key: Ethereum private key for signing transactions
            rpc_url: RPC URL for blockchain connection
            config_path: Path to Ritual config file
            model_name: Name of the OpenAI model to use
            temperature: Temperature setting for the model
            command_parser: Optional command parser instance
            safety_validator: Optional safety validator instance
            compound_strategy: Optional compound strategy instance
            mock_blockchain: Optional mock blockchain state for testing
            mock_contract: Optional mock staking contract for testing
        """
        # Load environment variables
        load_dotenv()

        # Initialize components
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            callbacks=[OpenAILoggingHandler()],
            base_url=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
        )
        self.toolkit = RitualToolkit(
            private_key=private_key,
            rpc_url=rpc_url,
            ritual_config=config_path,
            mock_mode=mock_blockchain is not None,
        )
        
        if mock_blockchain is not None:
            self.toolkit.api = MockRitualAPI()
            self.toolkit.api.blockchain = mock_blockchain
            self.toolkit.api.contract = mock_contract

        self.character = StakeMateCharacter()
        self.validator = safety_validator or SafetyValidator()
        self.operations = StakingOperations(self.toolkit, compound_strategy)
        self.command_parser = command_parser or CommandParser()
        self.compound_strategy = compound_strategy
        
        # Create agent with tools
        self.tools = self._get_tools()
        self.agent = create_react_agent(self.llm, self.tools, AGENT_PROMPT)
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            handle_parsing_errors=True,  # Handle cases where LLM output includes both action and final answer
            async_mode=True  # Enable async mode
        )

    def _get_tools(self):
        """Get the list of tools available to the agent.
    
        Returns:
            List of LangChain tools for blockchain interactions.
        """
        # If mock objects are provided, use them directly
        if hasattr(self, 'blockchain') and hasattr(self, 'contract'):
            return get_staking_tools(
                self.blockchain,
                self.contract,
                self.validator
            )
        # Otherwise use the toolkit's API
        return get_staking_tools(
            self.toolkit.api.blockchain,
            self.toolkit.api.contract,
            self.validator
        )

    def _validate_request(self, state: AgentState) -> bool:
        """Validate a user request.

        Args:
            state: Current agent state

        Returns:
            Whether the request is valid
        """
        request = state.messages[-1]["content"]
        is_valid, reason = self.validator.validate_request(request)
        if not is_valid:
            state.output = reason
        return is_valid

    async def invoke(self, state: AgentState) -> AgentState:
        """Invoke the agent.

        Args:
            state: Initial agent state

        Returns:
            Final agent state
        """
        try:
            if not self._validate_request(state):
                error_message = self.validator.get_last_error_message()
                state.output = error_message
                return state

            # Convert state to format expected by agent
            input_dict = {
                "input": state.messages[0]["content"],
                "agent_scratchpad": "",
                "tools": "\n".join(f"{tool.name}: {tool.description}" for tool in self.tools),
                "tool_names": ", ".join(tool.name for tool in self.tools)
            }

            # Run agent
            response = await self.agent_executor.ainvoke(input_dict)
            state.output = response["output"]
            return state
        except Exception as e:
            error_msg = f"Error processing request: {str(e)}"
            logger.error(error_msg)
            state.output = error_msg
            return state

    async def handle_request(self, request: str) -> AgentResponse:
        """Handle a user request.
        
        Args:
            request: User's request string
            
        Returns:
            AgentResponse containing the result
        """
        try:
            # Parse request into command
            command = self.command_parser.parse_request(request)
            
            # Execute command
            if isinstance(command, InformationalCommand) and command.topic == "help":
                help_msg = """I can help you with:

- Staking and unstaking tokens
- Viewing your staking position
- Monitoring APR changes
- Compounding rewards
- Optimizing your returns

Just ask me what you'd like to do!"""
                return AgentResponse(success=True, message=help_msg)
            
            return await self.execute_command(command)
            
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}", exc_info=True)
            return AgentResponse(
                success=False,
                message=str(e),
                error=str(e)
            )

    async def execute_command(self, command) -> AgentResponse:
        """Execute a parsed command.
        
        Args:
            command: The command to execute
            
        Returns:
            AgentResponse: Response with success status and message
        """
        try:
            if isinstance(command, StakeCommand):
                # Validate stake amount
                if command.amount <= 0:
                    return AgentResponse(
                        success=False,
                        message="Stake amount must be greater than 0 ETH",
                        error="Invalid stake amount"
                    )
                
                # Use default address if 'user' is provided
                address = "0xdefault" if command.address == "user" else command.address
                
                # Execute stake
                result = await self.operations.stake(address, command.amount, command.validator)
                if isinstance(result, dict) and "status" in result:
                    msg = f"Successfully staked {result['value']} from {result['from']} (Transaction: {result['hash']})"
                    return AgentResponse(success=True, message=msg)
                return AgentResponse(success=True, message=result)
                
            elif isinstance(command, UnstakeCommand):
                # Use default address if 'user' is provided
                address = "0xdefault" if command.address == "user" else command.address
                
                # Execute unstake
                result = await self.operations.unstake(address, command.amount)
                if isinstance(result, dict) and "status" in result:
                    msg = f"Successfully unstaked {result['value']} from {result['from']} (Transaction: {result['hash']})"
                    return AgentResponse(success=True, message=msg)
                return AgentResponse(success=True, message=result)
                
            elif isinstance(command, CompoundCommand):
                # Use default address if 'user' is provided
                address = "0xdefault" if command.address == "user" else command.address
                
                # Execute compound
                result = await self.operations.compound(address)
                if isinstance(result, dict) and "status" in result:
                    msg = f"Successfully compounded rewards for {result['from']} (Transaction: {result['hash']})"
                    return AgentResponse(success=True, message=msg)
                return AgentResponse(success=True, message=result)
                
            elif isinstance(command, ViewCommand):
                # Use default address if 'user' is provided
                address = "0xdefault" if command.address == "user" else command.address
                
                # Get view result
                result = await self.operations.view(address, command.view_type)
                return AgentResponse(success=True, message=result)
                
            elif isinstance(command, InformationalCommand):
                # Handle info request
                if command.topic == "help":
                    # Return a more detailed help message
                    help_msg = """I can help you with:

- Staking and unstaking tokens
- Viewing your staking position
- Monitoring APR changes
- Compounding rewards
- Optimizing your returns

Just ask me what you'd like to do!"""
                    return AgentResponse(success=True, message=help_msg)
                else:
                    return AgentResponse(success=True, message=self.character.format_response(command.topic))
                
            else:
                return AgentResponse(
                    success=False,
                    message=f"Unknown command type: {type(command)}",
                    error="Invalid command type"
                )
                
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return AgentResponse(success=False, message=str(e), error=str(e))
