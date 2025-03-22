"""StakeMate character implementation."""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class StakeMateCharacter:
    """StakeMate character for optimizing staking positions.

    This character helps users optimize their staking positions by:
    - Monitoring APR changes
    - Suggesting optimal stake amounts
    - Automating staking transactions
    - Managing rewards

    Design principles:
    - Safety first: Always validate transactions
    - Clear communication: Explain all suggestions
    - Proactive monitoring: Alert users to opportunities
    - Conservative estimates: Better safe than sorry

    Security rules:
    - Never share private keys
    - Always verify transaction parameters
    - Reward calculations must be accurate and conservative
    """

    # Mapping of topics to informational responses
    TOPIC_RESPONSES = {
        "staking_overview": """
            Staking is a way to earn rewards by locking up your tokens. Key points:
            - Higher stakes generally earn more rewards
            - APR can change based on market conditions
            - Consider gas costs when staking/unstaking
            - Monitor APR changes to optimize returns
        """,
        "help": """
            I can help you with:
            - Staking and unstaking tokens
            - Viewing your staking position
            - Monitoring APR changes
            - Compounding rewards
            - Optimizing your returns
        """,
        "risks": """
            Important risks to consider:
            - APR can decrease over time
            - Gas costs affect profitability
            - Smart contract risks exist
            - Consider your liquidity needs
        """,
        "rewards": """
            Staking rewards information:
            - Rewards are based on stake size and APR
            - Higher APR means higher rewards
            - Compounding can increase returns
            - Monitor gas costs vs rewards
        """,
        "requirements": """
            Requirements for staking:
            - Minimum stake amount: 0.1 ETH
            - Maximum stake amount: 100 ETH
            - Need enough ETH for gas
            - Account must exist on chain
        """,
        "apr_strategy": """
            Here's my advice about APR:
            - Evaluate if your current rate aligns with your investment goals
            - Consider the broader market conditions and available alternatives
            - Factor in gas costs when making any changes
            - Keep monitoring rates to make informed decisions
            - Remember that APR fluctuations are normal in DeFi
        """
    }

    def format_response(self, topic: str) -> str:
        """Format an informational response with StakeMate's personality.

        Args:
            topic: Topic to get information about

        Returns:
            Formatted response string

        Raises:
            ValueError: If topic is not supported
        """
        if topic not in self.TOPIC_RESPONSES:
            raise ValueError(f"Unknown topic: {topic}")

        response = self.TOPIC_RESPONSES[topic].strip()
        return f"Here's what you should know about {topic}:\n{response}"

    def format_apr_info(self, current_apr: float, previous_apr: float = None) -> str:
        """Format current APR information.

        Args:
            current_apr: Current APR as decimal (e.g. 0.05 for 5%)
            previous_apr: Previous APR as decimal, if available

        Returns:
            Formatted APR information string
        """
        if previous_apr is None or abs(current_apr - previous_apr) < 0.0001:
            return f"The current APR is {current_apr*100:.1f}%."
        elif current_apr < previous_apr:
            decrease = (previous_apr - current_apr) * 100
            return f"The APR has decreased to {current_apr*100:.1f}% (was {previous_apr*100:.1f}%)."
        else:
            increase = (current_apr - previous_apr) * 100
            return f"The APR has increased to {current_apr*100:.1f}% (was {previous_apr*100:.1f}%)."

    def format_apr_recommendation(self, current_apr: float, previous_apr: float) -> str:
        """Format an APR change recommendation.

        Args:
            current_apr: Current APR as decimal (e.g. 0.05 for 5%)
            previous_apr: Previous APR as decimal

        Returns:
            Formatted recommendation string
        """
        if current_apr < previous_apr:
            decrease = (previous_apr - current_apr) * 100
            if decrease > 2.0:  # More than 2% decrease
                return (
                    f"The APR has dropped significantly by {decrease:.1f}% (from {previous_apr*100:.1f}% to {current_apr*100:.1f}%). "
                    "Consider reviewing your position and potentially unstaking "
                    "if better opportunities are available."
                )
            else:
                return (
                    f"The APR has decreased slightly by {decrease:.1f}% (from {previous_apr*100:.1f}% to {current_apr*100:.1f}%). "
                    "Continue monitoring the rate, but no immediate action needed."
                )
        elif current_apr > previous_apr:
            increase = (current_apr - previous_apr) * 100
            return (
                f"Good news! The APR has increased by {increase:.1f}% (from {previous_apr*100:.1f}% to {current_apr*100:.1f}%). "
                "This is a good time to consider increasing your stake."
            )
        else:
            return f"The APR remains stable at {current_apr*100:.1f}%. Continue with your current strategy."
