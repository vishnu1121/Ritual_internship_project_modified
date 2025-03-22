"""Mock configuration for Ritual toolkit.

This module provides the configuration for using the Ritual toolkit in mock mode
with our StakingOptimizer mock implementations.

Example:
    ```python
    from langchain_ritual_toolkit import RitualToolkit
    from langchain_ritual_toolkit.mock import MockConnection, MockStateAdapter
    from staking_optimizer.blockchain.mock_state import MockBlockchainState
    from staking_optimizer.toolkit.mock_config import create_mock_connection
    
    # Create toolkit with mock mode
    connection = create_mock_connection()
    toolkit = RitualToolkit(mock_mode=True, mock_connection=connection)
    ```
"""

from staking_optimizer.blockchain.mock_state import MockBlockchainState
from staking_optimizer.blockchain.mock_contract import MockStakingContract
from langchain_ritual_toolkit.mock import MockConnection, MockStateAdapter


def create_mock_connection(
    state: MockBlockchainState = None,
    contract: MockStakingContract = None,
    auto_mine: bool = True,
    block_time: int = 12
) -> MockConnection:
    """Create a mock connection for the Ritual toolkit.
    
    Args:
        state: Optional MockBlockchainState instance
        contract: Optional MockStakingContract instance
        auto_mine: Whether to automatically mine blocks
        block_time: Time between blocks in seconds
        
    Returns:
        Configured MockConnection instance
    """
    if state is None:
        state = MockBlockchainState()
        
    if contract is None and state is not None:
        contract = MockStakingContract(state)
        
    adapter = MockStateAdapter(state, contract)
    return MockConnection(
        provider=adapter,
        auto_mine=auto_mine,
        block_time=block_time
    )
