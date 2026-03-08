@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ========== DIAGNOSTIC CHECK ==========
echo.

echo 1. Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
) else (
    echo OK
)

echo.
echo 2. Checking files...
if exist "server.py" (
    echo OK: server.py found
) else (
    echo ERROR: server.py NOT found
)

if exist "ecommerce_cx_hub_v10 (3).html" (
    echo OK: HTML file found
) else (
    echo ERROR: HTML file NOT found
)

if exist "navedas_cx_1000 (1).xlsx" (
    echo OK: Excel file found
) else (
    echo ERROR: Excel file NOT found
)

echo.
echo 3. Checking required Python packages...
python -c "import pandas; print('OK: pandas installed')" 2>nul || echo ERROR: pandas not installed

echo.
echo 4. Testing server startup (5 second test)...
timeout /t 1 /nobreak >nul
start /b python server.py >server_test.log 2>&1
timeout /t 4 /nobreak
taskkill /F /IM python.exe >nul 2>&1

if exist "server_test.log" (
    echo Server output:
    type server_test.log
    del server_test.log
) else (
    echo Could not capture server output
)

echo.
echo ========== END DIAGNOSTIC ==========
echo.
pause
