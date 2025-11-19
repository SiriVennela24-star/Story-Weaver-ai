# Start StoryWeaver AI - Backend and Frontend
# Windows PowerShell Script

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "   StoryWeaver AI - Multi-Agent Storytelling Engine" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Error: Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import flask; import torch; import transformers; import sentence_transformers" 2>&1 | Out-Null
    Write-Host "Dependencies OK!" -ForegroundColor Green
}
catch {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    python -m pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Error: Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
Write-Host ""

# Start backend
Write-Host "Starting Backend API (Port 5000)..." -ForegroundColor Cyan
Start-Process -WindowStyle Normal -FilePath "python" -ArgumentList "backend/app.py" -PassThru

# Wait for backend to start
Start-Sleep -Seconds 2

# Start frontend
Write-Host "Starting Frontend Server (Port 3000)..." -ForegroundColor Cyan
Start-Process -WindowStyle Normal -FilePath "python" -ArgumentList "frontend/app.py" -PassThru

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "Services started successfully!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Frontend UI:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend API:  http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop services, close the respective windows." -ForegroundColor Yellow
Write-Host ""
