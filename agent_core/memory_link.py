"""
Memory Link Module
Manages agent memory and context storage for Neo-Glyph agents.
"""

from typing import Dict, Any, List, Optional, Union
import json
import logging
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)


class MemoryEntry:
    """Represents a single memory entry."""
    
    def __init__(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None,
                 ttl: Optional[int] = None):
        self.key = key
        self.value = value
        self.metadata = metadata or {}
        self.created_at = datetime.now()
        self.accessed_at = self.created_at
        self.access_count = 0
        self.ttl = ttl  # Time to live in seconds
    
    def is_expired(self) -> bool:
        """Check if the memory entry has expired."""
        if self.ttl is None:
            return False
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def access(self) -> Any:
        """Access the memory entry and update access statistics."""
        self.accessed_at = datetime.now()
        self.access_count += 1
        return self.value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory entry to dictionary."""
        return {
            "key": self.key,
            "value": self.value,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
            "access_count": self.access_count,
            "ttl": self.ttl,
            "expired": self.is_expired()
        }


class MemoryLink:
    """Manages agent memory and context storage."""
    
    def __init__(self, agent_id: str, max_entries: int = 10000):
        self.agent_id = agent_id
        self.max_entries = max_entries
        self.memories: Dict[str, MemoryEntry] = {}
        self.categories: Dict[str, List[str]] = defaultdict(list)
        self._cleanup_threshold = 0.8  # Cleanup when 80% full
    
    def store(self, key: str, value: Any, category: Optional[str] = None,
              metadata: Optional[Dict[str, Any]] = None, ttl: Optional[int] = None) -> None:
        """Store a memory entry."""
        
        # Cleanup if necessary
        if len(self.memories) >= self.max_entries * self._cleanup_threshold:
            self._cleanup_expired()
        
        # Create memory entry
        entry = MemoryEntry(key, value, metadata, ttl)
        self.memories[key] = entry
        
        # Add to category if specified
        if category:
            if key not in self.categories[category]:
                self.categories[category].append(key)
        
        logger.debug(f"Stored memory: {key} for agent: {self.agent_id}")
    
    def retrieve(self, key: str) -> Optional[Any]:
        """Retrieve a memory entry by key."""
        if key not in self.memories:
            return None
        
        entry = self.memories[key]
        if entry.is_expired():
            self._remove_memory(key)
            return None
        
        return entry.access()
    
    def retrieve_by_category(self, category: str) -> Dict[str, Any]:
        """Retrieve all memories in a specific category."""
        result = {}
        if category not in self.categories:
            return result
        
        for key in self.categories[category].copy():
            value = self.retrieve(key)
            if value is not None:
                result[key] = value
        
        return result
    
    def search(self, query: str, category: Optional[str] = None) -> Dict[str, Any]:
        """Search memories by key or value content."""
        results = {}
        search_keys = self.categories.get(category, self.memories.keys()) if category else self.memories.keys()
        
        for key in search_keys:
            if key not in self.memories:
                continue
                
            entry = self.memories[key]
            if entry.is_expired():
                self._remove_memory(key)
                continue
            
            # Search in key
            if query.lower() in key.lower():
                results[key] = entry.access()
                continue
            
            # Search in value (if string or contains searchable content)
            try:
                value_str = str(entry.value).lower()
                if query.lower() in value_str:
                    results[key] = entry.access()
            except Exception:
                pass  # Skip non-searchable values
        
        return results
    
    def update(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing memory entry."""
        if key not in self.memories:
            return False
        
        entry = self.memories[key]
        if entry.is_expired():
            self._remove_memory(key)
            return False
        
        entry.value = value
        if metadata:
            entry.metadata.update(metadata)
        entry.accessed_at = datetime.now()
        
        logger.debug(f"Updated memory: {key} for agent: {self.agent_id}")
        return True
    
    def delete(self, key: str) -> bool:
        """Delete a memory entry."""
        if key in self.memories:
            self._remove_memory(key)
            return True
        return False
    
    def clear_category(self, category: str) -> int:
        """Clear all memories in a specific category."""
        if category not in self.categories:
            return 0
        
        cleared_count = 0
        for key in self.categories[category].copy():
            if self.delete(key):
                cleared_count += 1
        
        del self.categories[category]
        return cleared_count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        total_memories = len(self.memories)
        expired_count = sum(1 for entry in self.memories.values() if entry.is_expired())
        
        category_stats = {cat: len(keys) for cat, keys in self.categories.items()}
        
        return {
            "agent_id": self.agent_id,
            "total_memories": total_memories,
            "expired_memories": expired_count,
            "active_memories": total_memories - expired_count,
            "max_entries": self.max_entries,
            "usage_percentage": (total_memories / self.max_entries) * 100,
            "categories": category_stats
        }
    
    def export_memories(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Export memories to a list of dictionaries."""
        memories_to_export = []
        search_keys = self.categories.get(category, self.memories.keys()) if category else self.memories.keys()
        
        for key in search_keys:
            if key in self.memories:
                entry = self.memories[key]
                if not entry.is_expired():
                    memories_to_export.append(entry.to_dict())
        
        return memories_to_export
    
    def import_memories(self, memories_data: List[Dict[str, Any]]) -> int:
        """Import memories from a list of dictionaries."""
        imported_count = 0
        
        for memory_data in memories_data:
            try:
                key = memory_data["key"]
                value = memory_data["value"]
                metadata = memory_data.get("metadata", {})
                ttl = memory_data.get("ttl")
                
                self.store(key, value, metadata=metadata, ttl=ttl)
                imported_count += 1
                
            except Exception as e:
                logger.error(f"Failed to import memory: {e}")
        
        return imported_count
    
    def _remove_memory(self, key: str) -> None:
        """Remove a memory entry and clean up category references."""
        if key in self.memories:
            del self.memories[key]
        
        # Remove from all categories
        for category, keys in self.categories.items():
            if key in keys:
                keys.remove(key)
    
    def _cleanup_expired(self) -> int:
        """Clean up expired memory entries."""
        expired_keys = [key for key, entry in self.memories.items() if entry.is_expired()]
        
        for key in expired_keys:
            self._remove_memory(key)
        
        logger.info(f"Cleaned up {len(expired_keys)} expired memories for agent: {self.agent_id}")
        return len(expired_keys)


class MemoryManager:
    """Global memory manager for all agents."""
    
    def __init__(self):
        self.agent_memories: Dict[str, MemoryLink] = {}
    
    def get_memory_link(self, agent_id: str, max_entries: int = 10000) -> MemoryLink:
        """Get or create a memory link for an agent."""
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = MemoryLink(agent_id, max_entries)
        
        return self.agent_memories[agent_id]
    
    def cleanup_agent_memory(self, agent_id: str) -> bool:
        """Remove all memory for a specific agent."""
        if agent_id in self.agent_memories:
            del self.agent_memories[agent_id]
            logger.info(f"Cleaned up memory for agent: {agent_id}")
            return True
        return False
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global memory statistics across all agents."""
        total_agents = len(self.agent_memories)
        total_memories = sum(len(memory.memories) for memory in self.agent_memories.values())
        
        agent_stats = {}
        for agent_id, memory in self.agent_memories.items():
            agent_stats[agent_id] = memory.get_stats()
        
        return {
            "total_agents": total_agents,
            "total_memories": total_memories,
            "agent_stats": agent_stats
        }


# Global memory manager instance
memory_manager = MemoryManager()