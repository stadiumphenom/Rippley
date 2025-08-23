from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import os
import logging

# Import agent core modules for Neo-Glyph integration
try:
    from agent_core import AgentFactory, TaskRunner, MemoryLink
    from agent_core.agent_factory import agent_factory
    from agent_core.task_runner import task_runner
    from agent_core.memory_link import memory_manager
    AGENT_CORE_AVAILABLE = True
except ImportError:
    AGENT_CORE_AVAILABLE = False
    logging.warning("Agent core modules not available")

app = FastAPI(title="Rippley - Neo-Glyph Agent System", version="1.0.0")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Main application interface."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    """Get system status and agent core availability."""
    return {
        "status": "online",
        "system": "Rippley Neo-Glyph Agent System",
        "agent_core_available": AGENT_CORE_AVAILABLE,
        "version": "1.0.0"
    }

@app.get("/api/agents")
async def list_agents():
    """List all active agents."""
    if not AGENT_CORE_AVAILABLE:
        return {"error": "Agent core not available"}
    
    # TODO: Implement proper Neo-Glyph agent listing
    # INCOMPLETE: Needs integration with actual agent instances
    active_agents = agent_factory.list_active_agents()
    return {
        "agents": active_agents,
        "count": len(active_agents)
    }

@app.post("/api/agents")
async def create_agent(agent_data: dict):
    """Create a new Neo-Glyph agent."""
    if not AGENT_CORE_AVAILABLE:
        return {"error": "Agent core not available"}
    
    # TODO: Implement Neo-Glyph agent creation with proper validation
    # INCOMPLETE: Needs glyph_spec.json integration
    agent_type = agent_data.get("type", "neo_glyph")
    config = agent_data.get("config", {})
    
    try:
        agent = agent_factory.create_agent(agent_type, config)
        return {"status": "created", "agent": agent}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/tasks")
async def get_task_status():
    """Get task runner status."""
    if not AGENT_CORE_AVAILABLE:
        return {"error": "Agent core not available"}
    
    # TODO: Integrate with actual task queue monitoring
    # INCOMPLETE: Needs real task status from TaskRunner
    return task_runner.get_queue_status()

@app.post("/api/tasks")
async def create_task(task_data: dict):
    """Create a new task for execution."""
    if not AGENT_CORE_AVAILABLE:
        return {"error": "Agent core not available"}
    
    # TODO: Implement proper task validation and Neo-Glyph workflow integration
    # INCOMPLETE: Needs nl_rules.json integration for natural language processing
    task_id = task_data.get("id", f"task_{len(task_runner.task_queue)}")
    task_type = task_data.get("type", "basic")
    payload = task_data.get("payload", {})
    
    try:
        task = task_runner.add_task(task_id, task_type, payload)
        return {
            "status": "queued", 
            "task_id": task_id,
            "task_type": task_type
        }
    except Exception as e:
        return {"error": str(e)}

# For local development (not used by Vercel but handy for testing)
if __name__ == "__main__":
    uvicorn.run("rippley_viewer.app:app", host="0.0.0.0", port=8000, reload=True)