#!/usr/bin/env python3
"""
Simple script to start the Qualitative Edge backend server.
"""
import os
import sys
import subprocess

def main():
    # Check if we're in the right directory
    if not os.path.exists('app/main.py'):
        print("Error: Please run this script from the backend directory")
        print("Usage: cd backend && python start_server.py")
        sys.exit(1)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher required")
        sys.exit(1)
    
    print("🚀 Starting Qualitative Edge Backend Server...")
    print("📍 Server will be available at: http://localhost:8000")
    print("📄 API Documentation: http://localhost:8000/docs")
    print("🔧 To stop the server, press Ctrl+C")
    print("-" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ Server stopped successfully")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure you have installed dependencies: pip install -r requirements.txt")
        print("2. Check if port 8000 is already in use")
        print("3. Try running manually: uvicorn app.main:app --reload")
        sys.exit(1)
    except FileNotFoundError:
        print("\n❌ Error: uvicorn not found")
        print("Please install dependencies: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()