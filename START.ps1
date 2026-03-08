# Navedas CX Intelligence Hub - PowerShell Launcher
# Right-click and "Run with PowerShell"

Set-Location $PSScriptRoot
Write-Host "Starting Navedas CX Dashboard..." -ForegroundColor Cyan
Write-Host ""

# Check if Python exists
try {
    python --version 2>$null
    Write-Host "Python found. Starting server..." -ForegroundColor Green
    Write-Host ""
    Write-Host "Dashboard will open at: http://localhost:8080" -ForegroundColor Yellow
    Write-Host "Keep this window open while using the dashboard" -ForegroundColor Yellow
    Write-Host ""

    python server.py
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.8+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to close"
}
