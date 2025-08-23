"""
Agent Core Module for Rippley
Provides core agent functionality and factory patterns.
"""

__version__ = "1.0.0"
__author__ = "Rippley Team"

from .agent_factory import AgentFactory
from .task_runner import TaskRunner
from .memory_link import MemoryLink

__all__ = ["AgentFactory", "TaskRunner", "MemoryLink"]