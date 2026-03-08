@echo off
setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo.
echo ===============================================
echo   Navedas CX Intelligence Hub
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Checking files...
if not exist "server.py" (
    echo ERROR: server.py not found!
    pause
    exit /b 1
)

if not exist "ecommerce_cx_hub_v10 (3).html" (
    echo ERROR: HTML file not found!
    pause
    exit /b 1
)

if not exist "navedas_cx_1000 (1).xlsx" (
    echo ERROR: Excel data file not found!
    pause
    exit /b 1
)

echo All files found. Starting server...
echo.

REM Kill any existing Python processes on port 8080
for /f "tokens=5" %%a in ('netstat -aon ^| find "8080" ^| find "LISTENING"') do taskkill /PID %%a /F >nul 2>&1

REM Start the server
echo Starting Python server...
python server.py

if errorlevel 1 (
    echo.
    echo ERROR: Server failed to start
    echo.
    pause
    exit /b 1
)

pause
