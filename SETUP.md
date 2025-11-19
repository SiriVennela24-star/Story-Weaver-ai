# StoryWeaver AI - Setup Guide

## Quick Start (Windows)

### Option 1: Batch Script (Simplest)
```bash
start.bat
```
This will automatically start both backend and frontend in separate command windows.

### Option 2: PowerShell Script
```powershell
.\start.ps1
```

### Option 3: Python Script
```bash
python run.py
```

### Option 4: Manual Setup

**Terminal 1 - Backend:**
```bash
cd backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python app.py
```

---

## Detailed Installation

### 1. Prerequisites Check
Ensure you have:
- Python 3.8 or higher
- pip (comes with Python)
- 4GB+ RAM (for model loading)
- 2GB+ disk space (for dependencies)

Check Python version:
```bash
python --version
```

### 2. Create Virtual Environment (Recommended)

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- Flask 2.3.3
- Transformers 4.31.0
- PyTorch 2.0.1
- Sentence-Transformers 2.2.2
- And other required packages

Installation may take 5-10 minutes on first run as models are downloaded.

### 4. Verify Installation

Test the backend:
```bash
cd backend
python -c "from orchestrator.orchestrator import StoryWeaverOrchestrator; print('✓ Backend OK')"
cd ..
```

### 5. Start Services

Use one of the startup scripts mentioned in Quick Start section.

---

## Accessing the Application

Once running:

1. **Open Web UI**: Navigate to http://localhost:3000
2. **API Base URL**: http://localhost:5000

### Testing the API

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Generate Story (via PowerShell):**
```powershell
$body = @{
    prompt = "A young explorer discovers a hidden city"
    style = "adventure"
    length = "medium"
    num_characters = 3
} | ConvertTo-Json

Invoke-WebRequest -Uri http://localhost:5000/generate `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

---

## Troubleshooting

### Issue: "Module not found" error

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or upgrade pip first
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Issue: Port 5000 or 3000 already in use

**Solution:** Edit the port in app.py files:

**Backend** (backend/app.py):
```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)  # Change 5000 to 5001
```

**Frontend** (frontend/app.py):
```python
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=3001)  # Change 3000 to 3001
```

Also update the API URL in frontend/static/app.js:
```javascript
const API_BASE = 'http://localhost:5001';  // Update to new port
```

### Issue: ModuleNotFoundError for backend imports

**Solution:** Ensure you're running from the project root:
```bash
cd path\to\StoryWeaver-AI
python run.py
```

### Issue: Slow startup (models downloading)

**First run only** - The application downloads ML models (~1GB):
- Sentence-Transformers model
- This is cached locally for subsequent runs
- Subsequent startups are much faster

### Issue: Memory error on Windows

If you get memory errors:
1. Close other applications
2. Increase virtual memory (Page File)
3. Or reduce the model used in memory_module.py:
```python
# Change from
self.model = SentenceTransformer("all-MiniLM-L6-v2")
# To lighter model
self.model = SentenceTransformer("all-MiniLM-L6-v2")  # Already lightweight
```

### Issue: CORS errors in browser console

**Solution:** Backend should be running and CORS is configured:
```python
# Already in backend/app.py
from flask_cors import CORS
CORS(app)
```

If still seeing errors, ensure backend is running on port 5000.

### Issue: Frontend not loading at localhost:3000

**Solution:**
1. Check frontend is running: Terminal should show "Running on http://0.0.0.0:3000"
2. Try direct URL: http://127.0.0.1:3000
3. Check firewall isn't blocking port 3000
4. Restart frontend service

---

## Performance Tips

### 1. First-Time Run
- First startup takes longer (model downloading)
- Subsequent runs are faster
- Models are cached in `~/.cache/huggingface/`

### 2. Memory Optimization
- Close other applications
- Use "lite" models if needed
- Consider system RAM

### 3. Story Generation
- Shorter prompts generate faster
- Medium length stories balance speed and detail
- Feedback helps future generations

### 4. Development
- Use development versions for testing
- Check logs for debugging
- API logs available in terminal

---

## File Structure Reference

```
StoryWeaver-AI/
├── backend/
│   ├── agents/              # AI agent implementations
│   ├── memory/              # Memory and embedding module
│   ├── orchestrator/        # Pipeline coordinator
│   └── app.py              # Flask API server
├── frontend/
│   ├── static/             # CSS and JavaScript
│   ├── templates/          # HTML templates
│   └── app.py             # Flask frontend server
├── requirements.txt        # Python dependencies
├── README.md              # Full documentation
├── SETUP.md              # This file
├── start.bat             # Windows batch starter
├── start.ps1             # PowerShell starter
└── run.py               # Python runner script
```

---

## Next Steps

1. **Start the application** using a startup script
2. **Open** http://localhost:3000 in your browser
3. **Enter a story prompt** and click "Generate Story"
4. **View the results** - Story, Characters, Scenes, Music
5. **Provide feedback** using the 5-star rating
6. **Check metrics** to see agent performance

---

## Getting Help

### Common Issues
- Check README.md for API documentation
- Review logs in terminal windows
- Check browser console (F12) for errors

### Resource Links
- Python: https://www.python.org/
- Flask: https://flask.palletsprojects.com/
- PyTorch: https://pytorch.org/
- Transformers: https://huggingface.co/transformers/
- Sentence-Transformers: https://www.sbert.net/

---

## Stopping Services

### Batch or PowerShell Scripts
Close the command windows

### Manual Run
Press `Ctrl+C` in the terminal running services

### Services Stop Gracefully
Wait for "KeyboardInterrupt" message

---

**Happy Storytelling! 🎨✨**
