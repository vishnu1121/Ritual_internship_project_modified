"""Example usage of the Ritual toolkit.

This example demonstrates using the Ritual toolkit in both mock and non-mock modes.
The mock mode is useful for testing and development, while non-mock mode
interacts with a real blockchain.

Environment Variables:
    OPENAI_API_KEY: OpenAI API key for the language model
    RITUAL_PRIVATE_KEY: Ethereum private key (required if MOCK=false)
    RITUAL_RPC_URL: Ethereum RPC URL (required if MOCK=false)
    RITUAL_CONFIG_PATH: Path to ritual config file
    MOCK: Set to "true" for mock mode, "false" for real blockchain
"""

import os
import uuid
import logging
from typing import Dict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from langchain_ritual_toolkit import RitualToolkit


def setup_logging():
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def is_mock_mode() -> bool:
    """Check if we should run in mock mode.
    
    Returns:
        bool: True if MOCK environment variable is "true", False otherwise
    """
    return os.getenv("MOCK", "false").lower() == "true"


def create_agent(mock_mode: bool = False) -> Dict:
    """Create a LangChain agent with Ritual toolkit.
    
    Args:
        mock_mode: Whether to use mock mode instead of real blockchain
        
    Returns:
        Dict containing the agent executor
        
    Raises:
        ValueError: If required environment variables are missing in non-mock mode
    """
    
    # Initialize language model
    llm = ChatOpenAI(model="gpt-4")
    
    # Initialize toolkit
    ritual_agent_toolkit = RitualToolkit(
        private_key=os.getenv("RITUAL_PRIVATE_KEY"),
        rpc_url=os.getenv("RITUAL_RPC_URL"),
        ritual_config=None,  # Let it find the config file automatically
        mock_mode=mock_mode
    )
    
    # Get tools and create agent
    tools = ritual_agent_toolkit.get_tools()
    return create_react_agent(llm, tools, debug=False)


def main():
    """Run the example in either mock or non-mock mode based on MOCK env var."""
    load_dotenv()
    setup_logging()
    
    # Use mock mode based on environment variable
    USE_MOCK = is_mock_mode()
    print(f"Running in {'mock' if USE_MOCK else 'non-mock'} mode")
    
    # Create agent
    agent = create_agent(mock_mode=USE_MOCK)
    
    # Generate a unique job ID
    job_id = uuid.uuid4()
    
    # Schedule a job
    input_state_schedule = {
        "messages": f"""
           please schedule a job, id {job_id} using a gasLimit of 100000, 
           gasPrice 1000000000, frequency 2, and numBlocks 10
        """,
    }
    output_state = agent.invoke(input_state_schedule)
    print(output_state["messages"][-1].content)
    
    # Optional: Wait for blocks in non-mock mode
    if not USE_MOCK:
        print("\nWaiting for ~2 blocks...")
        from time import sleep
        sleep(24)  # Approximately 2 blocks
    
    # Cancel the job
    input_state_cancel = {
        "messages": f"""
           please cancel the scheduled job with id {job_id}
        """,
    }
    output_state = agent.invoke(input_state_cancel)
    print(output_state["messages"][-1].content)


if __name__ == "__main__":
    main()
