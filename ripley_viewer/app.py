import os
import json
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import aiohttp
import asyncio

app = FastAPI(title="Ripley Viewer Chatbot", version="1.0.0")

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.get("/chatbot", response_class=HTMLResponse)
async def serve_chatbot():
    """Serve the chatbot HTML page"""
    try:
        # Read the HTML file from the same directory
        current_dir = os.path.dirname(__file__)
        html_path = os.path.join(current_dir, "chatbot.html")
        
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chatbot HTML file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving chatbot page: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_openai(chat_message: ChatMessage):
    """Handle chat messages and interact with OpenAI API"""
    
    # Get OpenAI API key from environment
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500, 
            detail="OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
        )
    
    # Prepare the request to OpenAI API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": chat_message.message
            }
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 401:
                    raise HTTPException(
                        status_code=500,
                        detail="Invalid OpenAI API key. Please check your OPENAI_API_KEY environment variable."
                    )
                elif response.status == 429:
                    raise HTTPException(
                        status_code=429,
                        detail="OpenAI API rate limit exceeded. Please try again later."
                    )
                elif response.status != 200:
                    error_text = await response.text()
                    raise HTTPException(
                        status_code=500,
                        detail=f"OpenAI API error (status {response.status}): {error_text}"
                    )
                
                result = await response.json()
                
                # Extract the response from OpenAI
                if "choices" in result and len(result["choices"]) > 0:
                    ai_response = result["choices"][0]["message"]["content"]
                    return ChatResponse(response=ai_response)
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Unexpected response format from OpenAI API"
                    )
                    
    except aiohttp.ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Network error communicating with OpenAI: {str(e)}"
        )
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request to OpenAI API timed out. Please try again."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ripley_viewer_chatbot"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)