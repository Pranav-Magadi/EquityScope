#!/usr/bin/env python3
"""
Claude API Key Validation Test
Run this script to test if your Claude API key is valid and has credits.
"""

import os
import asyncio
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_claude_api():
    """Test Claude API key validity and credits."""
    
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("❌ No ANTHROPIC_API_KEY found in environment")
        return False
    
    print(f"🔑 Testing API Key: {api_key[:20]}...{api_key[-10:]}")
    
    try:
        # Initialize Claude client
        client = Anthropic(api_key=api_key)
        
        # Test with a simple completion
        print("🧪 Testing API call...")
        
        # For anthropic library version 0.66.0+
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Current available model
            max_tokens=50,
            temperature=0.1,
            system="You are a helpful assistant.",
            messages=[{"role": "user", "content": "Say 'API test successful' if you can read this."}]
        )
        
        if response.content and len(response.content) > 0:
            result = response.content[0].text
            print(f"✅ API Response: {result}")
            print("✅ Claude API key is VALID and has credits!")
            return True
        else:
            print("❌ Empty response from Claude API")
            return False
            
    except Exception as e:
        error_str = str(e).lower()
        
        if "authentication" in error_str or "invalid" in error_str:
            print(f"❌ AUTHENTICATION ERROR: Invalid API key")
            print("   → Get a new API key from: https://console.anthropic.com/")
        elif "credit" in error_str or "quota" in error_str or "limit" in error_str:
            print(f"❌ CREDITS EXHAUSTED: {e}")
            print("   → Add credits to your Anthropic account")
        elif "rate" in error_str:
            print(f"❌ RATE LIMITED: {e}")
            print("   → Wait a few minutes and try again")
        else:
            print(f"❌ UNKNOWN ERROR: {e}")
        
        return False

if __name__ == "__main__":
    print("🔍 Claude API Key Validation Test")
    print("=" * 50)
    
    success = asyncio.run(test_claude_api())
    
    if success:
        print("\n🎉 Your Claude API key is working correctly!")
        print("   AI Mode should work now.")
    else:
        print("\n🚨 Claude API key issue detected!")
        print("   Please fix the API key to enable AI Mode.")
        print("\n📋 Next Steps:")
        print("   1. Get a valid Claude API key from: https://console.anthropic.com/")
        print("   2. Update ANTHROPIC_API_KEY in backend/.env file")
        print("   3. Restart the backend server")
