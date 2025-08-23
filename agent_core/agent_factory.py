"""
Agent Factory Module
Creates and manages different types of Neo-Glyph agents.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AgentFactory:
    """Factory class for creating and managing Neo-Glyph agents."""
    
    def __init__(self):
        self.agent_registry: Dict[str, Any] = {}
        self.active_agents: Dict[str, Any] = {}
    
    def create_agent(self, agent_type: str, config: Optional[Dict[str, Any]] = None) -> Any:
        """
        Create a new agent instance.
        
        Args:
            agent_type: Type of agent to create
            config: Configuration parameters for the agent
            
        Returns:
            Created agent instance
            
        Raises:
            ValueError: If agent_type is not supported
        """
        if config is None:
            config = {}
            
        if agent_type not in self.agent_registry:
            logger.warning(f"Agent type '{agent_type}' not registered. Creating basic agent.")
            return self._create_basic_agent(config)
        
        agent_class = self.agent_registry[agent_type]
        agent = agent_class(**config)
        
        agent_id = config.get('id', f"{agent_type}_{len(self.active_agents)}")
        self.active_agents[agent_id] = agent
        
        logger.info(f"Created agent: {agent_id} of type: {agent_type}")
        return agent
    
    def register_agent_type(self, agent_type: str, agent_class: Any) -> None:
        """Register a new agent type with the factory."""
        self.agent_registry[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get an active agent by ID."""
        return self.active_agents.get(agent_id)
    
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from the active agents."""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
            logger.info(f"Removed agent: {agent_id}")
            return True
        return False
    
    def list_active_agents(self) -> Dict[str, Any]:
        """List all currently active agents."""
        return self.active_agents.copy()
    
    def _create_basic_agent(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic agent when no specific type is registered."""
        # TODO: Implement Neo-Glyph specific agent functionality
        # TODO: Integrate with configuration from config/glyph_spec.json
        # TODO: Add support for workflow orchestration and multi-modal processing
        # INCOMPLETE: This is a placeholder implementation
        return {
            "id": config.get('id', 'basic_agent'),
            "type": "basic",
            "config": config,
            "status": "initialized",
            "capabilities": ["basic_response"],  # TODO: Add Neo-Glyph capabilities
            "memory_link": None,  # TODO: Initialize MemoryLink integration
            "task_runner": None   # TODO: Initialize TaskRunner integration
        }


# Global factory instance
agent_factory = AgentFactory()