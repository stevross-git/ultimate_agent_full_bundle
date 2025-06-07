"""Core package initialization.

This module exposes the most commonly used classes from the core package so
they can be imported directly from :mod:`ultimate_agent.core`.
"""

from .agent import UltimateAgent
from .container import Container
from .events import event_bus

__all__ = ["UltimateAgent", "Container", "event_bus"]
