"""
Run script to start both backend and frontend servers.
Requires Python 3.8+
"""

import subprocess
import sys
import time
import os

def main():
    print("=" * 60)
    print("🎨 StoryWeaver AI - Multi-Agent Storytelling Engine 🎨")
    print("=" * 60)
    print()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(project_root, 'backend')
    frontend_dir = os.path.join(project_root, 'frontend')
    
    print("📦 Checking dependencies...")
    try:
        import flask
        import flask_cors
        import torch
        import transformers
        import sentence_transformers
        import sklearn
        print("✓ All dependencies installed!")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("\nInstalling dependencies...")
        subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
            cwd=project_root,
            check=True
        )
        print("✓ Dependencies installed!")
    
    print()
    print("🚀 Starting StoryWeaver AI Services...")
    print()
    
    # Start backend
    print("Starting Backend API (Port 5000)...")
    backend_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print("✓ Backend started (PID: {})".format(backend_process.pid))
    
    time.sleep(2)  # Wait for backend to start
    
    # Start frontend
    print("Starting Frontend Server (Port 3000)...")
    frontend_process = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print("✓ Frontend started (PID: {})".format(frontend_process.pid))
    
    print()
    print("=" * 60)
    print("🎉 All services started successfully!")
    print("=" * 60)
    print()
    print("📍 URLs:")
    print("  • Frontend UI:  http://localhost:3000")
    print("  • Backend API:  http://localhost:5000")
    print("  • API Docs:     http://localhost:5000/docs (if available)")
    print()
    print("📚 Documentation: See README.md for more information")
    print()
    print("Press Ctrl+C to stop all services...")
    print()
    
    try:
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.wait()
        frontend_process.wait()
        print("✓ Services stopped")
        sys.exit(0)

if __name__ == '__main__':
    main()
