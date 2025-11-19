@echo off
REM Start StoryWeaver AI - Backend and Frontend
REM Windows Batch Script

echo ============================================================
echo   StoryWeaver AI - Multi-Agent Storytelling Engine
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import flask; import torch; import transformers; import sentence_transformers" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Dependencies OK!
echo.
echo Starting services...
echo.

REM Start backend in new window
echo Starting Backend API (Port 5000)...
start "StoryWeaver AI - Backend" cmd /k "cd backend && python app.py"

REM Wait a bit for backend to start
timeout /t 2 /nobreak

REM Start frontend in new window
echo Starting Frontend Server (Port 3000)...
start "StoryWeaver AI - Frontend" cmd /k "cd frontend && python app.py"

echo.
echo ============================================================
echo Services started successfully!
echo ============================================================
echo.
echo URLs:
echo   Frontend UI:  http://localhost:3000
echo   Backend API:  http://localhost:5000
echo.
echo Close either window to stop that service.
echo.
pause
