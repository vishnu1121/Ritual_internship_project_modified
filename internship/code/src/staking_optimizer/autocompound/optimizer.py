"""Gas optimization for auto-compound operations.

This module provides functionality to optimize gas usage for auto-compound
operations by tracking historical gas prices and finding optimal execution windows.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

from staking_optimizer.blockchain.mock_state import MockBlockchainState

logger = logging.getLogger(__name__)


@dataclass
class GasWindow:
    """Represents a window of time with favorable gas prices.
    
    Attributes:
        start_time: Start of the window
        end_time: End of the window
        avg_gas_price: Average gas price during window
        min_gas_price: Minimum gas price during window
        max_gas_price: Maximum gas price during window
    """
    
    start_time: datetime
    end_time: datetime
    avg_gas_price: Decimal
    min_gas_price: Decimal
    max_gas_price: Decimal


@dataclass
class GasOptimizer:
    """Optimizes gas usage by tracking historical prices and finding optimal windows.
    
    This class tracks gas prices over time and identifies windows with historically
    low gas prices that would be favorable for auto-compound operations.
    
    Attributes:
        blockchain: Mock blockchain state
        window_size: Size of analysis window in minutes
        min_window_size: Minimum size of a favorable window in minutes
        price_history: Historical gas prices with timestamps
        last_check: Last time gas prices were checked
    """
    
    blockchain: MockBlockchainState
    window_size: int = 60  # Look at last hour by default
    min_window_size: int = 5  # Minimum 5 minute window
    price_history: List[Tuple[datetime, Decimal]] = field(default_factory=list)
    last_check: Optional[datetime] = None
    
    def check_gas_price(self) -> bool:
        """Check if current gas price is favorable for auto-compound.
        
        Returns:
            True if current gas price is within optimal window
        """
        # Update price history
        now = self.blockchain.last_block_time
        current_price = self.blockchain.gas_price
        self.price_history.append((now, current_price))
        self.last_check = now
        
        # Remove old prices outside window
        cutoff = now - timedelta(minutes=self.window_size)
        self.price_history = [
            (t, p) for t, p in self.price_history if t >= cutoff
        ]
        
        # Special case: single price point
        if len(self.price_history) == 1:
            return True
            
        # Check if current price is below average
        avg_price = sum(p for _, p in self.price_history) / len(self.price_history)
        if current_price > avg_price:
            return False
            
        # Get current window
        window = self._find_optimal_window()
        if not window:
            # If no window but price is below average, consider it favorable
            return True
            
        # Check if current time is within window
        return window.start_time <= now <= window.end_time
    
    def _find_optimal_window(self) -> Optional[GasWindow]:
        """Find the optimal window for auto-compound based on gas prices.
        
        Returns:
            GasWindow if favorable window found, None otherwise
        """
        if len(self.price_history) < 2:
            return None
            
        # Calculate average price
        prices = [p for _, p in self.price_history]
        avg_price = sum(prices) / len(prices)
        
        # Find contiguous periods below average
        windows = []
        start_idx = None
        
        for i, (time, price) in enumerate(self.price_history):
            if price <= avg_price:
                if start_idx is None:
                    start_idx = i
            elif start_idx is not None:
                # End of window
                window_start = self.price_history[start_idx][0]
                window_end = self.price_history[i-1][0]
                
                if (window_end - window_start).total_seconds() / 60 >= self.min_window_size:
                    window_prices = [p for t, p in self.price_history[start_idx:i]]
                    windows.append(GasWindow(
                        start_time=window_start,
                        end_time=window_end,
                        avg_gas_price=sum(window_prices) / len(window_prices),
                        min_gas_price=min(window_prices),
                        max_gas_price=max(window_prices),
                    ))
                start_idx = None
        
        # Check final window
        if start_idx is not None:
            window_start = self.price_history[start_idx][0]
            window_end = self.price_history[-1][0]
            
            if (window_end - window_start).total_seconds() / 60 >= self.min_window_size:
                window_prices = [p for t, p in self.price_history[start_idx:]]
                windows.append(GasWindow(
                    start_time=window_start,
                    end_time=window_end,
                    avg_gas_price=sum(window_prices) / len(window_prices),
                    min_gas_price=min(window_prices),
                    max_gas_price=max(window_prices),
                ))
        
        # Return window with lowest average gas price
        return min(windows, key=lambda w: w.avg_gas_price) if windows else None
    
    def get_gas_stats(self) -> Dict[str, Decimal]:
        """Get statistics about gas prices.
        
        Returns:
            Dictionary with gas price statistics
        """
        if not self.price_history:
            return {
                "average_gas_price": Decimal("0"),
                "min_gas_price": Decimal("0"),
                "max_gas_price": Decimal("0"),
                "current_gas_price": self.blockchain.gas_price,
            }
            
        prices = [p for _, p in self.price_history]
        return {
            "average_gas_price": sum(prices) / len(prices),
            "min_gas_price": min(prices),
            "max_gas_price": max(prices),
            "current_gas_price": self.blockchain.gas_price,
        }
