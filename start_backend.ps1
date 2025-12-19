# Quick Start Script for AutoML System
# This script starts the FastAPI backend

Write-Host "Starting AutoML Backend..." -ForegroundColor Cyan
Write-Host ""

# Check if in correct directory
if (-not (Test-Path "app.py")) {
    Write-Host "Error: app.py not found. Run this script from the AutoML_System directory." -ForegroundColor Red
    exit 1
}

# Start backend
Write-Host "Starting FastAPI server on http://localhost:8000" -ForegroundColor Green
Write-Host "API Documentation: http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

python app.py
