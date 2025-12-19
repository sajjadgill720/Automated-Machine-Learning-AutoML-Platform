# Quick Start Script for React Frontend
# This script starts the React development server

Write-Host "Starting AutoML React UI..." -ForegroundColor Cyan
Write-Host ""

# Check if in frontend directory
if (-not (Test-Path "frontend/package.json")) {
    Write-Host "Error: frontend directory not found." -ForegroundColor Red
    Write-Host "Make sure you're in the AutoML_System directory and frontend folder exists." -ForegroundColor Red
    exit 1
}

# Navigate to frontend
Set-Location frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies (first-time setup)..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "npm install failed" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Starting React development server..." -ForegroundColor Green
Write-Host "Frontend will open at: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Make sure the backend is running on http://localhost:8000" -ForegroundColor Magenta
Write-Host ""

npm run dev
