"""
Task Runner Module
Manages and executes tasks for Neo-Glyph agents.
"""

import asyncio
from typing import Dict, Any, List, Optional, Callable
from enum import Enum
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task:
    """Represents a single task to be executed."""
    
    def __init__(self, task_id: str, task_type: str, payload: Dict[str, Any], 
                 callback: Optional[Callable] = None):
        self.task_id = task_id
        self.task_type = task_type
        self.payload = payload
        self.callback = callback
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Any] = None
        self.error: Optional[str] = None


class TaskRunner:
    """Manages task execution for agents."""
    
    def __init__(self, max_concurrent_tasks: int = 5):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.task_queue: List[Task] = []
        self.running_tasks: Dict[str, Task] = {}
        self.completed_tasks: Dict[str, Task] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self._running = False
    
    def register_task_handler(self, task_type: str, handler: Callable) -> None:
        """Register a handler for a specific task type."""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    def add_task(self, task_id: str, task_type: str, payload: Dict[str, Any], 
                 callback: Optional[Callable] = None) -> Task:
        """Add a new task to the execution queue."""
        task = Task(task_id, task_type, payload, callback)
        self.task_queue.append(task)
        logger.info(f"Added task: {task_id} of type: {task_type}")
        return task
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task."""
        # Check running tasks
        if task_id in self.running_tasks:
            return self.running_tasks[task_id].status
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].status
        
        # Check queued tasks
        for task in self.task_queue:
            if task.task_id == task_id:
                return task.status
        
        return None
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """Get the result of a completed task."""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id].result
        return None
    
    async def execute_task(self, task: Task) -> None:
        """Execute a single task."""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            self.running_tasks[task.task_id] = task
            
            logger.info(f"Executing task: {task.task_id}")
            
            if task.task_type in self.task_handlers:
                handler = self.task_handlers[task.task_type]
                task.result = await self._call_handler(handler, task.payload)
            else:
                # TODO: Implement default task execution
                logger.warning(f"No handler found for task type: {task.task_type}")
                task.result = {"message": f"No handler for {task.task_type}", "payload": task.payload}
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            
            # Execute callback if provided
            if task.callback:
                await self._call_handler(task.callback, task.result)
            
            logger.info(f"Task completed: {task.task_id}")
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            logger.error(f"Task failed: {task.task_id}, Error: {e}")
        
        finally:
            # Move from running to completed
            if task.task_id in self.running_tasks:
                del self.running_tasks[task.task_id]
            self.completed_tasks[task.task_id] = task
    
    async def _call_handler(self, handler: Callable, *args, **kwargs) -> Any:
        """Call a handler function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(handler):
            return await handler(*args, **kwargs)
        else:
            return handler(*args, **kwargs)
    
    async def run(self) -> None:
        """Start the task runner."""
        self._running = True
        logger.info("Task runner started")
        
        while self._running:
            # Process queued tasks if we have capacity
            while (len(self.running_tasks) < self.max_concurrent_tasks and 
                   self.task_queue):
                task = self.task_queue.pop(0)
                asyncio.create_task(self.execute_task(task))
            
            # Small delay to prevent busy waiting
            await asyncio.sleep(0.1)
    
    def stop(self) -> None:
        """Stop the task runner."""
        self._running = False
        logger.info("Task runner stopped")
    
    def get_queue_status(self) -> Dict[str, int]:
        """Get current queue status."""
        return {
            "queued": len(self.task_queue),
            "running": len(self.running_tasks),
            "completed": len(self.completed_tasks)
        }


# Global task runner instance
task_runner = TaskRunner()