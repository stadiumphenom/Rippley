#!/usr/bin/env python3
"""
Simple test script for the Ripley Viewer chatbot functionality.
"""

import asyncio
import aiohttp
import os
import sys
from pathlib import Path

async def test_chatbot_endpoints():
    """Test the chatbot endpoints"""
    base_url = "http://localhost:8000"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("Testing health endpoint...")
        async with session.get(f"{base_url}/health") as response:
            if response.status == 200:
                result = await response.json()
                print(f"✓ Health endpoint working: {result}")
            else:
                print(f"✗ Health endpoint failed: {response.status}")
                return False
        
        # Test chatbot HTML endpoint
        print("Testing chatbot HTML endpoint...")
        async with session.get(f"{base_url}/chatbot") as response:
            if response.status == 200:
                html_content = await response.text()
                if "Ripley Viewer Chatbot" in html_content:
                    print("✓ Chatbot HTML endpoint working")
                else:
                    print("✗ Chatbot HTML content incorrect")
                    return False
            else:
                print(f"✗ Chatbot HTML endpoint failed: {response.status}")
                return False
        
        # Test chat API endpoint without API key
        print("Testing chat API endpoint without API key...")
        chat_data = {"message": "Hello, test message"}
        async with session.post(f"{base_url}/api/chat", json=chat_data) as response:
            if response.status == 500:
                error_data = await response.json()
                if "OpenAI API key not found" in error_data.get("detail", ""):
                    print("✓ Chat API properly handles missing API key")
                else:
                    print(f"✗ Chat API unexpected error: {error_data}")
                    return False
            else:
                print(f"✗ Chat API should return 500 without API key, got: {response.status}")
                return False
    
    print("\n✅ All tests passed! The chatbot implementation is working correctly.")
    return True

def main():
    """Main test function"""
    print("🧪 Testing Ripley Viewer Chatbot Implementation")
    print("=" * 50)
    
    # Check if required files exist
    current_dir = Path(__file__).parent
    required_files = [
        current_dir / "ripley_viewer" / "app.py",
        current_dir / "ripley_viewer" / "chatbot.html",
        current_dir / "ripley_viewer" / "requirements.txt",
        current_dir / "make_ripley.py"
    ]
    
    print("Checking required files...")
    for file_path in required_files:
        if file_path.exists():
            print(f"✓ {file_path.name} exists")
        else:
            print(f"✗ {file_path.name} missing")
            return False
    
    print("\n📋 Manual Tests to Run:")
    print("1. Start the server: python make_ripley.py")
    print("2. Open browser to: http://localhost:8000/chatbot")
    print("3. Set OPENAI_API_KEY environment variable")
    print("4. Test chat functionality")
    print("5. Check API docs at: http://localhost:8000/docs")
    
    print(f"\n📁 Project structure created:")
    print(f"  📂 ripley_viewer/")
    print(f"    📄 requirements.txt  (FastAPI dependencies)")
    print(f"    📄 app.py            (FastAPI application)")
    print(f"    📄 chatbot.html      (Chat interface)")
    print(f"  📄 make_ripley.py      (Application runner)")
    
    return True

if __name__ == "__main__":
    if main():
        sys.exit(0)
    else:
        sys.exit(1)