"""
Bootstrap script that injects mock dependencies and starts both servers.
This allows the website to run immediately without downloading large ML models.
"""
import sys
import types
import numpy as np
import os

# Create fake sentence_transformers if not installed
if 'sentence_transformers' not in sys.modules:
    fake_st = types.SimpleNamespace()

    class FakeModel:
        def __init__(self, model_name=None):
            self.model_name = model_name

        def encode(self, texts, convert_to_numpy=True):
            if isinstance(texts, (list, tuple)):
                texts = texts[0]
            h = abs(hash(str(texts))) % (10**8)
            rng = np.random.RandomState(h)
            return rng.rand(384)

    fake_st.SentenceTransformer = FakeModel
    sys.modules['sentence_transformers'] = fake_st

# Now import and run apps
if __name__ == '__main__':
    import subprocess
    import time
    
    print("=" * 60)
    print("🚀 StoryWeaver AI - Startup")
    print("=" * 60)
    print()
    print("Starting Backend API (port 5000) and Frontend (port 3000)...")
    print()
    
    # Start backend
    print("[1/2] Starting Backend API...")
    backend_proc = subprocess.Popen(
        [sys.executable, '-m', 'backend.app'],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    time.sleep(2)
    
    # Start frontend
    print("[2/2] Starting Frontend UI...")
    frontend_proc = subprocess.Popen(
        [sys.executable, '-m', 'frontend.app'],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )
    
    print()
    print("=" * 60)
    print("✓ Services started!")
    print()
    print("Frontend:  http://localhost:3000")
    print("Backend:   http://localhost:5000")
    print()
    print("Press Ctrl+C to stop all services.")
    print("=" * 60)
    
    try:
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("Done.")
