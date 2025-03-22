"""Auto-compound functionality for optimizing staking rewards.

This package provides components for automatically compounding staking rewards
based on configurable strategies and gas optimization.
"""

from .monitor import RewardMonitor as AutoCompoundMonitor
from .optimizer import GasOptimizer
from .strategy import (
    AutoCompoundStrategy,
    ThresholdStrategy,
    TimeBasedStrategy,
    GasOptimizedStrategy,
)

__all__ = [
    "AutoCompoundMonitor",
    "GasOptimizer",
    "AutoCompoundStrategy",
    "ThresholdStrategy",
    "TimeBasedStrategy",
    "GasOptimizedStrategy",
]
