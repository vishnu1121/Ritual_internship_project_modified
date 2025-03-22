"""StakingOptimizer agent configuration."""

from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain.agents import AgentType, initialize_agent
from langchain_core.language_models import BaseLLM

from ..character.profile import STAKE_MATE_PROFILE, get_response
from ..operations.staking import StakingOperations
from ..safety.validator import TransactionValidator
from ..autocompound.scheduler import AutoCompoundScheduler

def create_staking_tools(
    staking_ops: StakingOperations,
    validator: TransactionValidator,
    scheduler: AutoCompoundScheduler
) -> list[Tool]:
    """Create tools for the staking agent."""
    return [
        Tool(
            name="StakeTokens",
            func=staking_ops.stake,
            description="Stake tokens with gas optimization and safety checks"
        ),
        Tool(
            name="UnstakeTokens",
            func=staking_ops.unstake,
            description="Unstake tokens with gas optimization and safety checks"
        ),
        Tool(
            name="GetStakingPosition",
            func=staking_ops.get_position,
            description="Get current staking position and rewards"
        ),
        Tool(
            name="ScheduleTransaction",
            func=scheduler.schedule_transaction,
            description="Schedule a future staking transaction"
        ),
        Tool(
            name="SetupAutoCompound",
            func=scheduler.setup_auto_compound,
            description="Setup automatic reward compounding"
        ),
        Tool(
            name="ValidateTransaction",
            func=validator.validate_transaction,
            description="Validate transaction parameters and simulate execution"
        ),
    ]

def create_agent_prompt() -> PromptTemplate:
    """Create the agent's prompt template."""
    template = f"""You are {STAKE_MATE_PROFILE['name']}, {STAKE_MATE_PROFILE['personality']}.

Your expertise includes: {', '.join(STAKE_MATE_PROFILE['expertise'])}

When communicating, you should:
{chr(10).join('- ' + style for style in STAKE_MATE_PROFILE['communication_style'])}

Please respond with the following format:
"Action: [action name]
Parameters: [parameter values]
Reasoning: [explanation of the action]"

You can ask for help or clarification by responding with "Help" or "Clarify".
"""

def initialize_staking_agent(llm: BaseLLM, tools: list[Tool], prompt: PromptTemplate) -> AgentType:
    """Initialize the staking agent."""
    return initialize_agent(llm, tools, prompt, name="StakingOptimizer")

def get_staking_agent(llm: BaseLLM, staking_ops: StakingOperations, validator: TransactionValidator, scheduler: AutoCompoundScheduler) -> AgentType:
    """Get the staking agent."""
    tools = create_staking_tools(staking_ops, validator, scheduler)
    prompt = create_agent_prompt()
    return initialize_staking_agent(llm, tools, prompt)