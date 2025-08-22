#!/usr/bin/env python3
"""
make_ripley.py - Entry point for running the Ripley Viewer FastAPI application

This script runs the FastAPI chatbot application with proper configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Main entry point for the Ripley Viewer application"""
    
    # Add the current directory to Python path to import the app
    current_dir = Path(__file__).parent
    ripley_viewer_dir = current_dir / "ripley_viewer"
    
    if not ripley_viewer_dir.exists():
        print(f"Error: ripley_viewer directory not found at {ripley_viewer_dir}")
        sys.exit(1)
    
    # Add ripley_viewer directory to Python path
    sys.path.insert(0, str(ripley_viewer_dir))
    
    try:
        # Import the FastAPI app
        from app import app
        
        # Check if OpenAI API key is set
        if not os.getenv("OPENAI_API_KEY"):
            print("Warning: OPENAI_API_KEY environment variable is not set.")
            print("The chatbot will not work without a valid OpenAI API key.")
            print("Set it with: export OPENAI_API_KEY='your-api-key-here'")
            print()
        
        print("Starting Ripley Viewer Chatbot...")
        print("Access the chatbot at: http://localhost:8000/chatbot")
        print("API documentation at: http://localhost:8000/docs")
        print("Press Ctrl+C to stop the server")
        print()
        
        # Run the FastAPI application
        uvicorn.run(
            app,
            host="0.0.0.0", 
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except ImportError as e:
        print(f"Error importing the FastAPI app: {e}")
        print("Make sure you have installed the required dependencies.")
        print("Run: pip install -r ripley_viewer/requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down Ripley Viewer Chatbot...")
    except Exception as e:
        print(f"Error starting the application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()