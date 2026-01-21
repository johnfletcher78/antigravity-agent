#!/usr/bin/env python3
"""
Test script to verify the Antigravity Marketing Agent is working correctly.
Run this after updating your GOOGLE_API_KEY in the .env file.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from services.llm_service import LLMService

async def test_llm_service():
    """Test the LLM service with streaming"""
    print("=" * 60)
    print("🧪 Testing Antigravity Marketing Agent")
    print("=" * 60)
    
    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ ERROR: GOOGLE_API_KEY not found in .env file")
        return False
    
    if api_key.startswith("AIzaSyC1_5fVmSo3mfqn"):
        print("❌ ERROR: You're still using the OLD leaked API key!")
        print("   Please get a new key from: https://aistudio.google.com/apikey")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...")
    print()
    
    try:
        # Initialize service
        print("🔧 Initializing LLM Service...")
        service = LLMService()
        print("✅ Service initialized successfully")
        print()
        
        # Test streaming
        print("💬 Testing chat streaming...")
        print("   Question: 'What is SEO in one sentence?'")
        print("   Response: ", end="", flush=True)
        
        response_text = ""
        async for chunk in service.get_response_stream("What is SEO in one sentence?"):
            print(chunk, end="", flush=True)
            response_text += chunk
        
        print("\n")
        
        if response_text:
            print("✅ Chat streaming works!")
            print()
            print("=" * 60)
            print("🎉 ALL TESTS PASSED!")
            print("=" * 60)
            print()
            print("Your Antigravity Marketing Agent is ready to use!")
            print("Open http://localhost:3000 in your browser to start chatting.")
            return True
        else:
            print("❌ No response received from the API")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_llm_service())
    sys.exit(0 if success else 1)
