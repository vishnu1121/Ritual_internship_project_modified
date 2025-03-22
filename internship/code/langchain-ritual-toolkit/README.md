# Langchain Ritual Toolkit

A LangChain-based toolkit for interacting with the Ritual network. This toolkit provides tools for scheduling and managing blockchain transactions through natural language interactions.

## Features

- Schedule blockchain transactions with customizable parameters
- Cancel scheduled transactions
- Mock mode for testing and development
- Fully integrated with LangChain's agent framework
- Smart fee calculation for scheduled transactions
- Type-safe ABI handling

## Installation

```bash
pip install langchain-ritual-toolkit
```

## Quick Start

1. Set up your environment variables:
```bash
# Required for all modes
OPENAI_API_KEY=your_openai_key

# Required for non-mock mode
RITUAL_PRIVATE_KEY=your_ethereum_private_key
RITUAL_RPC_URL=your_ethereum_rpc_url

# Optional - defaults to searching in current directory, package examples, or env var
RITUAL_CONFIG_PATH=path_to_ritual_config

# Optional - set to "true" for mock mode, defaults to "false"
MOCK=false
```

2. Create an agent with the toolkit:

```python
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_ritual_toolkit import RitualToolkit

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4")

# Create the toolkit
ritual_toolkit = RitualToolkit(
    private_key=os.getenv("RITUAL_PRIVATE_KEY"),
    rpc_url=os.getenv("RITUAL_RPC_URL"),
    ritual_config=None,  # Will auto-discover config
    mock_mode=os.getenv("MOCK", "false").lower() == "true"
)

# Set up the agent with tools
tools = ritual_toolkit.get_tools()
agent = create_react_agent(llm, tools)
```

3. Use the agent to schedule and manage transactions:

```python
# Schedule a transaction
response = agent.invoke({
    "messages": """
        schedule job, id my-job-123,
        gasLimit 100000,
        gasPrice 1000000000,
        frequency 2,
        numBlocks 10
    """
})

# Cancel a transaction
response = agent.invoke({
    "messages": "cancel the scheduled job with id my-job-123"
})
```

## Configuration

The toolkit requires a configuration file (`ritual_config.json`) that specifies the contract address, ABI, and function names. The file will be searched for in the following locations:

1. Current directory
2. Package examples directory
3. Path specified in `RITUAL_CONFIG_PATH` environment variable

Example configuration:
```json
{
    "contract_address": "0xa53C1aEf5a19d82037Fe7E54A3CBAa852f808E21",
    "schedule_fn": "scheduleJob",
    "cancel_fn": "cancelJob",
    "abi": [
        {
            "type": "function",
            "name": "scheduleJob",
            "inputs": [
                {"name": "jobId", "type": "string"},
                {"name": "gasLimit", "type": "uint256"},
                {"name": "gasPrice", "type": "uint256"},
                {"name": "frequency", "type": "uint256"},
                {"name": "numBlocks", "type": "uint256"}
            ],
            "outputs": [],
            "stateMutability": "nonpayable"
        },
        {
            "type": "function",
            "name": "cancelJob",
            "inputs": [
                {"name": "jobId", "type": "string"}
            ],
            "outputs": [],
            "stateMutability": "nonpayable"
        }
    ]
}
```

## Development Mode

The toolkit supports a mock mode for testing and development without requiring a real blockchain connection:

```python
# Create toolkit in mock mode
ritual_toolkit = RitualToolkit(
    ritual_config="ritual_config.json",
    mock_mode=True  # No private_key or rpc_url needed
)
```

In mock mode:
- No real blockchain transactions are made
- Transaction hashes are simulated using UUIDs
- Scheduled jobs are stored in memory
- Perfect for testing and development

## Transaction Fee Calculation

For scheduled transactions, the toolkit automatically calculates the required fee based on:
- Gas limit
- Gas price
- Number of blocks
- Execution frequency

The fee is included as the transaction value when scheduling jobs.

## Error Handling

The toolkit provides robust error handling for common scenarios:
- Missing configuration
- Invalid contract addresses
- Insufficient funds
- Failed transactions
- Network issues

All errors include descriptive messages to help diagnose and fix issues.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

The Clear BSD License

Copyright (c) 2023 Origin Research Ltd
All rights reserved.
