from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI()
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "..", "templates"))


class SimulationInput(BaseModel):
    input: str


class SimulationResponse(BaseModel):
    result: str
    status: str


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/simulate", response_model=SimulationResponse)
async def simulate(simulation_input: SimulationInput):
    """
    Simulate processing - placeholder logic for now.
    
    Args:
        simulation_input: JSON body with 'input' field
        
    Returns:
        SimulationResponse with result and status
    """
    # Placeholder logic - simple response based on input
    result = f"Simulated processing of: {simulation_input.input}"
    return SimulationResponse(result=result, status="success")

# For local development (not used by Vercel but handy for testing)
if __name__ == "__main__":
    uvicorn.run("ripley_viewer.app:app", host="0.0.0.0", port=8000, reload=True)